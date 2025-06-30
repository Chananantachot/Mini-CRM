import os
import sqlite3

from datetime import date
import json

from dotenv import load_dotenv
from pywebpush import webpush, WebPushException

load_dotenv()

# Load push credentials
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_CLAIMS = {"sub": "mailto:udth2010@gmail.com"}

# Register adapter and converter for date
sqlite3.register_adapter(date, lambda d: d.isoformat())
sqlite3.register_converter("date", lambda s: date.fromisoformat(s.decode("utf-8")))
DATABASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'crm.db'))

db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
cursor = db.cursor()

# Get tasks due today and not notified
today = date.today()
cursor.execute('''
    SELECT id, title, assigned_to 
    FROM tasks 
    WHERE due_date <= ? AND status = 'Pending' AND notified = 0
''', (today,))
tasks = cursor.fetchall()

# Group tasks by salesperson
from collections import defaultdict
user_tasks = defaultdict(list)
for task_id, title, user_id in tasks:
    user_tasks[user_id].append((task_id, title))

# Fetch subscription info per salesperson
for user_id, task_list in user_tasks.items():
    cursor.execute("SELECT subscription_json FROM subscriptions WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if not result:
        continue

    subscription_info = json.loads(result[0])
    task_count = len(task_list)
    message = f"📌 You have {task_count} task(s) due today."

    try:
        webpush(
            subscription_info,
            data=message,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
    except WebPushException as ex:
        print(f"Failed to send to {user_id}: {ex}")

#db.commit()
