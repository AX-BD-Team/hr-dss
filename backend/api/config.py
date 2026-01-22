"""API 설정"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 환경
    environment: str = "development"
    debug: bool = False

    # 서버
    host: str = "0.0.0.0"
    port: int = 8000

    # 데이터베이스
    database_url: str = ""
    neo4j_uri: str = ""
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    # AI
    anthropic_api_key: str = ""

    # 보안
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "https://hr.minu.best",
        "https://hr-dss-web.pages.dev",
    ]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # .env 파일의 추가 변수 무시
    }


settings = Settings()
