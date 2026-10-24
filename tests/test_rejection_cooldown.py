from datetime import date
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import yaml

from jobintel.rejection_cooldown import load_retry_rules, retry_reason, require_retry_eligible, six_months_after
from jobintel.prefilter import CompanyRetryRule, prefilter_job
from tests.test_prefilter import make_job


class RejectionCooldownTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = self.root / 'registry'
        self.store = Mock()
        self.store.list_vacancies.return_value = []
        self.store.get.return_value = None

    def rejection(self, company='Cubbit S.r.l.', day='2026-09-25T21:11:20Z'):
        self.store.list_vacancies.return_value = [dict(archived=True, meta=dict(
            company=company, status='rejected', status_history=[dict(status='rejected', changed_at=day)]))]
        return load_retry_rules(self.registry, store=self.store)

    def test_calendar_boundary_and_month_end(self):
        self.assertEqual(date(2027, 3, 25), six_months_after(date(2026, 9, 25)))
        self.assertEqual(date(2027, 2, 28), six_months_after(date(2026, 8, 31)))
        self.assertEqual(date(2024, 2, 29), six_months_after(date(2023, 8, 31)))
        rules = self.rejection()
        self.assertIsNotNone(retry_reason('Cubbit', rules, today=date(2027, 3, 24)))
        self.assertIsNone(retry_reason('Cubbit', rules, today=date(2027, 3, 25)))

    def test_archived_rejection_blocks_company_variants_and_new_job(self):
        rules = self.rejection()
        self.store.list_vacancies.assert_called_once_with(scope='jobs', include_archived=True)
        for company in ['Cubbit', 'CUBBIT S.R.L.', 'Cubbit Srl']:
            self.assertIsNotNone(retry_reason(company, rules, today=date(2026, 10, 24)))
        self.assertIsNone(retry_reason('Another Cubbit', rules, today=date(2026, 10, 24)))
        result = prefilter_job(make_job(company='Cubbit'), company_retry_rules=rules)
        self.assertEqual('company_retry_block', result.category)

    def test_manual_audit_retains_exclusion_after_vacancy_removal(self):
        self.store.get.return_value = {'payload': {'events': [dict(
            company='Removed Employer', to_status='rejected', changed_at='2026-09-25T12:00:00Z')]}}
        rules = load_retry_rules(self.registry, store=self.store)
        self.assertIn('2027-03-25', retry_reason('Removed Employer', rules, today=date(2026, 10, 24)))

    def test_latest_rejection_and_longer_manual_rule_win(self):
        rules = self.rejection()
        self.store.get.return_value = {'payload': {'events': [dict(
            company='Cubbit', to_status='rejected', changed_at='2026-10-20T12:00:00Z')]}}
        rules = load_retry_rules(self.registry, store=self.store)
        self.assertIn('2027-04-20', retry_reason('Cubbit', rules, today=date(2027, 3, 25)))
        rules += (CompanyRetryRule('Cubbit', date(2027, 6, 1), 'Explicit longer delay'),)
        self.assertIn('2027-06-01', retry_reason('Cubbit', rules, today=date(2027, 3, 25)))

    def test_not_match_and_withdrawal_are_not_employer_rejections(self):
        self.store.list_vacancies.return_value = [dict(meta=dict(company='Cubbit',
            status_history=[dict(status='withdrawn', changed_at='2026-10-01T12:00:00Z')],
            match=dict(hard_rejection=True)))]
        self.assertEqual((), load_retry_rules(self.registry, store=self.store))

    def test_rome_calendar_date_and_invalid_date_fail_closed(self):
        rules = self.rejection(day='2026-09-25T23:00:00Z')
        self.assertIn('2027-03-26', retry_reason('Cubbit', rules, today=date(2027, 3, 25)))
        with self.assertRaises(ValueError):
            self.rejection(day='not-a-date')

    def test_explicit_preparation_guard_uses_canonical_history(self):
        rules = self.rejection()
        with patch('jobintel.rejection_cooldown.load_retry_rules', return_value=rules):
            with self.assertRaisesRegex(ValueError, '2027-03-25'):
                require_retry_eligible(self.registry, 'Cubbit', today=date(2026, 10, 24))
            require_retry_eligible(self.registry, 'Cubbit', today=date(2027, 3, 25))

    def test_yaml_backend_and_configured_aliases(self):
        path = self.registry / 'jobs/old/meta.yaml'
        path.parent.mkdir(parents=True)
        path.write_text(yaml.safe_dump(dict(company='Alias Employer', status_history=[dict(
            status='rejected', changed_at='2026-09-25T12:00:00Z')])), encoding='utf-8')
        profile = self.root / 'config/application-profile.yaml'
        profile.parent.mkdir()
        profile.write_text(yaml.safe_dump({'company_retry_after': [dict(
            company='Alias Employer', aliases=['Parent Brand'], allow_after='2026-01-01')]}), encoding='utf-8')
        with patch('jobintel.rejection_cooldown.op.get_store', return_value=None):
            rules = load_retry_rules(self.registry)
        self.assertIn('2027-03-25', retry_reason('Parent Brand', rules, today=date(2026, 10, 24)))
