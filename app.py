import psycopg2
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor

DEFAULT_DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "secret",
    "host": "localhost",
    "port": "5432"
}

def create_app(db_config=None):
    app = Flask(__name__)
    config = db_config or DEFAULT_DB_CONFIG

    def get_db_connection():
        return psycopg2.connect(**config)

    @app.route("/api/authors", methods=["GET", "POST"])
    def manage_authors():
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if request.method == "POST":
            data = request.get_json()
            if not data or "name" not in data:
                return jsonify({"error": "Missing name"}), 400
            cur.execute("INSERT INTO authors (name, birth_year) VALUES (%s, %s) RETURNING *",
                        (data["name"], data.get("birth_year")))
            new_author = cur.fetchone()
            conn.commit()
            return jsonify(new_author), 201
        
        cur.execute("SELECT * FROM authors")
        authors = cur.fetchall()
        return jsonify(authors), 200

    @app.route("/api/authors/<int:author_id>", methods=["GET", "DELETE"])
    def author_detail(author_id):
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if request.method == "DELETE":
            cur.execute("DELETE FROM authors WHERE id = %s", (author_id,))
            if cur.rowcount == 0: return jsonify({"error": "Not found"}), 404
            conn.commit()
            return "", 204
        
        cur.execute("SELECT * FROM authors WHERE id = %s", (author_id,))
        author = cur.fetchone()
        return jsonify(author), 200 if author else 404

    @app.route("/api/books", methods=["GET", "POST"])
    def manage_books():
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if request.method == "POST":
            data = request.get_json()
            if not data or "title" not in data or "created_by" not in data:
                return jsonify({"error": "Missing fields"}), 400
            
            if data.get("author_id"):
                cur.execute("SELECT id FROM authors WHERE id = %s", (data["author_id"],))
                if not cur.fetchone(): return jsonify({"error": "Author not found"}), 400

            cur.execute("""
                INSERT INTO books (title, genre, year_published, author_id, created_by)
                VALUES (%s, %s, %s, %s, %s) RETURNING *
            """, (data["title"], data.get("genre"), data.get("year_published"), data.get("author_id"), data["created_by"]))
            new_book = cur.fetchone()
            conn.commit()
            return jsonify(new_book), 201

        genre = request.args.get("genre")
        author_id = request.args.get("author_id")
        q = request.args.get("q")
        
        query = "SELECT * FROM books WHERE 1=1"
        params = []
        if genre: 
            query += " AND genre = %s"; params.append(genre)
        if author_id: 
            query += " AND author_id = %s"; params.append(author_id)
        if q: 
            query += " AND title ILIKE %s"; params.append(f"%{q}%")
            
        cur.execute(query, params)
        return jsonify(cur.fetchall()), 200

    @app.route("/api/books/<int:book_id>", methods=["GET", "DELETE"])
    def book_detail(book_id):
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if request.method == "DELETE":
            cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
            if cur.rowcount == 0: return jsonify({"error": "Not found"}), 404
            conn.commit()
            return "", 204
        
        cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        book = cur.fetchone()
        return jsonify(book), 200 if book else 404

    @app.route("/api/authors/<int:author_id>/books")
    def get_author_books(author_id):
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id FROM authors WHERE id = %s", (author_id,))
        if not cur.fetchone(): return jsonify({"error": "Not found"}), 404
        cur.execute("SELECT * FROM books WHERE author_id = %s", (author_id,))
        return jsonify(cur.fetchall()), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)