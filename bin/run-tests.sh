#!/usr/bin/env bash

python -m pytest -vv --cov-report=xml --cov-report=html --cov=scrum_master_jr --cov=jira --cov-fail-under=90

RETURN=$?

if [ "$RETURN" != "0" ]; then
  exit $RETURN
fi

if [ "$CODECOV" == "true" ]; then
    bash <(curl -s https://codecov.io/bash);
fi
