# Interview preparation — Confitech Dienstleistungs GmbH

## Recruiter / HR Screening

Explain that your experience combines PHP and Go backend work, technical leadership and production services, including document automation. State that CRURATED was a concurrent part-time engagement rather than a second full-time position. The posting is for remote work from Europe or Ukraine and labels the engagement outstaff. Ask which company is the contractual counterparty, where the team is located, and whether the stated compensation is gross, net or a contractor rate. The listing shows $2,500–3,000 with consideration up to $3,500. Do not treat that figure as your confirmed expectation.

The application form asks for a number of commercial PHP years. Count actual qualifying periods without adding overlaps twice, and confirm the number before entering it. It also asks whether you have commercial experience in both DDD and TDD, and whether you have PostgreSQL and either SQL Server or Oracle. Give a truthful answer for every component. The sources reviewed do not establish all of these experiences. English upper-intermediate and Ukrainian native are in the candidate profile, while the posting asks for English B2 and Ukrainian C2.

## Culture Fit / Behavioral Interview

Prepare an example of coordinating work across product and engineering at airSlate. Explain which decisions you made, which were shared, and what the team delivered. Use the backend-lead scope in the employment extract and the candidate-confirmed account, rather than turning team results into solo achievements. A second example can cover the Simple.life telephony launch with backend, frontend and SRE. Describe the handoff and security sign-off without suggesting you led every contributor. Be ready to explain what you did when a requirement or a system boundary was unclear, using a real event rather than a hypothetical anecdote presented as history.

## Technical Interview

Review PHP language features you have actually used and be candid about versions, especially the role's reference to 8.4. Discuss how you separate domain behaviour from transport, persistence and framework details. For test-first development, explain your actual practice and its limits. A conceptual answer about TDD is not proof of commercial TDD experience. Likewise, discuss DDD through a real example only if you can explain the model, boundaries, decisions and trade-offs from your own work.

For databases, prepare examples of query analysis, indexes, transaction boundaries and correctness under concurrent requests. Distinguish systems you have used directly from technologies you know only conceptually. The airSlate database load work can support a discussion of diagnosing a production bottleneck, but do not invent the query, plan or measurements. If asked about SQL Server or Oracle and you have not used them commercially, say so and describe how you would learn the project's database conventions.

Review REST API contracts, authentication, validation, errors and backwards compatibility. The CRURATED integration is a useful example of ownership, with account linking and purchase verification in the confirmed scope. Explain the trust boundary and the integration flow only to the extent you can substantiate. Do not claim a specific library or mechanism merely because the vacancy names it.

## CV Deep-Dive Questions

For the CRURATED analytics platform, describe the problem, your technical ownership and the actual production boundaries. Explain why event versions needed parallel publication and how consumers were affected, if you can recall a specific example. Distinguish your design and ownership from the work of the wider team. For the integration, prepare to discuss account linking and purchase ownership without adding an unverified adoption figure.

For airSlate, explain the sequence from identifying database pressure to redistributing work and the resulting stability. The candidate confirmed team-level outcomes and backend leadership. Avoid presenting the withdrawn ECS-to-Kubernetes migration as your achievement. For Simple.life, explain a security decision in outbound telephony, such as keeping phone numbers out of the agent UI and logs. Explain the intended privacy benefit, the production release and your role in the cross-functional team.

## Company-Specific Preparation

The company's site presents a staffing and nearshoring business, and the vacancy describes an outstaff position on a document management product. The customer and product ownership remain unknown. The role asks for native PHP, with Symfony or a custom Symfony-based framework listed as a plus, not necessarily prior Symfony experience, although it is listed as a plus. Ask how the framework is maintained, what parts are proprietary, and how engineers can influence its evolution. Do not assume the product is the same as the candidate's previous document automation work.

## Preparation Plan

First, resolve the combined form questions using your actual employment history and examples. Next, review one airSlate database story, one CRURATED integration story and one Simple.life privacy story. For each, write down the problem, your actions, a supported result and what you would change today. Then rehearse a concise explanation of PHP experience and the areas in which your knowledge is less recent. Review database migration and transaction concepts without implying experience with a particular engine. Finally, compare the proposed contract and compensation with your own expectations once the basis is clear.

## Questions to Ask

- Who owns the product and how is the team organised between Confitech and the customer?
- Which databases are used in production, and is prior SQL Server or Oracle experience essential from the first day?
- What does the team mean by practical DDD and test-first development, and how are those practices reviewed?
- How much of the work concerns core domain modelling versus framework maintenance and integration?
- What are the contract type, pay basis, working hours and process for reviewing compensation?
- What would a successful first three months look like, and who helps a new engineer learn the domain?
