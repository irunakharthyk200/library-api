import os
import pytest
import psycopg2
from app import create_app

TEST_DB_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "port": int(os.environ.get("POSTGRES_PORT", "5432")),
    "database": os.environ.get("POSTGRES_DB", "library_test_db"),
    "user": os.environ.get("POSTGRES_USER", "postgres"),
    "password": os.environ.get("POSTGRES_PASSWORD", "secret"),
}

@pytest.fixture(scope="session")
def test_db():

    admin_config = TEST_DB_CONFIG.copy()
    admin_config["database"] = "postgres"
    
    conn = psycopg2.connect(**admin_config)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_CONFIG['database']}")
    cur.execute(f"CREATE DATABASE {TEST_DB_CONFIG['database']}")
    
    cur.close()
    conn.close()

    conn = psycopg2.connect(**TEST_DB_CONFIG)
    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS authors (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                birth_year INTEGER
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                genre TEXT,
                year_published INTEGER,
                author_id INTEGER REFERENCES authors(id),
                created_by TEXT,
                status TEXT DEFAULT 'available'
            );
        """)
    yield conn
    conn.close()

@pytest.fixture
def client(test_db):
    app = create_app(TEST_DB_CONFIG)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

    with test_db.cursor() as cur:
        cur.execute("TRUNCATE books, authors RESTART IDENTITY CASCADE")