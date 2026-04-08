class TestBooks:
    def test_get_books_empty(self, client):
        assert client.get("/api/books").get_json() == []

    def test_create_book(self, client):
        response = client.post("/api/books", json={
            "title": "Kobzar", "genre": "poetry", "year_published": 1840, "created_by": "Харчук Ірина"
        })
        assert response.status_code == 201
        assert response.get_json()["created_by"] == "Харчук Ірина"

    def test_create_book_without_title(self, client):
        res = client.post("/api/books", json={"created_by": "Харчук Ірина"})
        assert res.status_code == 400

    def test_create_book_without_created_by(self, client):
        res = client.post("/api/books", json={"title": "No Author"})
        assert res.status_code == 400

    def test_create_book_with_author(self, client):
        auth = client.post("/api/authors", json={"name": "Леся Українка"}).get_json()
        res = client.post("/api/books", json={
            "title": "Lisova Pisnia", "author_id": auth["id"], "created_by": "Харчук Ірина"
        })
        assert res.status_code == 201
        assert res.get_json()["author_id"] == auth["id"]

    def test_create_book_with_nonexistent_author(self, client):
        res = client.post("/api/books", json={
            "title": "Ghost", "author_id": 999, "created_by": "Харчук Ірина"
        })
        assert res.status_code == 400

    def test_get_book_by_id(self, client):
        book = client.post("/api/books", json={"title": "Test", "created_by": "Харчук Ірина"}).get_json()
        assert client.get(f"/api/books/{book['id']}").status_code == 200

    def test_get_book_not_found(self, client):
        assert client.get("/api/books/999").status_code == 404

    def test_delete_book(self, client):
        book = client.post("/api/books", json={"title": "Delete me", "created_by": "Харчук Ірина"}).get_json()
        assert client.delete(f"/api/books/{book['id']}").status_code == 204
        assert client.get(f"/api/books/{book['id']}").status_code == 404

    def test_create_book_default_status(self, client):
        """Книга створюється зі статусом за замовчуванням - Харчук Ірина"""
        response = client.post("/api/books", json={
            "title": "Test Book",
            "created_by": "Харчук Ірина",
        })
        assert response.status_code == 201

class TestBooksFilter:
    def test_filter_by_genre(self, client):
        client.post("/api/books", json={"title": "P1", "genre": "poetry", "created_by": "Харчук Ірина"})
        client.post("/api/books", json={"title": "N1", "genre": "novel", "created_by": "Харчук Ірина"})
        res = client.get("/api/books?genre=poetry")
        data = res.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "P1"

    def test_filter_by_author_id(self, client):
        auth = client.post("/api/authors", json={"name": "Ірина"}).get_json()
        client.post("/api/books", json={"title": "B1", "author_id": auth["id"], "created_by": "Харчук Ірина"})
        res = client.get(f"/api/books?author_id={auth['id']}")
        assert len(res.get_json()) == 1

    def test_search_by_title(self, client):
        client.post("/api/books", json={"title": "Kobzar", "created_by": "Харчук Ірина"})
        res = client.get("/api/books?q=kob")
        assert len(res.get_json()) == 1

    def test_filter_no_results(self, client):
        res = client.get("/api/books?genre=nonexistent")
        assert res.get_json() == []