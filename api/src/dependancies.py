from src.database import SessionLocal, AsyncSessionLocal, UnreachableDatabase
from sqlalchemy.exc import OperationalError


# Database dependency yielder
def get_db():
    db = SessionLocal()
    try:
        yield db
    except OperationalError as e:
        raise UnreachableDatabase() from e
    finally:
        db.close()

# Database async dependency yielder
async def get_async_db():
    db = AsyncSessionLocal()
    try:
        yield db
    except OperationalError as e:
        raise UnreachableDatabase() from e
    finally:
        await db.close()
