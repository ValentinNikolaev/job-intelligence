"""Synthetic, source-backed review fixtures; never candidate application material."""
import hashlib
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
    review = dict(reviewer='letter-editor', document_sha256=document_digest(letter),
        basis_sha256=review_digest(letter_basis(quality)),
        priority_mapping=[dict(requirement='Backend', evidence_ids=['delivery'], letter_quote=quote,
            point=point, why_priority='This is a stated high-priority vacancy requirement.') for point in ('Backend delivery', 'Operational reliability')],
        distinctness='The technical delivery and operational reliability points complement each other in one example.',
        channel_fit='The attachment explains relevant fit without adding a second case study.',
        narrated_examples=[dict(letter_quote=quote, adds_value='One example addresses both relevant abilities.')],
        company_claim=fact, company_grounding='The final company sentence states the same billing-software fact as the captured primary source.',
        voice=dict(language='English', notes='Reviewed the exact final English wording and practical closing.', rules=rules))
    quality['cover_letter']['editorial_review'] = review
    (draft / 'cover-letter.md').write_text(letter, encoding='utf-8')
    (draft / 'quality.yaml').write_text(yaml.safe_dump(quality), encoding='utf-8')
    return review
