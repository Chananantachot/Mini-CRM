#!/bin/bash

echo "🔧 Activating virtual environment..."
. .venv/bin/activate

echo "🛑 Killing processes on ports 5000..."
kill -9 $(lsof -iTCP:443 -sTCP:LISTEN) 2>/dev/null



echo "🌐 Setting Flask env for auto-reload..."
export FLASK_APP=app.py
export FLASK_ENV=development


echo "🔧 Database initializing..."
flask seed

echo "🌐 Starting App with auto-reload..."
sudo flask run --port=443 --cert=cert.pem --key=key.pem --reload
