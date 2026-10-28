"""Bind editorial work to final documents and independently readable source records."""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

from .career_coverage import _corrected_roles, _cv_entries, _scoped_roles, validate_career_coverage
from .evidence import _source
from .preparation_context import PreparationContext, resolve_preparation_context


def review_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def document_digest(text: str) -> str:
    return 'sha256:' + hashlib.sha256((text.strip() + '\n').encode()).hexdigest()


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} requires nonempty text')
    return value.strip()


def validate_role_inventory(audit: Mapping, markdown: str, root: Path, *, reference_date: date | None = None, context: PreparationContext | None = None) -> list:
    rows = audit.get('role_coverage')
    if not isinstance(rows, list) or not rows:
        raise ValueError('cv_audit.role_coverage requires a complete source-role inventory')
    context = resolve_preparation_context(root, context)
    source_path = context.career_source_path
    all_roles = _corrected_roles(source_path, context=context)
    permitted = _scoped_roles(all_roles, source_path, reference_date, context=context)
    validate_career_coverage(markdown, source_path, reference_date=reference_date, context=context)
    editor = audit['editorial_review']
    author = _text(editor.get('author'), 'CV editorial author')
    if editor.get('mode') == 'independent' and author == editor['reviewer']:
        raise ValueError('independent CV editor must differ from the author')
    headings = {title for title, _ in _cv_entries(markdown)}
    seen = set()
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError('role_coverage entries must be mappings')
        employer = _text(row.get('employer'), 'role_coverage employer')
        if employer in seen or employer not in all_roles:
            raise ValueError('role_coverage has duplicate or unknown source employers')
        seen.add(employer)
        expected = 'include' if employer in permitted else 'exclude'
        if row.get('decision') != expected:
            raise ValueError(f'role_coverage decision violates the career policy for {employer}')
        period = all_roles[employer]
        expected_period = dict(start=list(period[0]), end=list(period[1]) if period[1] else None)
        if row.get('source_period') != expected_period:
            raise ValueError(f'role_coverage has stale source dates for {employer}')
        _text(row.get('reason'), 'role_coverage reason')
        if row.get('reviewer') != editor['reviewer']:
            raise ValueError('role_coverage exclusion/inclusion must be reviewed by the CV editor')
        sources = row.get('sources')
        if not isinstance(sources, list) or not sources:
            raise ValueError('role_coverage requires exact candidate sources')
        quotes = '\n'.join(_source(root, item, context=context) for item in sources if isinstance(item, Mapping))
        if len([item for item in sources if isinstance(item, Mapping)]) != len(sources):
            raise ValueError('role_coverage sources must be mappings')
        aliases = context.employer_aliases.get(employer.casefold(), (employer,))
        if not any(alias.casefold() in quotes.casefold() for alias in aliases):
            raise ValueError('role_coverage source does not support the employer')
        if expected == 'include':
            heading = _text(row.get('heading'), 'role_coverage heading')
            if heading not in headings or not any(alias.casefold() in heading.casefold() for alias in aliases):
                raise ValueError('role_coverage included role is absent from final CV headings')
        elif row.get('heading'):
            raise ValueError('role_coverage excluded employer cannot have a CV heading')
    if seen != set(all_roles):
        raise ValueError('role_coverage omits source employers: ' + ', '.join(sorted(set(all_roles) - seen)))
    if {row['heading'] for row in rows if row['decision'] == 'include'} != headings:
        raise ValueError('role_coverage must account for every final CV heading')
    return rows


def letter_basis(quality: Mapping) -> dict:
    letter = quality['cover_letter']
    return dict(evidence_stories=letter['evidence_stories'], company_motivation=letter['company_motivation'],
                requirements=quality['requirements'], channel=letter.get('channel', 'attachment'),
                application_route=letter.get('application_route'))


def validate_letter_review(quality: Mapping, markdown: str, draft: Path, root: Path, ledger: Mapping, *, context: PreparationContext | None = None) -> dict:
    letter = quality['cover_letter']
    review = letter.get('editorial_review')
    if not isinstance(review, Mapping):
        raise ValueError('letter editorial_review is required for the exact final text')
    _text(review.get('reviewer'), 'letter reviewer')
    if review.get('document_sha256') != document_digest(markdown):
        raise ValueError('letter editorial review is stale for the final text')
    if review.get('basis_sha256') != review_digest(letter_basis(quality)):
        raise ValueError('letter editorial review is stale for priorities, evidence or company source')
    mappings = review.get('priority_mapping')
    if not isinstance(mappings, list) or len(mappings) != 2:
        raise ValueError('letter review needs two complementary priority mappings')
    rows = {row['requirement']: row for row in quality['requirements']}
    priorities = {name for name, row in rows.items() if row['importance'] in {'critical', 'high'}
                  and row['match'] in {'strong', 'partial'} and row.get('evidence_ids')}
    points = set()
    for mapping, strand in zip(mappings, letter['evidence_stories']):
        if not isinstance(mapping, Mapping):
            raise ValueError('letter priority mapping must be a mapping')
        requirement = mapping.get('requirement')
        if requirement not in rows or requirement != strand['requirement']:
            raise ValueError('letter priority mapping must name a real requirement and its evidence strand')
        if priorities and requirement not in priorities:
            raise ValueError('letter priority mapping must address critical/high vacancy priorities')
        ids = mapping.get('evidence_ids')
        if ids != strand['evidence_ids'] or not set(ids).issubset(set(rows[requirement].get('evidence_ids', []))):
            raise ValueError('letter priority evidence must match its requirement and strand')
        point = _text(mapping.get('point'), 'letter complementary point').casefold()
        if point in points:
            raise ValueError('letter evidence strands must make distinct points')
        points.add(point)
        _text(mapping.get('why_priority'), 'letter priority rationale')
        quote = _text(mapping.get('letter_quote'), 'letter priority quote')
        if quote not in markdown or not any(quote in claim['text'] and set(ids).issubset(claim['evidence_ids'])
                for claim in ledger['claims'] if claim['document'] in {'cover-letter', 'cover_letter_markdown'}):
            raise ValueError('letter priority quote must anchor a final letter claim')
    _text(review.get('distinctness'), 'letter distinctness review')
    _text(review.get('channel_fit'), 'letter channel fit review')
    examples = review.get('narrated_examples')
    maximum = 1 if letter.get('channel') == 'email' else 2
    if not isinstance(examples, list) or len(examples) > maximum:
        raise ValueError('letter narrated examples exceed the channel limit')
    example_quotes = set()
    for example in examples:
        if not isinstance(example, Mapping):
            raise ValueError('letter narrated example must be a mapping')
        quote = _text(example.get('letter_quote'), 'letter narrated example')
        if quote not in markdown or quote in example_quotes:
            raise ValueError('letter narrated examples must be distinct final-text excerpts')
        example_quotes.add(quote)
        _text(example.get('adds_value'), 'letter example reader value')
    company = letter['company_motivation']
    snapshot = company.get('snapshot')
    if not isinstance(snapshot, Mapping):
        raise ValueError('letter company claim requires a captured primary-source snapshot')
    path_value = _text(snapshot.get('path'), 'company snapshot path')
    path = (draft / path_value).resolve()
    if Path(path_value).is_absolute() or not path.is_relative_to(draft.resolve()):
        raise ValueError('company snapshot escapes the draft')
    raw = path.read_bytes()
    quote = _text(snapshot.get('quote'), 'company source quote')
    if snapshot.get('sha256') != hashlib.sha256(raw).hexdigest() or quote not in raw.decode('utf-8-sig'):
        raise ValueError('letter company snapshot is stale or its quote is absent')
    date.fromisoformat(_text(snapshot.get('checked_on'), 'company source checked_on'))
    if snapshot.get('url') != company['source_url'] or company['fact'] not in quote:
        raise ValueError('letter company fact must be supported by its cited snapshot')
    company_quote = _text(review.get('company_claim'), 'final letter company claim')
    if company_quote not in markdown:
        raise ValueError('letter company claim must be present in the final text')
    _text(review.get('company_grounding'), 'letter company source-to-final-text review')
    validate_voice_review(review, root, context=context)
    validate_letter_delivery(letter, review, markdown, draft=draft)
    return {**review, 'company_source': dict(snapshot), 'company_fact': company['fact'],
            'application_route': dict(letter['application_route'])}


def _letter_paragraphs(markdown: str) -> list[str]:
    return [paragraph.strip() for paragraph in re.split(r'\n\s*\n', markdown.strip()) if paragraph.strip()]


def validate_letter_council(review: Mapping, markdown: str, draft: Path | None = None) -> None:
    """Validate independent review receipts and their binding to the final text."""
    author = _text(review.get('author'), 'letter author').casefold()
    council = review.get('council')
    if not isinstance(council, Mapping) or council.get('schema_version') != 1 or council.get('mode') != 'quick':
        raise ValueError('letter council requires schema_version 1 and quick mode')
    reviews = council.get('reviews')
    if not isinstance(reviews, list) or len(reviews) != 3:
        raise ValueError('letter council requires exactly three independent reviews')
    digest = document_digest(markdown)
    paragraphs = _letter_paragraphs(markdown)
    names = set()
    ratings = []
    expected_rules = {'contribution_first', 'necessary_evidence', 'no_cv_replay', 'natural_voice'}
    for item in reviews:
        if not isinstance(item, Mapping):
            raise ValueError('letter council reviews must be mappings')
        name = _text(item.get('reviewer'), 'letter council reviewer').casefold()
        if name == author or name in names:
            raise ValueError('letter council reviewers must be distinct and independent of the author')
        names.add(name)
        if item.get('document_sha256') != digest:
            raise ValueError('letter council review is stale for the final text')
        if item.get('verdict') != 'approve' or item.get('unresolved_objections') != []:
            raise ValueError('letter council requires approval and no unresolved objections from every reviewer')
        rating = item.get('naturalness')
        _validate_naturalness(rating, digest)
        if rating['reviewer'].strip().casefold() != name:
            raise ValueError('letter council naturalness reviewer must match its independent reviewer')
        ratings.append(rating)
        rules = item.get('rule_checks')
        if not isinstance(rules, Mapping) or set(rules) != expected_rules:
            raise ValueError('letter council requires all four rule checks')
        for rule in rules.values():
            if not isinstance(rule, Mapping) or rule.get('pass') is not True:
                raise ValueError('letter council rule checks must pass')
            if _text(rule.get('quote'), 'letter council rule quote') not in markdown:
                raise ValueError('letter council rule quote must appear in the exact final text')
            _text(rule.get('reason'), 'letter council rule rationale')
        paragraph_reviews = item.get('paragraph_reviews')
        if not isinstance(paragraph_reviews, list) or len(paragraph_reviews) != len(paragraphs):
            raise ValueError('letter council paragraph reviews must cover every final paragraph')
        for paragraph, row in zip(paragraphs, paragraph_reviews):
            if not isinstance(row, Mapping) or row.get('quote') != paragraph:
                raise ValueError('letter council paragraph review must quote each exact final paragraph in order')
            _text(row.get('purpose'), 'letter paragraph purpose')
            _text(row.get('reason'), 'letter paragraph rationale')
            if row.get('decision') != 'keep':
                raise ValueError('approved final letter requires keep decisions for every paragraph')
    if _text(review.get('reviewer'), 'letter editorial reviewer').casefold() not in names:
        raise ValueError('letter editorial reviewer must be one of the independent council reviewers')
    minimum = min(rating['score'] for rating in ratings)
    if review.get('naturalness') not in [rating for rating in ratings if rating['score'] == minimum]:
        raise ValueError('letter editorial naturalness must copy the lowest independent council rating')
    peer = council.get('peer_review')
    if (not isinstance(peer, Mapping)
            or _text(peer.get('reviewer'), 'letter peer reviewer').casefold() not in names
            or peer['reviewer'].strip().casefold() == author):
        raise ValueError('letter peer review requires one independent council reviewer')
    if peer.get('reviews_sha256') != review_digest(reviews):
        raise ValueError('letter peer review is stale for the independent review set')
    if peer.get('document_sha256') != digest:
        raise ValueError('letter peer review is stale for the final text')
    if peer.get('verdict') != 'approve' or peer.get('unresolved_objections') != []:
        raise ValueError('letter peer review requires approval with no unresolved objections')
    _text(peer.get('notes'), 'letter peer review notes')
    _text(peer.get('weakest_point'), 'letter peer review weakest point')
    snapshot = peer.get('snapshot')
    if not isinstance(snapshot, Mapping):
        raise ValueError('letter peer review requires an anonymized snapshot')
    path_value = _text(snapshot.get('path'), 'letter peer snapshot path')
    relative = Path(path_value)
    if relative.is_absolute() or not relative.parts or relative.parts[0] != 'parts' or '..' in relative.parts:
        raise ValueError('letter peer snapshot must be inside draft parts')
    if draft is not None:
        path = (draft / relative).resolve()
        if not path.is_relative_to((draft / 'parts').resolve()):
            raise ValueError('letter peer snapshot escapes draft parts')
        raw = path.read_bytes()
        if not raw.strip() or snapshot.get('sha256') != hashlib.sha256(raw).hexdigest():
            raise ValueError('letter peer snapshot is empty or altered')


def validate_letter_delivery(letter: Mapping, review: Mapping, markdown: str, *, draft: Path | None = None) -> None:
    """Check recorded editorial work, not machine-infer authorship or style scores."""
    route = letter.get('application_route')
    if not isinstance(route, Mapping):
        raise ValueError('letter application_route must explain why a letter is required')
    channel = route.get('channel')
    if channel == 'form':
        if route.get('letter_required') is not True or letter.get('channel', 'attachment') != 'attachment':
            raise ValueError('form letters require a mandatory apply-form field')
    elif channel == 'email':
        if route.get('email_only') is not True or letter.get('channel') != 'email':
            raise ValueError('email letters require an email-only application route')
        language = _text(route.get('company_language'), 'company language')
        _text(route.get('language_evidence'), 'company language evidence')
        if language.casefold() != review['voice']['language'].casefold():
            raise ValueError('application email must use the company language')
    else:
        raise ValueError('letter application_route channel must be form or email')
    url = _text(route.get('source_url'), 'application route source URL')
    if not url.startswith(('https://', 'http://')):
        raise ValueError('application route requires an HTTP(S) source URL')
    _text(route.get('evidence'), 'application route evidence')
    date.fromisoformat(_text(route.get('checked_on'), 'application route checked_on'))
    for name, skill in (('humanizer', 'humanizer'), ('ai_detection', 'ai-detector')):
        receipt = review.get(name)
        if not isinstance(receipt, Mapping) or receipt.get('skill') != skill:
            raise ValueError(f'letter requires {name} skill receipt')
        _text(receipt.get('version'), f'{name} version')
        _text(receipt.get('reviewer'), f'{name} reviewer')
        _text(receipt.get('notes'), f'{name} findings and keep decisions')
        if receipt.get('document_sha256') != document_digest(markdown):
            raise ValueError(f'{name} receipt is stale for the final text')
    detector = review['ai_detection']
    if detector.get('mode') not in {'local', 'external'}:
        raise ValueError('ai_detection mode must be local or external')
    if detector['mode'] == 'external':
        _text(detector.get('session_url'), 'external detector session URL')
        _text(detector.get('literal_feedback'), 'external detector literal feedback')
    rating = review.get('naturalness')
    _validate_naturalness(rating, document_digest(markdown))
    validate_letter_council(review, markdown, draft)


def _validate_naturalness(rating: Any, digest: str) -> None:
    if not isinstance(rating, Mapping) or rating.get('rubric') != 'naturalness-v1':
        raise ValueError('letter requires naturalness-v1 editorial rating')
    if rating.get('document_sha256') != digest:
        raise ValueError('naturalness rating is stale for the final text')
    _text(rating.get('reviewer'), 'naturalness reviewer')
    dimensions = rating.get('dimensions')
    expected = {'voice', 'specificity', 'flow', 'restraint'}
    if not isinstance(dimensions, Mapping) or set(dimensions) != expected:
        raise ValueError('naturalness rating requires all four rubric dimensions')
    for item in dimensions.values():
        if not isinstance(item, Mapping) or type(item.get('score')) is not int or not 0 <= item['score'] <= 25:
            raise ValueError('naturalness dimension scores must be integers from 0 to 25')
        _text(item.get('reason'), 'naturalness dimension rationale')
    score = sum(item['score'] for item in dimensions.values())
    if type(rating.get('score')) is not int or rating['score'] != score or score < 90:
        raise ValueError('letter naturalness must total at least 90/100; revise before publication')


def validate_voice_review(review: Mapping, root: Path, *, context: PreparationContext | None = None) -> None:
    context = resolve_preparation_context(root, context)
    if context.project_root != root.resolve():
        raise ValueError('letter voice context belongs to another project')
    configured = context.voice_sources
    voice = review.get('voice')
    if not isinstance(voice, Mapping):
        raise ValueError('letter review requires final-language voice inspection')
    _text(voice.get('language'), 'letter language')
    _text(voice.get('notes'), 'letter final-language voice notes')
    rules = voice.get('rules')
    if not isinstance(rules, list) or len(rules) != len(configured):
        raise ValueError('letter review must bind every configured voice source')
    for rule, configured_path in zip(rules, configured):
        if not isinstance(rule, Mapping):
            raise ValueError('letter voice source must be a mapping')
        path = Path(configured_path)
        if not path.is_absolute():
            path = root / path
        if rule.get('path') != configured_path or rule.get('sha256') != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError('letter voice review is stale or uses another rules source')


def validate_application_review(quality: Mapping, package: Mapping, draft: Path, root: Path, ledger: Mapping, *, reference_date: date | None = None, context: PreparationContext | None = None) -> dict:
    receipt = {}
    if 'cv_markdown' in package:
        receipt['role_coverage'] = validate_role_inventory(quality['cv_audit'], package['cv_markdown'], root, reference_date=reference_date, context=context)
    if 'cover_letter_markdown' in package:
        receipt['letter_review'] = validate_letter_review(quality, package['cover_letter_markdown'], draft, root, ledger, context=context)
    if ledger.get('schema_version') != 2:
        raise ValueError('quality v3 requires claims ledger schema_version 2 with measurement context')
    return receipt
