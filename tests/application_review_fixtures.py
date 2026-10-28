"""Synthetic, source-backed review fixtures; never candidate application material."""
import hashlib
import re
from pathlib import Path

import yaml

from jobintel.preparation_context import load_preparation_context

from jobintel.application_review import document_digest, letter_basis, review_digest


def add_letter_review(root, draft, quality, package):
    letter = package['cover_letter_markdown'].strip() + '\n'
    fact = 'Example builds billing software.'
    letter = letter.replace('Dear Hiring Team,', 'Dear Hiring Team,\n\n' + fact, 1)
    package['cover_letter_markdown'] = letter
    quality['schema_version'] = 3
    quality['final_review']['document_sha256']['cover-letter'] = document_digest(letter)
    quality['requirements'][0]['requirement'] = 'Backend'
    for strand in quality['cover_letter']['evidence_stories']:
        strand['requirement'] = 'Backend'
    ledger_path = draft / 'claims.yaml'
    ledger = yaml.safe_load(ledger_path.read_text(encoding='utf-8'))
    ledger['schema_version'] = 2
    ledger_path.write_text(yaml.safe_dump(ledger), encoding='utf-8')
    parts = draft / 'parts'
    parts.mkdir(exist_ok=True)
    snapshot = parts / 'company-source.txt'
    snapshot.write_text(fact + '\n', encoding='utf-8')
    quality['cover_letter']['company_motivation'] = dict(fact=fact, source_url='https://example.test/company',
        snapshot=dict(path='parts/company-source.txt', url='https://example.test/company', quote=fact,
            sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(), checked_on='2026-10-15'))
    rules = []
    config = root / 'config'
    config.mkdir(exist_ok=True)
    for name in ('social-voice.md', 'employer-letter-flow.md'):
        path = config / name
        path.write_text('Use calm, concrete language and verify the final text.\n', encoding='utf-8')
        rules.append(dict(path='config/' + name, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (config / 'application-review.yaml').write_text(yaml.safe_dump(dict(schema_version=1, voice_sources=[r['path'] for r in rules])), encoding='utf-8')
    quality['preparation_context_version'] = load_preparation_context(root).version
    quote = ledger['claims'][0]['text']
    review = dict(author='fixture-letter-author', reviewer='fixture-reviewer-a', document_sha256=document_digest(letter),
        basis_sha256=review_digest(letter_basis(quality)),
        priority_mapping=[dict(requirement='Backend', evidence_ids=['delivery'], letter_quote=quote,
            point=point, why_priority='This is a stated high-priority vacancy requirement.') for point in ('Backend delivery', 'Operational reliability')],
        distinctness='The technical delivery and operational reliability points complement each other in one example.',
        channel_fit='The attachment explains relevant fit without adding a second case study.',
        narrated_examples=[dict(letter_quote=quote, adds_value='One example addresses both relevant abilities.')],
        company_claim=fact, company_grounding='The final company sentence states the same billing-software fact as the captured primary source.',
        voice=dict(language='English', notes='Reviewed the exact final English wording and practical closing.', rules=rules))
    quality['cover_letter']['editorial_review'] = review
    quality['cover_letter']['application_route'] = dict(channel='form', letter_required=True,
        source_url='https://example.test/apply', checked_on='2026-10-27', evidence='Cover Letter (required)')
    review['basis_sha256'] = review_digest(letter_basis(quality))
    for key, skill in [('humanizer', 'humanizer'), ('ai_detection', 'ai-detector')]:
        review[key] = dict(skill=skill, version='fixture', reviewer='fixture-editor',
            document_sha256=document_digest(letter), notes='Synthetic receipt: retain the concrete example and direct closing.')
    review['ai_detection']['mode'] = 'local'
    paragraphs = [paragraph.strip() for paragraph in re.split(r'\n\s*\n', letter.strip())]
    reviews = []
    for name in ('fixture-reviewer-a', 'fixture-reviewer-b', 'fixture-reviewer-c'):
        naturalness = dict(rubric='naturalness-v1', reviewer=name,
            document_sha256=document_digest(letter), score=92,
            dimensions={key: dict(score=23, reason='Synthetic fixture rationale for this dimension.')
                for key in ('voice', 'specificity', 'flow', 'restraint')})
        reviews.append(dict(reviewer=name, document_sha256=document_digest(letter),
            verdict='approve', unresolved_objections=[], naturalness=naturalness,
            rule_checks={key: dict(**{'pass': True}, quote=fact,
                reason='The final sentence supplies a concrete company fact in this fixture.')
                for key in ('contribution_first', 'necessary_evidence', 'no_cv_replay', 'natural_voice')},
            paragraph_reviews=[dict(quote=paragraph, purpose='Contributes to the complete fixture letter.',
                decision='keep', reason='The paragraph has a distinct place in this fixture.')
                for paragraph in paragraphs]))
    peer_snapshot = parts / 'letter-review-snapshot.txt'
    peer_snapshot.write_text('Anonymized synthetic review: the example and company fact support the letter.\n', encoding='utf-8')
    review['council'] = dict(schema_version=1, mode='quick', reviews=reviews,
        peer_review=dict(reviewer='fixture-reviewer-b', document_sha256=document_digest(letter),
            reviews_sha256=review_digest(reviews),
            verdict='approve', notes='The exact final fixture letter is coherent.',
            weakest_point='The synthetic company motivation is short.', unresolved_objections=[],
            snapshot=dict(path='parts/letter-review-snapshot.txt',
                sha256=hashlib.sha256(peer_snapshot.read_bytes()).hexdigest())))
    review['naturalness'] = reviews[0]['naturalness'].copy()
    (draft / 'cover-letter.md').write_text(letter, encoding='utf-8')
    (draft / 'quality.yaml').write_text(yaml.safe_dump(quality), encoding='utf-8')
    return review
