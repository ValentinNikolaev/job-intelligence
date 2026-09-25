# Djinni collector

Collects public [Djinni jobs](https://djinni.co/jobs/) in the PHP and Golang
categories with the Full Remote filter. The dashboard URL is account-specific;
collection uses the public search pages and does not require credentials.

Edit `config.yaml` to change the queries, request timeout, page limit, or
analysis priority. The collector follows public pagination, reads the full
description embedded in each listing card, and only accepts cards explicitly
marked Full Remote. It deduplicates jobs found by both queries using Djinni's
numeric job ID. An optional `DJINNI_CONFIG` in `sources/.env` overrides the
configuration path.

Run this source with `python run.py djinni`.
