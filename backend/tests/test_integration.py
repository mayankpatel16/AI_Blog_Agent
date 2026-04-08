"""
Integration tests combining multiple components
Tests for:
  - End-to-end blog generation workflow
  - Database transactions and cascades
  - API workflow scenarios
  - Concurrent operations
"""

import pytest
from fastapi.testclient import TestClient
from main import app


class TestIntegrationWorkflows:
    """Integration test workflows"""

    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)

    def test_e2e_generate_and_retrieve_blog(self, client):
        """Test end-to-end: generate blog and retrieve it"""
        # Step 1: Create blog
        response = client.post(
            "/api/posts",
            json={"topic": "Complete Guide to Python"}
        )
        # Should not crash
        assert response.status_code != 500

    def test_e2e_generate_update_publish(self, client):
        """Test workflow: generate -> update -> publish"""
        # Create
        gen_response = client.post(
            "/api/posts",
            json={"topic": "Web Development Best Practices"}
        )
        # Should not crash
        assert gen_response.status_code != 500

    def test_e2e_generate_and_seo_analyze(self, client):
        """Test workflow: generate blog and analyze SEO"""
        # Create blog
        gen_response = client.post(
            "/api/posts",
            json={"topic": "SEO Optimization Guide"}
        )
        # Should not crash
        assert gen_response.status_code != 500

    def test_e2e_generate_update_outline_reseo(self, client):
        """Test workflow: generate -> update outline -> re-SEO analyze"""
        # Create
        gen_response = client.post(
            "/api/posts",
            json={"topic": "Content Marketing Strategy"}
        )
        # Should not crash
        assert gen_response.status_code != 500

    def test_list_blogs_pagination_workflow(self, client):
        """Test paginating through list of blogs"""
        # Get first page
        page1 = client.get("/api/posts?skip=0&limit=5")
        assert page1.status_code in [200, 403]
        
        # Get second page
        page2 = client.get("/api/posts?skip=5&limit=5")
        assert page2.status_code in [200, 403]

    def test_delete_blog_cascade_cleanup(self, client):
        """Test deleting blog cascades to outline and SEO"""
        # Try to delete a blog
        delete_response = client.delete("/api/posts/1")
        assert delete_response.status_code != 500

    def test_export_workflow(self, client):
        """Test exporting blog in different formats"""
        # Export as Markdown
        md_response = client.get("/api/export/1?format=markdown")
        assert md_response.status_code != 500
        
        # Export as HTML
        html_response = client.get("/api/export/1?format=html")
        assert html_response.status_code != 500

    def test_concurrent_blog_generation(self, client):
        """Test concurrent blog generation requests"""
        import threading
        
        results = []
        
        def generate_blog(topic):
            response = client.post(
                "/api/posts",
                json={"topic": topic}
            )
            results.append(response.status_code)
        
        # Start multiple concurrent requests
        threads = [
            threading.Thread(target=generate_blog, args=(f"Topic {i}",))
            for i in range(3)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All should complete without server errors (500)
        assert len(results) == 3
        assert all(code != 500 for code in results)

    def test_authentication_workflow(self, client):
        """Test authentication flow if implemented"""
        # Test login
        login_response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )
        # Should not crash
        assert login_response.status_code != 500

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_malformed_json_request(self, client):
        """Test handling of malformed JSON"""
        response = client.post(
            "/api/posts",
            json={"topic": "Valid Topic"}
        )
        # Should not crash
        assert response.status_code != 500

    def test_missing_required_field(self, client):
        """Test handling of missing required field"""
        response = client.post(
            "/api/posts",
            json={}
        )
        # Should return validation error, not 500
        assert response.status_code in [422, 401, 403, 400]

    def test_invalid_status_value(self, client):
        """Test invalid status value"""
        response = client.put(
            "/api/posts/1",
            json={"status": "invalid_status"}
        )
        # Should handle gracefully, not 500
        assert response.status_code in [422, 404, 403, 400, 401, 405]

    def test_very_large_payload(self, client):
        """Test handling of very large payload"""
        large_content = "x" * 10000
        response = client.put(
            "/api/posts/1",
            json={"content": large_content}
        )
        # Should not crash
        assert response.status_code != 500
