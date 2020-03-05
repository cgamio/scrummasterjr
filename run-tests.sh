#!/usr/bin/env bash

export SLACK_SIGNING_SECRET="test-signing-secret"
export SLACK_BOT_TOKEN="test-slack-bot-token"
export JIRA_HOST="test-jira-host"
export JIRA_USER="test-jira-user"
export JIRA_TOKEN="test-jira-token"

python -m pytest
