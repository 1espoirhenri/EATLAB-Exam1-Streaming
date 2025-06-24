"""
SQLAlchemy session/engine helpers + Base declarative class.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# ========== Engine ==========
# sqlite: cần check_same_thread False, pg/mariadb không cần
sqlite_kwargs = {"check_same_thread": False} if settings.DB_URL.startswith("sqlite") else {}
engine = create_engine(settings.DB_URL, pool_pre_ping=True, connect_args=sqlite_kwargs)

# ========== Session =========
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ========== Base class for models =========
class Base(DeclarativeBase):
    pass


# ========== Init helper =========
def init_db() -> None:
    """
    Gọi hàm này 1 lần ở `app/main.py` (hoặc Alembic) để tạo bảng nếu chưa có.
    """
    import app.db.models  # noqa: F401 (chỉ để đăng ký lớp model)
    Base.metadata.create_all(bind=engine)


# ========== Dependency cho FastAPI =========
def get_db():
    """
    FastAPI dependency: `db: Session = Depends(get_db)`
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
