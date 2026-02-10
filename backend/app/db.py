from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "mysql+pymysql://root:password@127.0.0.1:3306/questionnaire"
        "?charset=utf8mb4"
    )
    admin_user: str = "admin"
    admin_password: str = "dk2026#C"
    admin_token: str = "dev-admin-token"
    allow_resubmit: bool = False
    public_base_url: str = "http://localhost:5173"
    dwz_token: str | None = None
    dwz_term: str = "long-term"
    dwz_api_base: str = "https://dwz.cn"
    dwz_ssl_verify: bool = True
    dwz_ca_file: str | None = None
    export_links_format: str = "xlsx"

    class Config:
        env_file = ".env"


settings = Settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
