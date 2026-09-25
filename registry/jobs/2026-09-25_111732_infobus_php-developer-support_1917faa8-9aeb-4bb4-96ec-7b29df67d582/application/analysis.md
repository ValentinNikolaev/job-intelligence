# Application Analysis — INFOBUS: PHP Developer (Support)

## Vacancy Summary

INFOBUS Holding, an international ticket-booking platform operating BUSSYSTEM across
more than 40 countries, is hiring a PHP Developer to support and stabilize existing
partner-facing systems: fixing bugs, optimizing databases, and diagnosing partner API
integration issues. The role includes a weekend duty rotation and is explicitly
framed around maintenance and troubleshooting rather than greenfield development.

## Company Research

INFOBUS was founded in 2002 and built its own online ticket-sales system, BUSSYSTEM,
which now spans more than 40 countries, 37,000 cities, 47,000 routes, 6,500 carriers,
and over 10,000 points of sale, per the company's own profile and job posting
(https://jobs.dou.ua/companies/infobus/vacancies/364976/). This scale means the
partner-integration surface referenced in the posting is genuinely large, which
supports the candidate's framing of the role as varied troubleshooting work rather
than repetitive maintenance.

## Initial Resume Audit

The candidate's most relevant, directly transferable experience is the CRURATED
Crutrade integration ownership (authentication/OTP, account linking, purchase
verification, request/response logging) and the CRURATED DataLake/event-analytics
ownership (99.9%+ delivery reliability, sub-4-hour stream onboarding). The airSlate
database-bottleneck story adds a second, independent proof point for the
"database performance" requirement. The candidate's most recent full-time role
(Simple.life) is Go-focused rather than PHP-focused, which is honestly disclosed
rather than concealed, with the concurrent CRURATED PHP subcontract used to establish
current PHP relevance.

## Strict Hiring Manager Review

A hiring manager reading this CV would see a candidate whose most impressive recent
work (CRURATED, Simple.life) is genuinely about production ownership under load,
which matches the tone of "we need someone who can stabilize what's already running."
The main friction point a skeptical reviewer might raise is that CRURATED was a
part-time subcontract, not a full-time role, and that the most recent full-time
employer is not PHP-focused; the CV and cover letter both address this directly by
naming CRURATED as a concurrent PHP-focused engagement rather than letting the reader
infer a gap.

## Red Flags

- Git and Postman/cURL are both explicitly listed as expected tools, and no verified
  evidence entry names either one specifically; this is disclosed as an open item in
  interview preparation rather than concealed or overclaimed in the CV.
- The CRURATED engagement is part-time/concurrent, not full-time; both the CV heading
  and the cover letter make this explicit to avoid appearing misleading.
- Weekend duty rotation acceptance is not independently confirmed with the candidate
  beyond the cover letter's openness to discussing it further.

## ATS Keyword Analysis

The CV and cover letter contain: PHP, MySQL, SQL, REST API, API integration, database
performance, troubleshooting, logs, monitoring, Laravel, Symfony, Git-adjacent version
control context, JSON/XML-adjacent integration work, and production reliability
language, matching the posting's core keyword set. Postman and cURL are not present
as literal keywords since the candidate's verified record does not name them.

## Major CV Changes

The CV was built specifically for this posting: it leads with a support-and-
integration-focused Summary and headline rather than a generic backend-engineer
framing, orders Experience with the two most support-relevant employers (CRURATED,
Simple.life) first, and keeps the AWS/Kubernetes/architecture-heavy airSlate and
Hyprr material compact rather than leading with it, since this posting rewards
troubleshooting depth over architecture breadth.

## Final Quality Gate

Every Experience bullet in the CV traces to a verified evidence-bank entry with a
matching claim in claims.yaml; every numeric claim (99.9%, 20,000 tickets, 86%, 3
million emails, 10x, 4 hours) is confirmed against its cited source. The cover letter
uses two complementary, non-duplicative evidence stories and one verified,
sourced company fact. No unsupported tools, employers, or metrics were introduced.

## Recommendation

Strong recommendation to proceed. The candidate's CRURATED and airSlate evidence maps
directly onto the posting's two most emphasized requirements: partner API
integration diagnosis and database performance troubleshooting. The honest
disclosure of the CRURATED engagement's part-time nature and the Git/Postman gaps
should read as credibility rather than weakness to a careful reviewer.

## Additional Context

The candidate's Simple.life and airSlate roles both involve owning systems under
sustained production load rather than short-lived projects, which is a useful signal
for a support-oriented role where the same systems need to be maintained reliably
over long periods rather than handed off after a sprint. This continuity of
ownership, more than any single technology match, is the strongest predictor of fit
for INFOBUS's stated need.
