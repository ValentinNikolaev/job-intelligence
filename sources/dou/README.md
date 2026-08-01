# DOU collector

The DOU collector monitors remote category pages on DOU Jobs and stores matching
vacancies with `source: dou`.

Edit [`config.yaml`](config.yaml):

```yaml
version: 1
timeout_seconds: 30
analysis_priority: 100
queries:
  - name: php-remote
    url: https://jobs.dou.ua/vacancies/?remote&category=PHP
    category: PHP
  - name: golang-remote
    url: https://jobs.dou.ua/vacancies/?remote&category=Golang
    category: Golang
```

Each query fetches one server-rendered listing page, parses `li.l-vacancy`
cards, follows each vacancy link for the full description when available, and
deduplicates overlapping category results by vacancy URL. The configured
`analysis_priority` is copied to every collected vacancy.

To use another config file, set `DOU_CONFIG` in `sources/.env`.

Run only this source with:

```text
python run.py dou
```
