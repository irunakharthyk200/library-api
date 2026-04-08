class TestAuthors:
    def test_get_authors_empty(self, client):
        response = client.get("/api/authors")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_create_author(self, client):
        response = client.post("/api/authors", json={"name": "Харчук Ірина", "birth_year": 2000})
        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Харчук Ірина"
        assert "id" in data

    def test_create_author_without_name(self, client):
        response = client.post("/api/authors", json={"birth_year": 1990})
        assert response.status_code == 400

    def test_get_author_by_id(self, client):
        auth = client.post("/api/authors", json={"name": "Харчук Ірина"}).get_json()
        response = client.get(f"/api/authors/{auth['id']}")
        assert response.status_code == 200
        assert response.get_json()["name"] == "Харчук Ірина"

    def test_get_author_not_found(self, client):
        assert client.get("/api/authors/999").status_code == 404

    def test_delete_author(self, client):
        auth = client.post("/api/authors", json={"name": "Харчук Ірина"}).get_json()
        assert client.delete(f"/api/authors/{auth['id']}").status_code == 204
        assert client.get(f"/api/authors/{auth['id']}").status_code == 404

    def test_delete_author_not_found(self, client):
        assert client.delete("/api/authors/999").status_code == 404

    def test_delete_author_keeps_books(self, client):
        auth = client.post("/api/authors", json={"name": "Іван Франко"}).get_json()
        book = client.post("/api/books", json={
            "title": "Zakhar Berkut", "author_id": auth["id"], "created_by": "Харчук Ірина"
        }).get_json()
        client.delete(f"/api/authors/{auth['id']}")
        res = client.get(f"/api/books/{book['id']}")
        assert res.status_code == 200
        assert res.get_json()["author_id"] is None

class TestAuthorBooks:
    def test_get_author_books(self, client):
        auth = client.post("/api/authors", json={"name": "Харчук Ірина"}).get_json()
        client.post("/api/books", json={"title": "Книга 1", "author_id": auth["id"], "created_by": "Харчук Ірина"})
        res = client.get(f"/api/authors/{auth['id']}/books")
        assert len(res.get_json()) == 1

    def test_get_author_books_empty(self, client):
        auth = client.post("/api/authors", json={"name": "Харчук Ірина"}).get_json()
        assert client.get(f"/api/authors/{auth['id']}/books").get_json() == []

    def test_get_author_books_not_found(self, client):
        assert client.get("/api/authors/999/books").status_code == 404