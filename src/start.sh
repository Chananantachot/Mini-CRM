#!/bin/bash

echo "🔧 Activating virtual environment..."
. .venv/bin/activate

echo "🛑 Killing processes on ports 5000..."
kill -9 $(lsof -ti:5000) 2>/dev/null


echo "🌐 Setting Flask env for auto-reload..."
export FLASK_APP=app.py          # update with your actual file
export FLASK_ENV=development     # auto-reload and debug mode


echo "🔧 Database initializing..."
flask seed

echo "🌐 Starting App with auto-reload..."
flask run --cert=cert.pem --key=key.pem --reload
