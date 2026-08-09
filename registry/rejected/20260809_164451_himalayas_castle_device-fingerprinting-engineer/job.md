# Device Fingerprinting Engineer

Posted: 2026-08-08T20:29:39Z

## Rejection

- Category: tech_stack
- Reason: role does not mention Go/Golang or PHP

Device fingerprinting is often misunderstood.

From the outside, it looks like a simple problem: collect a set of signals from the browser, hash them, and suddenly you have a device identifier that can track bots and fraudsters.

Anyone who has built fingerprinting systems at scale knows the reality is very different.

Browsers and operating systems evolve constantly. APIs appear, change behavior, or disappear. Hardware configurations change. Users travel, change networks, or simply resize their screens. At the same time, fraudsters actively manipulate their environment using anti-detect browsers, patched Chromium builds, canvas manipulation, and residential proxies. They clear storage, rotate identities, and try to make multiple devices look like one — or one device look like many.

In practice, production-grade fingerprinting systems are much more than a hash of JavaScript attributes. They combine reliable client-side signal collection with sophisticated server-side logic that determines whether two fingerprints actually belong to the same device or user — even when the signals are noisy, drifting over time, or intentionally manipulated.

[Castle](https://himalayas.app/companies/castle) is a small, profitable team building a real-time trust layer for modern platforms, and fingerprinting is one of the core components of that system.

Many fingerprinting systems look stable at first but break down under real-world conditions. Signals evolve, environments are manipulated, collisions happen, and what once looked like a reliable identifier becomes unusable. Our approach is to treat fingerprints as evolving representations rather than static identifiers. The goal is to reliably recognize devices over time, even when signals change and attackers actively try to interfere.

This role owns fingerprinting end to end: from signal collection in the browser to the matching logic on the server side.

In practice, this means working with other JavaScript researchers and detection engineers to design new signals, build reliable client-side collection mechanisms, and develop the algorithms that determine whether two fingerprints likely belong to the same device or user.

We already have fingerprinting systems running in production. The goal of this role is to take them much further.

### You will work on problems such as:

-

Designing and improving the overall fingerprinting system, from signal collection to matching logic

-

Proposing new approaches to measure fingerprint quality, stability, and long-term effectiveness

-

Detecting manipulated or inconsistent fingerprints in adversarial browser environments

-

Building matching algorithms that remain reliable despite drift, collisions, and partial fingerprints

-

Ensuring the system remains performant and resilient as browsers evolve and attacker techniques change

We are looking for someone who has already built or operated device fingerprinting systems at real scale.

You have worked on signal collection in real browsers, not just theoretical models. You have dealt with unstable signals, fingerprint collisions, and manipulated environments. You understand the tradeoffs between entropy, stability, and collection cost. You have experience designing matching or clustering algorithms that operate under noisy and adversarial conditions.

If you have spent time thinking about how to reliably track devices on the modern web — even when the device tries not to be tracked — you will probably find this problem interesting.

And yes, since this is still a job post: we pay US-level salaries globally, we’re remote-friendly in Europe, and we care far more about outcomes than hours.

Originally posted on [Himalayas](https://himalayas.app)
