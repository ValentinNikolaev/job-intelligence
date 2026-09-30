from __future__ import annotations

import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen


API_URL = "https://readytotouch.com/api/v1/unsafe/golang/companies.json"
SOURCE_URL = "https://readytotouch.com/golang/companies?remote=1"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "companies"


def slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-") or "company"


def link(label: str, url: str | None) -> str:
    return f"[{label}]({url})" if url else "—"


def company_markdown(company: dict, fetched_on: str) -> str:
    name = str(company.get("name") or "Unnamed company").strip()
    linkedin = company.get("linkedin_profile") or {}
    github = company.get("github_profile") or {}
    glassdoor = company.get("glassdoor_profile") or {}
    careers = company.get("careers_url") or ""
    about = company.get("about_url") or ""
    blog = company.get("blog_url") or ""
    linkedin_verified = " (verified by ReadyToTouch)" if linkedin.get("verified") else ""
    github_verified = " (verified by ReadyToTouch)" if github.get("verified") else ""
    glassdoor_verified = " (verified by ReadyToTouch)" if glassdoor.get("verified") else ""
    github_url = f"https://github.com/{github['login']}" if github.get("login") else None
    lines = [
        f"# {name}",
        "",
        f"- ReadyToTouch: {link('company profile', f'https://readytotouch.com/golang/companies/{linkedin.get('alias', '')}')}",
        f"- Website: {link('official site', company.get('base_url'))}",
        f"- Careers: {link('careers', careers)}",
        f"- Dev blog: {link('dev blog', blog)}",
        f"- About: {link('about', about)}",
        f"- Remote flag (ReadyToTouch): {'yes' if company.get('remote') else 'no'}",
        f"- Type: {company.get('type') or '—'}",
        f"- Description (ReadyToTouch): {company.get('short_description') or '—'}",
        f"- Industries: {', '.join(item.get('name', item.get('alias', '')) for item in company.get('industries') or []) or '—'}",
        "",
        "## Profiles",
        "",
        f"- LinkedIn alias: {linkedin.get('alias') or '—'}{linkedin_verified}",
        f"- GitHub: {link(github.get('login') or 'profile', github_url)}{github_verified}",
        f"- Glassdoor overview: {link('overview', glassdoor.get('overview_url'))}{glassdoor_verified}",
        f"- Glassdoor reviews: {link('reviews', glassdoor.get('reviews_url'))}",
        f"- Glassdoor rating (ReadyToTouch): {glassdoor.get('reviews_rate') or '—'}",
        "",
        "## Provenance",
        "",
        f"- Source dataset: {link('ReadyToTouch Go companies API', API_URL)}",
        f"- Source listing: {link('Golang companies, remote filter', SOURCE_URL)}",
        f"- Retrieved: {fetched_on}",
        f"- ReadyToTouch company ID: {company.get('id', '—')}",
        "- Metadata above is transcribed from ReadyToTouch. LinkedIn is recorded as its ReadyToTouch alias; the GitHub URL is formed from the supplied login. Careers destinations and their hiring platform have not yet been independently checked.",
        "",
    ]
    return "\n".join(lines)


def render(companies: list[dict], fetched_on: str) -> None:
    selected = [company for company in companies if company.get("remote") is True]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = OUTPUT / "records"
    records.mkdir(parents=True, exist_ok=True)

    rows = [
        "# Company directory",
        "",
        f"Snapshot retrieved {fetched_on} from ReadyToTouch's Go companies listing with its remote filter applied: {len(selected)} companies.",
        "",
        "The directory is separate from vacancy-source configuration. It stores company metadata and discovery links; it does not register or enable job collection.",
        "",
        "| Company | Careers | Dev blog | About | LinkedIn | GitHub | Glassdoor | Card |",
        "|---|---|---|---|---|---|---|---|",
    ]
    blogs = [
        "# Go company dev blogs to follow",
        "",
        f"Dev blog links supplied by ReadyToTouch for remote Go companies ({fetched_on}). Links are listed separately for easy subscription and have not been independently checked in this pass.",
        "",
        "| Company | Dev blog | Careers | Company card |",
        "|---|---|---|---|",
    ]

    for company in selected:
        name = str(company.get("name") or "Unnamed company").strip()
        company_id = str(company.get("id", "unknown"))
        slug = f"{slugify(name)}-{company_id}"
        card = f"records/{slug}.md"
        (records / f"{slug}.md").write_text(company_markdown(company, fetched_on), encoding="utf-8")

        linkedin = company.get("linkedin_profile") or {}
        github = company.get("github_profile") or {}
        glassdoor = company.get("glassdoor_profile") or {}
        linkedin_url = f"https://www.linkedin.com/company/{linkedin['alias']}" if linkedin.get("alias") else ""
        github_url = f"https://github.com/{github['login']}" if github.get("login") else ""
        glassdoor_url = glassdoor.get("overview_url") or ""
        rows.append(
            "| " + " | ".join(
                [
                    name,
                    link("careers", company.get("careers_url")),
                    link("dev blog", company.get("blog_url")),
                    link("about", company.get("about_url")),
                    link("LinkedIn", linkedin_url),
                    link("GitHub", github_url),
                    link("Glassdoor", glassdoor_url),
                    link("open", card),
                ]
            ) + " |"
        )
        if company.get("blog_url"):
            blogs.append(
                f"| {name} | {link('Dev blog', company['blog_url'])} | {link('careers', company.get('careers_url'))} | {link('card', card)} |"
            )

    (OUTPUT / "README.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (OUTPUT / "dev-blogs.md").write_text("\n".join(blogs) + "\n", encoding="utf-8")


def main() -> int:
    if "--stdin" in sys.argv[1:]:
        payload = json.load(sys.stdin)
    else:
        request = Request(API_URL, headers={"User-Agent": "job-intelligence-company-directory/1.0"})
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    companies = payload.get("companies") if isinstance(payload, dict) else None
    if not isinstance(companies, list):
        raise ValueError("ReadyToTouch response does not contain a companies list")
    render(companies, date.today().isoformat())
    print(f"Wrote company directory for {sum(company.get('remote') is True for company in companies)} remote companies to {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
