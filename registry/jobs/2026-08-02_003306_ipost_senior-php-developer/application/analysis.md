# Application Analysis

## Vacancy Summary

The vacancy is for an experienced PHP product developer working on existing and new backend/frontend functionality. Explicit requirements include PHP 8.2+, at least four years of Yii2, strong MySQL knowledge, REST and external-service integrations, tests, GitLab, Docker, and practical HTML/CSS/Bootstrap/jQuery/JavaScript/Ajax/Node.js. The role can be remote, with Kyiv proximity treated as a plus rather than a requirement.

The candidate has strong evidence for PHP product engineering, MySQL performance work, REST integrations, testing, production maintenance, and team delivery. Prior Yii2 exposure is documented, but four years of Yii2 and the exact PHP-version requirement are not established. The requested frontend stack, Node.js, GitLab, Docker, and the named coding standard are also not fully evidenced.

## Company Research

- **Verified fact:** [iPOST's official company page](https://ipost.ua/about-us.html) describes a Ukrainian technology courier service founded in 2017, operating in more than 180 Ukrainian cities and serving e-commerce, retail, and private customers.
- **Verified fact:** The official site says deliveries are managed through its own courier application and that the system handles peak load. Its [customer FAQ](https://ipost.ua/help-customers.html) also describes real-time order tracking and API integration for online stores.
- **Verified fact:** The supplied [vacancy page](https://jobs.dou.ua/companies/ipost/vacancies/186031/) asks for work on an existing product codebase, MySQL, integrations, and a mixed backend/frontend scope.
- **Inference:** Reliability, fast diagnosis of existing-code behavior, and safe database changes are likely more important than greenfield architecture.
- **Unknown:** Public sources reviewed do not establish the engineering-team structure, deployment process, test coverage, or current Yii2 modernization plans.

## Initial Resume Audit

**Impact — 7/10.** Strength: the CV includes evidence such as database-load reduction and a service operating at around 50 million emails per month. Weakness: the opening did not immediately connect those outcomes to maintaining a PHP product. Rewrite example: “Investigated API and query bottlenecks” → “Reduced peak database workload and addressed API and query bottlenecks to improve service stability.”

**Keyword relevance — 6/10.** Strength: PHP, MySQL, REST APIs, integrations, tests, and product work are supported. Weakness: recent experience does not establish the required Yii2 duration or much of the frontend list. Rewrite example: “PHP frameworks” → “Prior Yii2 exposure alongside recent Laravel and Symfony production work.”

**Readability — 8/10.** Strength: clear reverse chronology and short bullets. Weakness: infrastructure detail could overshadow the core PHP/MySQL fit. Rewrite example: infrastructure tools were consolidated into one airSlate bullet so database and application work remains prominent.

**Summary effectiveness — 7/10.** Strength: seniority and backend scope are clear. Weakness: a generic Go/PHP summary underplayed legacy-code maintenance and integrations. Rewrite example: “Backend engineer across PHP and Go” → “PHP product engineer experienced in maintaining production code, improving MySQL and API performance, and integrating external services.”

**ATS compatibility — 8/10.** Strength: simple headings, plain text, standard chronology, and exact supported terms. Weakness: several mandatory terms cannot be added honestly. Baseline overall score: **7.2/10**. Priority changes were PHP-first positioning, explicit MySQL/API evidence, honest Yii2 wording, and removal of less relevant Go detail.

## Strict Hiring Manager Review

### Strengths

1. **Production PHP depth.** Recent Laravel/Symfony work and long-term PHP product experience reduce onboarding risk for a mature codebase.
2. **Database and API troubleshooting.** The airSlate evidence directly supports MySQL/query optimization and backend diagnosis.
3. **Ownership and collaboration.** Technical-lead work, delivery planning, and team leadership support the responsibility and teamwork expectations.

### Material weaknesses

1. **Yii2 duration is unproven.** This matters because the vacancy explicitly requires at least four years. Safe rewrite: “Prior Yii2 exposure” rather than “expert Yii2 developer.”
2. **Frontend breadth is thin and partly old.** The role names jQuery, Ajax, Node.js, and Bootstrap. Safe rewrite: list only supported JavaScript and Bootstrap exposure and position the candidate as backend-first.
3. **Tooling mismatches remain.** GitLab, Docker, and the stated coding standard are not in the candidate record. Safe rewrite: retain supported Git-based CI/CD and Kubernetes experience without substituting those tools.

The CV was reviewed twice: first to move PHP/MySQL evidence upward, then to remove wording that could imply unsupported Yii2 duration or frontend depth.

## Red Flags

- Recruiters may screen directly for four years of Yii2. The application should answer the duration precisely if asked; it must not imply experience not present in the source records.
- PHP 8.2+ is explicit, while the candidate record confirms PHP but not a specific production version.
- The CV and LinkedIn sources disagree on the end date of the latest role. The published CV uses the workflow's normalized date, but the candidate should confirm chronology before submission.
- The profile is backend-heavy for a role with routine frontend duties. Positioning it as full-stack would create credibility risk.
- Kyiv location is only a plus. Rome-based remote work should be discussed early, including employment and timezone arrangements.

## ATS Keyword Analysis

Top vacancy terms: PHP 8.2+, Yii2, MySQL, indexes, transactions, REST API, external services, JavaScript, jQuery, Ajax, Node.js, HTML/CSS, Bootstrap, tests, Docker.

- **Strong matches:** PHP, MySQL, REST APIs, external integrations, database optimization, testing, JavaScript/Bootstrap exposure.
- **Underrepresented but supported:** production code maintenance, query troubleshooting, product-company work, teamwork, technical ownership.
- **Missing required evidence:** four years of Yii2, PHP 8.2+, jQuery, Ajax, Node.js, Docker, GitLab, and the named coding standard.
- **Terms not added:** no unsupported tool or duration was inserted for ATS matching.

The revised CV emphasizes PHP, MySQL, REST APIs, external services, and existing-system reliability while keeping the unsupported terms out.

## Major CV Changes

- **Before:** “Backend engineer with 15+ years across PHP and Go.”  
  **After:** “Backend engineer with a long-standing focus on PHP product systems, production code, MySQL and API performance, and external integrations.”
- **Before:** “Investigated and addressed API and query performance bottlenecks.”  
  **After:** “Reduced peak database workload and addressed API and query bottlenecks to improve service stability.”
- **Before:** broad infrastructure list near the top.  
  **After:** vacancy-relevant PHP, Yii2 exposure, MySQL, REST, integrations, testing, and maintenance appear first.
- **Before:** no qualification around Yii2.  
  **After:** “prior Yii2 exposure” states the supported scope without claiming the required four years.

## Final Quality Gate

- Role fit: **6.5/10**
- Recruiter screening potential: **6/10**
- Hiring-manager appeal: **7/10**
- ATS compatibility: **7.5/10**
- Credibility: **9/10**

All claims trace to the candidate records. The CV is readable, PHP-first, and explicit about supported Yii2 exposure, while the hard duration and frontend/tooling gaps remain visible.

## Recommendation

**Apply With Reservations.** The underlying PHP, MySQL, integrations, and product-maintenance fit is credible, but the four-year Yii2 requirement may be a hard screen and should be clarified before investing heavily in the process.
