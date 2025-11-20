from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    r = conn.execute(text("SELECT id, username, email FROM users WHERE username='tangrui'"))
    rows = r.fetchall()
    print(rows)
