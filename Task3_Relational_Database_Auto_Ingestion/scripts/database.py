from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "retail.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = URL.create(
    drivername="sqlite",
    database=str(DB_PATH)
)

engine = create_engine(DATABASE_URL,echo=False, future=True)

@event.listens_for(engine,"connect")
def enable_foreign_keys(connection,record):
    cursor=connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def get_connection():
    return engine.connect()