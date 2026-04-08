import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add backend to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_db, AsyncSessionLocal
from models.models import Base
from config import get_settings


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create FastAPI test client"""
    return TestClient(app)


@pytest.fixture
async def db_session():
    """Create test database session"""
    # Use in-memory SQLite for testing
    from sqlalchemy.orm import sessionmaker
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_local = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_local() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing"""
    mock_service = AsyncMock()
    mock_service.generate_blog = AsyncMock(return_value={
        "title": "How to Scale a SaaS Product",
        "content": "This is a test blog post with enough content to be meaningful.",
        "outline": {
            "sections": [
                {"heading": "Introduction", "content": "Introduction text", "level": 1},
                {"heading": "Key Points", "content": "Key points text", "level": 2},
                {"heading": "Conclusion", "content": "Conclusion text", "level": 2}
            ]
        }
    })
    return mock_service


@pytest.fixture
def mock_seo_service():
    """Mock SEO service for testing"""
    mock_service = MagicMock()
    mock_service.analyze_seo = MagicMock(return_value={
        "keyword_density": {"machine": 0.5, "learning": 0.4},
        "heading_hierarchy": {"h1_count": 1, "h2_count": 2, "issues": []},
        "readability_score": 65,
        "title_variations": ["Title 1", "Title 2"],
        "meta_description": "Meta description here",
        "seo_score": 75
    })
    return mock_service


@pytest.fixture
def sample_blog_data():
    """Sample blog data for testing"""
    return {
        "topic": "How to Scale a SaaS Product",
        "title": "Scaling Your SaaS: A Complete Guide",
        "content": "This is a detailed blog post about scaling SaaS products. " * 50,  # ~1500 words
        "outline": {
            "sections": [
                {"heading": "Introduction", "content": "Introduction text", "level": 1},
                {"heading": "Planning", "content": "Planning content", "level": 2},
                {"heading": "Execution", "content": "Execution content", "level": 2},
                {"heading": "Monitoring", "content": "Monitoring content", "level": 2},
                {"heading": "Conclusion", "content": "Conclusion text", "level": 2}
            ]
        }
    }


@pytest.fixture
def invalid_topics():
    """Collection of invalid topics for testing"""
    return {
        "empty": "",
        "too_short": "AI",
        "too_long": "A" * 513,
        "whitespace_only": "     ",
        "sql_injection": "Test'; DROP TABLE posts; --",
        "xss_attempt": "<script>alert('xss')</script>",
    }
