import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def verify_env_variables():
    required_env_variables = [
        "SECRET_KEY",
        "MONGO_HOST",
        "MONGO_INITDB_ROOT_PASSWORD",
        "MONGO_INITDB_ROOT_USERNAME",
        "POSTGRES_USER",
        "POSTGRES_HOST",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
    ]

    missing_env_variables: list[str] = []
    for var in required_env_variables:
        if not os.getenv(var):
            missing_env_variables.append(var)

    if not missing_env_variables:
        return

    missing_env_variables_str = ", ".join(missing_env_variables)
    pytest.fail(f"Required environment variables are missing: {missing_env_variables_str}")


@pytest.fixture(scope="session")
def client():
    from tusdatos.main import app

    return TestClient(app)
