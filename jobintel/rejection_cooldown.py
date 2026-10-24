"""Read-only company exclusion for six calendar months after employer rejection."""
from __future__ import annotations

import calendar
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from . import storage_bridge as op
from .prefilter import CompanyRetryRule, load_company_retry_rules, _company_retry_rejection


def six_months_after(day: date) -> date:
    month = day.month + 5
    year, month = day.year + month // 12, month % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def rejection_day(value) -> date:
    text = str(value).strip()
    if len(text) == 10:
        return date.fromisoformat(text)
    moment = datetime.fromisoformat(text.replace('Z', '+00:00'))
    if moment.tzinfo is not None:
        moment = moment.astimezone(ZoneInfo('Europe/Rome'))
    return moment.date()


def load_retry_rules(registry_root: Path, *, store=None) -> tuple[CompanyRetryRule, ...]:
    """Include archived vacancies and the retained manual audit, without caching dates."""
    registry_root = Path(registry_root).resolve()
    rules = list(load_company_retry_rules(registry_root.parent / 'config/application-profile.yaml'))
    store = store if store is not None else op.get_store(registry_root)
    if store is None:
        metadata = [yaml.safe_load(op.read_text(path)) for path in op.metadata_paths(registry_root / 'jobs')]
        audit_path = registry_root / 'manual-status-log.yaml'
        audit = yaml.safe_load(op.read_text(audit_path)) if op.exists(audit_path) else {}
    else:
        metadata = [doc.get('meta', {}) for doc in store.list_vacancies(scope='jobs', include_archived=True)]
        audit = (store.get('operational_logs', 'manual-status-log.yaml') or {}).get('payload', {})
    events = []
    for meta in metadata:
        for event in meta.get('status_history', []):
            if event.get('status') == 'rejected':
                events.append((meta.get('company'), event.get('changed_at')))
    for event in (audit or {}).get('events', []):
        if event.get('to_status') == 'rejected':
            events.append((event.get('company'), event.get('changed_at')))
    latest = {}
    for company, timestamp in events:
        if not company or not timestamp:
            raise ValueError('employer rejection requires company and rejection date for cooldown')
        day = rejection_day(timestamp)
        latest[str(company)] = max(day, latest.get(str(company), day))
    for company, rejected_on in latest.items():
        aliases = tuple(alias for rule in rules if rule.matches(company)
                        for alias in (rule.company, *rule.aliases))
        rules.append(CompanyRetryRule(company, six_months_after(rejected_on),
                                     f'Employer rejection on {rejected_on.isoformat()}; six-calendar-month cooldown.', aliases))
    return tuple(rules)


def retry_reason(company: str, rules: tuple[CompanyRetryRule, ...], *, today: date | None = None) -> str | None:
    today = today or datetime.now(ZoneInfo('Europe/Rome')).date()
    # The latest applicable deadline wins, including longer explicit company rules.
    active = tuple(sorted(rules, key=lambda rule: rule.allow_after, reverse=True))
    rejection = _company_retry_rejection(company, active, today)
    return rejection.reason if rejection else None


def require_retry_eligible(registry_root: Path, company: str, *, today: date | None = None) -> None:
    reason = retry_reason(company, load_retry_rules(registry_root), today=today)
    if reason:
        raise ValueError(reason)
