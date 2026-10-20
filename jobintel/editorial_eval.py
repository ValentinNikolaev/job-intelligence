"""Evaluate Codex-produced editorial decisions against an anonymized fixed corpus."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml

from .application_review import review_digest
from .preparation_context import load_preparation_context


POLICY_FILES = ('config/cv-editorial-knowledge.yaml', 'prompts/vacancy-application.md',
                'config/matching-policy.yaml', 'prompts/vacancy-match.md', 'docs/application-quality.md',
                'docs/application-review-contract.md', '.agents/skills/job-intelligence-workflow/references/prepare.md',
                'prompts/job-intelligence-workflow.md', 'prompts/cv-editorial-rebuild-six.md',
                '.agents/skills/job-intelligence-workflow/SKILL.md', 'AGENTS.md',
                'prompts/scheduled-prepare.md',
                '.agents/skills/manual-vacancy-application/SKILL.md',
                'skills/manual-vacancy-application/SKILL.md')
CORPUS_PATH = 'tests/fixtures/editorial-corpus.yaml'


def _load(root: Path):
    corpus = yaml.safe_load((root / CORPUS_PATH).read_text(encoding='utf-8'))
    if corpus.get('schema_version') != 1 or not isinstance(corpus.get('cases'), list) or not corpus['cases']:
        raise ValueError('editorial corpus requires schema 1 and nonempty cases')
    ids = [case['id'] for case in corpus['cases']]
    if len(ids) != len(set(ids)):
        raise ValueError('editorial corpus has duplicate cases')
    policies = {path: (root / path).read_text(encoding='utf-8') for path in POLICY_FILES}
    context = load_preparation_context(root)
    policies['config/application-profile.yaml#preparation'] = json.dumps({
        'preparation_context_version': context.version,
        'career_scope': context.preparation['career_scope'],
    }, sort_keys=True, ensure_ascii=False)
    return corpus, policies


def export_pack(root: Path) -> dict:
    corpus, policies = _load(root)
    return dict(schema_version=1, corpus_sha256=review_digest(corpus), policy_sha256=review_digest(policies),
        scope=corpus['note'],
        policies=policies, cases=[{key: value for key, value in case.items() if key != 'expected'} for case in corpus['cases']],
        decisions=('keep', 'rewrite', 'omit'))


def evaluate_decisions(root: Path, decisions: dict) -> dict:
    corpus, policies = _load(root)
    if decisions.get('schema_version') != 1 or not str(decisions.get('reviewer', '')).strip():
        raise ValueError('editorial decisions require schema 1 and actual reviewer identity')
    if decisions.get('corpus_sha256') != review_digest(corpus) or decisions.get('policy_sha256') != review_digest(policies):
        raise ValueError('editorial decisions are stale for the corpus or policy')
    rows = decisions.get('decisions')
    if not isinstance(rows, list) or len(rows) != len(corpus['cases']):
        raise ValueError('editorial decisions must cover every case exactly once')
    by_id = {}
    for row in rows:
        if not isinstance(row, dict) or row.get('id') in by_id:
            raise ValueError('editorial decisions have duplicate or malformed cases')
        by_id[row['id']] = row
    if set(by_id) != {case['id'] for case in corpus['cases']}:
        raise ValueError('editorial decisions have missing or unknown cases')
    failures = []
    for case in corpus['cases']:
        row = by_id[case['id']]
        if row.get('decision') not in {'keep', 'rewrite', 'omit'} or not isinstance(row.get('reason'), str) or len(row['reason'].strip()) < 20:
            raise ValueError('editorial decision requires a disposition and substantive reason')
        quotes = row.get('source_quotes')
        if not isinstance(quotes, list) or not quotes or any(not isinstance(q, str) or not q.strip() or q not in case['source'] for q in quotes):
            raise ValueError('editorial decision must cite exact input-source excerpts')
        codes = row.get('reason_codes')
        if not isinstance(codes, list) or not all(isinstance(code, str) for code in codes):
            raise ValueError('editorial reason_codes must be a list of text codes')
        expected = case['expected']
        if row['decision'] != expected['decision'] or not set(expected['reason_codes']).issubset(codes):
            failures.append(dict(id=case['id'], expected=expected, actual=row, rationale=expected['rationale']))
    return dict(schema_version=1, ok=not failures, reviewer=decisions['reviewer'], cases=len(rows),
        passed=len(rows) - len(failures), failures=failures, corpus_sha256=review_digest(corpus),
        policy_sha256=review_digest(policies), decisions_sha256=review_digest(decisions),
        limitation='Checks decisions against curated expectations; it does not prove hiring effectiveness or general factual truth.')


def main(argv=None, *, root: Path) -> int:
    parser = argparse.ArgumentParser(description='Export blind editorial cases and evaluate completed Codex decisions. No model calls.')
    commands = parser.add_subparsers(dest='action', required=True)
    export = commands.add_parser('export', help='Export cases without answer keys')
    export.add_argument('--output', type=Path, required=True)
    evaluate = commands.add_parser('evaluate', help='Fail on missing, stale or incorrect decisions')
    evaluate.add_argument('--input', type=Path, required=True)
    evaluate.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        result = export_pack(root) if args.action == 'export' else evaluate_decisions(root, json.loads((root / args.input).read_text(encoding='utf-8-sig')))
        if args.output:
            path = (root / args.output).resolve()
            if not path.is_relative_to((root / '.codex-work').resolve()) or path.suffix != '.json':
                raise ValueError('editorial output must be JSON under .codex-work/')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('ok', True) else 1
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
        print(f'Editorial evaluation error: {exc}')
        return 1
