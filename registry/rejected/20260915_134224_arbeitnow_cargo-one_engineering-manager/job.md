# Engineering Manager

Posted: 2026-09-15T11:40:11Z

## Rejection

- Category: location_requirement
- Reason: vacancy is explicitly non-remote

## 🏆 What's the opportunity?

Air freight carries less than 1% of world trade by volume and more than a third of it by value, around $22.7 billion of goods every single day. It's how a vaccine reaches a clinic before it spoils, how a semiconductor arrives before the production line stops, and how a retailer restocks a continent away in three days instead of five weeks. When speed is the whole point, freight flies.

Somebody has to price it, book it and move it, and that work is still done largely by hand, in inboxes and spreadsheets.

For eight years we've been building the data infrastructure underneath it: direct integrations with 75 airlines, the top ten ocean carriers and dozens of GSAs, used every day by 30,000 freight forwarders across 172 countries to hold their rates, price their business and book their freight.

In 2026 we acquired Cargofive, and [cargo.one](http://cargo.one) now spans air and ocean, the two modes that carry international trade. That foundation is what makes the next part possible.

In March 2026 we launched the industry's first AI-native operating system for multimodal freight:one workspace where freight teams and AI agents work side by side across rate management, procurement, quoting, booking and support. Crane Worldwide and Yusen Logistics are rolling it out across their global operations.

AI-led engineering is how we build. Engineers write specs and acceptance criteria, agents do much of the implementation, and the engineer owns the architecture, the review and what ships.

We're backed by Index Ventures, Bessemer, Creandum, Point Nine, Next47 and Lufthansa Cargo, which has been an investor in us since 2018.

## 🚀 What makes this role different

This is an engineering management job for a team where agents do much of the implementation. That changes the job.

When producing code gets cheaper and faster, the bottleneck moves. Throughput depends more on how well engineers define the problem, direct the agents, review what comes back and tell a plausible answer from a correct one.

**You'll lead our engineers: what they ship, how good it is, how fast they move, whether the people are growing, and how quickly the team gets better at working AI-led. **A lot of what engineering managers know about pacing, estimating, reviewing and measuring a team was calibrated for a different bottleneck. **Working out what good looks like now is part of this job.**

Today, engineers direct agents on their own work. That's where we are, but it's not the end state. We're building toward fleets of agents that work on their own inside guardrails and harnesses we design, while engineers move up to setting direction, reviewing what comes back, and owning what ships. Part of your job is helping the team get there while keeping the quality bar high**.**

This is also a player-coach role. You'll stay close enough to the code to keep your judgment sharp and your technical credibility current, while the engineers you lead and what they deliver remain the focus.

## 🧭 What we're looking for — the part that isn't negotiable

**You get more from growing people than from being the smartest person in the room.** You've watched someone you managed become better than you at something and enjoyed it. You run real one-to-ones, not status meetings. You give hard feedback early and kindly, and you've done the hard version more than once.

**You think in systems. Teams are systems too.** You can see why delivery is slipping without needing someone to tell you, and you fix the process rather than working harder inside a broken one.

**You're excited about the business.** You want to know what your engineers' work is worth and what it does for the customer paying us. You can explain that to them so their work has a point beyond the issue they're closing.

**You work at eye level with Product.** You co-own what gets built and when, push back on the brief, and don't treat "Product decides, Engineering delivers" as a healthy way to work.

**You want to be in the room with customers.** Freight forwarders and airlines, directly. You'd rather hear the problem first-hand, and you take your engineers with you.

**English is your working language, at close to native fluency.** You write and speak it the way you think in it. Almost everything a manager does in a remote-first company is language: the feedback that has to land precisely, the written decision that stops a debate, the difficult conversation where the wrong word costs you trust.

**You'll also need:**

-

Experience managing engineers: hiring them, growing them, running performance honestly and shipping on a predictable cadence.

-

A backend engineering background, strong architecture instincts and enough technical currency that your engineers respect your technical opinion.

-

A delivery track record. Specific things that shipped, on a schedule you can describe, and an honest account of what slipped and why.

-

Experience building a team, not only running one. You know how to assess for potential, close a candidate and set someone up so their first ninety days work.

-

Genuine engagement with AI-led engineering. You don't need to be an expert, but you can't manage engineers working this way from the outside. You need to use the tools yourself and want to get good at them.

-

Judgment, and the nerve to use it. You'll make calls with incomplete information and own them out loud.

-

Low ego. You take feedback from your own engineers and change your mind in public.

Nice to have: experience with our stack of Python 3, Flask, gRPC, PostgreSQL, Redis, Celery and Kubernetes on GCP; Vue.js; managing a distributed team across several countries; or introducing a new way of working to a team that didn't ask for one.

## 🎬 A snapshot of what you'll be doing

-

**Own delivery.** What ships, how good it is and whether the commitments you make hold.

-

**Grow the people.** One-to-ones that are worth the hour, honest performance conversations, career paths that mean something, and knowing what each person wants next.

-

**Hire.** You'll own the hiring bar and run your own loops. We hire senior engineers on judgement and character rather than AI experience, and teach them the workflow. You'll be central to making that work.

-

**Partner with Product as an equal.** Shape the roadmap, negotiate scope and protect engineers from churn that isn't worth it.

-

**Raise the team's AI capability.** Help engineers use agents better today, spread what works, remove friction, and help evolve our setup toward autonomous agent fleets with the right guardrails and harnesses in place.

-

**Stay technical, roughly a day a week.** Reviews, a well-chosen piece of work, enough to keep your hands and judgement in.

-

**Go to the users.** Sit with freight forwarders and airlines, and take your engineers with you.

## 🤖 What you'd be working with

We're honest about where we are: Everything below is real and running today, but some of it is young, adoption is uneven across our five teams, and the next stage doesn't exist yet. You'd help build it, not inherit it.

How we work AI-led:

-

**Work starts from a spec**: Tickets and specs are drafted with agent help, against our agreed templates. Once a spec meets the bar, engineers pick it up, refine it, and own the design and architecture decisions; only then do agents start implementing.

-

Conventions for how** agents get context**, how work **runs in parallel**, and how the results come back together safely.

-

**AI review on every merge request in CI**, and a human review standard built for telling a plausible answer from a correct one.

What we've built to make that work:

-

**Our shared AI engineering practice:** spec templates, a directory of reusable AI skills, agent harnesses and review conventions for giving agents context, running work in parallel and bringing the results back together safely.

-

**A Slack-triggered agent** (Timber) that takes a Jira ticket and delivers a merge request, currently handling all bugs and small, well-scoped tickets and built on our RAG context layer and a memory layer.

-

**A triage agent** that protects the team's focus: it routes incoming questions, tickets and reports from other internal teams to the right engineering team and does the first level of triage itself; answering directly, creating a bug ticket, or escalating to a human.

The furthest edge of this is our AI team's production work, the bar the rest of the practice is being pulled toward, and closing that gap across the department is part of your job:

-

**AI doing commercial work in production.** In June 2026, Saudia Cargo went live with an AI worker our engineers built. It handles inbound rate requests around the clock and returns a quote in seconds, cutting turnaround time by 68% with 89% first-time accuracy.

-

**An LLM pipeline** turning airlines' free-text email replies into structured, bookable quotes.

## ❤️ How we work

-

Feedback is constant and direct, in both directions. You'll get it in your first week and you're expected to give it.

-

Remote-first, which means we write things down.

-

You take ownership, and you back your opinions with data.

-

Given the ambitious option and the easy one, you take the ambitious one.

-

Diverse, and playful about it.

## ✨ What we offer

-

Equity in [cargo.one](http://cargo.one). This role is equity-eligible.

-

Company-provided Claude Code and the other AI tools the work requires.

-

A one-time €650 home office budget, plus your choice of MacBook or Dell laptop, delivered before day one.

-

Co-working access through our partner Desana.

-

24 paid vacation days on top of your country's public holidays, plus special leave.

-

Two company-wide offsites a year, plus team trips.

-

Permanent full-time employment. In Germany, a contract with [cargo.one](http://cargo.one). In Portugal, a contract with our subsidiary Cargo Five. Elsewhere in our approved hiring countries, through our partner [Remote.com](http://Remote.com).

## 🌍 Where you'll work

We're remote across our approved hiring countries in the European timezone band, so the engineering team overlaps for most of the working day.

We currently hire in:

Armenia, Bosnia and Herzegovina, Bulgaria, Cyprus, Czechia, Denmark, Estonia, Finland, Georgia, Germany, Greece, Hungary, Ireland, Kosovo, Latvia, Lithuania, Malta, Moldova, Norway, Poland, Portugal, Romania, Serbia, Slovakia, South Africa, Spain, Sweden, Ukraine and the United Kingdom.

We meet in person regularly, including twice a year as a full company.

We can currently support visa processes in Germany only.

We hire for talent. If you don't tick every box but think you'd be a great match, reach out anyway. We'd love to hear from you.

Find [Jobs in Germany](https://www.arbeitnow.com) on Arbeitnow
