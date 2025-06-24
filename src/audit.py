from datetime import datetime
import uuid

from flask_jwt_extended import get_jwt_identity, jwt_required
from Db import Db
from enum import Enum

class AuditAction(Enum):
    INSERT = 'INSERT'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'

@jwt_required()
def log_audit(action: AuditAction, table_name, record_id, old_value=None, new_value=None):
    db = Db.get_db()
    userName = get_jwt_identity()
    user = Db.getCurrentActiveUser(userName)
    db.execute("""
        INSERT INTO audit_logs (id, user_id, action, table_name, record_id, old_value, new_value, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        user['id'],
        action.value,
        table_name,
        record_id,
        str(old_value) if old_value else None,
        str(new_value) if new_value else None,
        datetime.utcnow()
    ))
    db.commit()
