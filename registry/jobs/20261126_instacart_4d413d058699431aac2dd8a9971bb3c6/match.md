# Match Analysis

**Score:** 15/100  
**Recommendation:** Not Match

The candidate has relevant AWS, Go, automation, observability, and CI/CD evidence, but the vacancy explicitly hires only in four Canadian provinces while the sealed profile places the candidate in Italy. The location conflict is decisive, and detection-engineering, macOS-threat, attacker-TTP, and certification evidence is also absent.

## Why it matches

- AWS and Go experience are explicitly evidenced.
- The profile shows automation workflows, telemetry-related reliability work, testing, CI/CD, and incident-oriented production troubleshooting.

## Gaps

- No detection engineering, incident response, offensive security, threat hunting, or cyber-forensics role is evidenced.
- macOS internals and macOS threat telemetry are not evidenced.
- Detection-as-code and SOAR playbooks are not evidenced as security workflows.
- The requested security certifications are not evidenced.

## Concerns

- The posting states that current hiring is restricted to Ontario, Alberta, British Columbia, and Nova Scotia, which conflicts with the candidate's confirmed Italy location.
- The copied source label says Anywhere in the World, but the vacancy text contains the more specific Canadian hiring restriction.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Permanent work location in one of the eligible Canadian provinces | critical / stated | missing | Currently, we are only hiring in the following provinces: Ontario, Alberta, British Columbia, and Nova Scotia. | Fiumicino, Latium, Italy | The employer's stated hiring geography excludes the candidate's evidenced location and blocks the application unless an exception or relocation path exists. / Confirm whether Instacart can employ an Italy-based candidate or sponsor relocation to an eligible Canadian province before any further work. |
| 2+ years in detection engineering, incident response, or offensive security | critical / stated | missing | 2+ years of experience in a detection engineering, incident response, or offensive security role. |  | The profile does not evidence the required security-role background. / Do not position general backend reliability or support automation as detection-engineering experience. |
| Deep understanding of attacker TTPs and identity compromise | high / stated | unknown | Deep understanding of attacker TTPs across modern zero trust environments, including identity compromise, token theft, and abuse of trust boundaries |  | No direct security evidence supports this requirement. / Require explicit security evidence before treating the requirement as met. |
| Proficient macOS internals and threat telemetry | high / stated | unknown | Proficient understanding of macOS internals and telemetry available to identify macOS specific threats |  | macOS security telemetry is not evidenced. / Treat as an unverified material gap. |
| Detection-as-code with version control, testing, and CI/CD | high / stated | partial | Experience implementing detection-as-code workflows including version control, peer review processes, automated testing, and CI/CD deployment pipelines | Implemented CI/CD pipelines to ensure efficient software development processes, | General software CI/CD evidence does not establish security detection-as-code experience. / Confirm security-specific detection repositories, review, tests, and deployments. |
| Experience with a public cloud platform | high / stated | strong | Experience with 1 or more public cloud platforms (AWS, Azure, GCP) | AWS | / |
| Basic proficiency with Python, Golang, or another scripting language | meaningful / stated | strong | Basic proficiency with Python, Golang, or other programming/scripting languages | Senior Software Engineer \| Tech Lead \| Backend \| AWS \| Golang \| PHP | / |
| Relevant security certification | preferred / stated | unknown | Relevant certifications: GCFA, GCFE, GNFA, GREM, OSCP, GCIA, or similar |  | No relevant certification is evidenced in the sealed profile. / Confirm credentials only if the application route requires them. |

## Hard rejection

- The vacancy explicitly limits current hiring to Ontario, Alberta, British Columbia, and Nova Scotia, while the candidate profile states Fiumicino, Latium, Italy.
