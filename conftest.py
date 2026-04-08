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
    conn = psycopg2.connect(**DEFAULT_DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DROP DATABASE IF EXISTS library_test_db")
    cur.execute("CREATE DATABASE library_test_db")
    
    test_config = DEFAULT_DB_CONFIG.copy()
    test_config["dbname"] = "library_test_db"
    
    with psycopg2.connect(**test_config) as t_conn:
        with t_conn.cursor() as t_cur:
            t_cur.execute("""
                CREATE TABLE authors (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    birth_year INTEGER
                );
                CREATE TABLE books (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    genre TEXT,
                    year_published INTEGER,
                    author_id INTEGER REFERENCES authors(id) ON DELETE SET NULL,
                    created_by TEXT NOT NULL
                );
            """)
    yield test_config

@pytest.fixture(scope="session")
def app(test_db):
    return create_app(db_config=test_db)

@pytest.fixture(scope="function")
def client(app, test_db):
    conn = psycopg2.connect(**test_db)
    with conn.cursor() as cur:
        cur.execute("TRUNCATE books, authors RESTART IDENTITY CASCADE")
    conn.commit()
    conn.close()
    return app.test_client()