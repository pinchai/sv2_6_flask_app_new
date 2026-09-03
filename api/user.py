from api import api_bp

from extensions import db
from sqlalchemy import text


@api_bp.get('/user')
def user():
    sql = text("SELECT username, email, profile, role FROM user")
    result = db.session.execute(sql)
    rows = [dict(row._mapping) for row in result]

    return rows
