# trase-uat-hosted-tool

An externally deployed (hosted) tool for Trase OS UAT: `UatBusinessDaysUntil` counts working days
between two dates. Input: `{"due_date": "2026-10-16", "start_date": "2026-10-05"}` -> 9 business days.

Deploy: Studio > Deployments > Deploy a tool > this repo > tool name `UatBusinessDaysUntil`, then from the
repo root: `trase-os-sdk register-tool tools/business_days_until.py`.
