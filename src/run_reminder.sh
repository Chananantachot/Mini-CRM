#!/bin/bash

cd /Users/achananantachot/Downloads/Mini-CRM/src || exit 1

if [ ! -d ".venv" ]; then
  echo "Virtual environment not found!"
  exit 1
fi

source .venv/bin/activate
python3 scripts/send_task_reminders.py
