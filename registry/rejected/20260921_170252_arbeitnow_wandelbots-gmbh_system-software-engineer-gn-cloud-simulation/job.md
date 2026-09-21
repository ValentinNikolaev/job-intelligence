# System Software Engineer (gn) Cloud & Simulation

Posted: 2026-09-21T14:09:43Z

## Rejection

- Category: location_requirement
- Reason: vacancy is explicitly non-remote

**Your mission**

At Wandelbots, we are building NOVA, a platform that makes industrial robot programming accessible to everyone. Our Simulation team develops the technologies that allow partners, customers, and internal teams to work with photorealistic digital twins of real production environments.

This includes a pipeline that transforms real-world scans into usable 3D scenes through Gaussian Splatting, as well as a browser-based streaming platform built on NVIDIA Omniverse and Isaac Sim. Both technologies work today, but neither is yet operated as a product. Your mission is to change that.

The first step is internal standardization. We want to replace individually maintained environments and hand-crafted deployments with one reproducible, documented solution that teams can use independently: scene in, session out, without requiring the Simulation team to operate every setup.
The second step is external productization. The same capabilities need to be packaged so that partners and customers can operate them in their own environments.
E.g. with versioned releases, stable interfaces, tenant isolation, diagnostics, upgrade paths, and documentation.

You will join the Simulation team and focus on the infrastructure and operational foundations of these systems. You will not be building them in isolation: Wandelbots has an established infrastructure team responsible for shared infrastructure and platform capabilities. You will work closely with that team while owning the simulation-specific workloads, deployment patterns, and operational requirements.

This is a hands-on engineering role with room to shape architecture and make technical decisions in collaboration with the teams involved.

What you will work on

-

Build and operate the GPU infrastructure required by our simulation workloads, including NVIDIA GPU Operator, device plugins, driver lifecycle, and GPU sharing through MIG or time slicing

-

Work with the infrastructure team to integrate simulation workloads into our shared Kubernetes and cloud infrastructure

-

Make deployments declarative and reproducible using Infrastructure as Code and GitOps, and help consolidate the tooling used across today’s environments

-

Own CI/CD and the container and image lifecycle for CUDA- and NGC-based workloads

-

Design scheduling and autoscaling for two distinct workload profiles: latency-sensitive interactive streaming sessions and compute-intensive Gaussian Splatting jobs

-

Turn the Gaussian Splatting pipeline into a reproducible workflow, from data capture and training to OpenUSD assets

-

Operate and extend our Omniverse and Isaac Sim streaming platform, including Kit App Streaming, session lifecycle, and tenant isolation

-

Establish the platform as an internal standard through self-service workflows, golden paths, templates, onboarding, and documentation

-

Prepare the solution for operation by partners and customers through packaged deployments, versioned releases, upgrade paths, and actionable diagnostics

-

Support deployments across cloud, on-premises, and partner-managed environments

-

Build meaningful observability using metrics, logs, GPU telemetry, and actionable alerting

-

Define the simulation-specific security and access model, including ingress, TURN and STUN for WebRTC, RBAC, secrets management, SSO, and tenant boundaries

-

Work closely with our robotics, product, and platform teams to ensure that the solution supports real development and customer workflows

**Your profile**

We are looking for an engineer who is interested in how complex systems are built, deployed, and operated, not only in delivering the next application feature.
You should bring:

-

Experience building or operating production systems in platform engineering, infrastructure, SRE, DevOps, or systems software

-

Practical Kubernetes experience, including resource management, workload scheduling, and debugging distributed systems under load

-

Experience with Infrastructure as Code, GitOps, and CI/CD, together with the ability to evaluate tools based on the problem rather than a fixed preference

-

Solid knowledge of Linux, containers, and networking

-

Good Python skills for automation, services, and data-processing workflows

-

Experience with GPU workloads, or a strong technical foundation and clear interest in working with drivers, CUDA, and GPU scheduling

-

The ability to turn working technology into a system that other teams can use independently

-

A strong sense of operational ownership, including documentation, diagnostics, maintainability, and reproducibility

-

Very good English; German is a plus

We do not expect candidates to have prior experience with every technology in this description. A strong systems foundation, the ability to learn unfamiliar components, and an interest in this problem space are more important than matching every item. The scope and responsibilities of the role will grow with your experience.

Nice to have

-

Experience turning an internally developed system into a product that can be operated in customer-controlled environments

-

Hands-on experience with NVIDIA Omniverse, Isaac Sim, Kit SDK, or OpenUSD

-

Experience with Gaussian Splatting, NeRF, photogrammetry, or comparable 3D reconstruction pipelines

-

Knowledge of WebRTC, pixel streaming, or other low-latency video technologies

-

Python, Rust, or Go skills sufficient to contribute to existing services and infrastructure tooling

-

Experience with robotics or simulation, such as ROS 2 or sim-to-real workflows

-

Experience with multi-tenant platforms, air-gapped deployments, or customer environments with specific security and compliance requirements

**Why us?**

**Make an impact!**
Work on an innovative, deep tech product that adds value to the robotics world and to society! Become a crucial part of something new, big and exciting where you can truly make an impact!

**Our teams inspire!**
Cross-functional communication is key. You'll get to know many of your 100+ colleagues. Collaborate with great people on our international teams who value knowledge sharing and unique ways of doing things!

**Be authentic!**
Work in a value-driven environment where everything may not be perfect, but we're working on it! Your feedback is required while you receive feedback and appreciation for your work!

**Help others!**
You can have up to 3 days of volunteer time off to help your favorite charity.

**Develop yourself!**
We offer training and mental health opportunities so that you can develop both mentally and professionally.

**And there is even more!**
Enjoy our free lunch, snacks and drinks, team events, 30 days of annual vacation + additional rest during Christmas season until New Year. If your child gets sick, we assure that a 100% of your usual earnings will be paid while you take care of your little one.

Find [Jobs in Germany](https://www.arbeitnow.com) on Arbeitnow
