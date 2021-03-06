#!/usr/bin/env bash
set -e

python -m pytest -vv --cov-report=xml --cov-report=html --cov=scrummasterjr.jira --cov=scrummasterjr.app --cov=scrummasterjr.jiracommand --cov-fail-under=75

if [ "$CODECOV" == "true" ]; then
    bash <(curl -s https://codecov.io/bash);
fi
