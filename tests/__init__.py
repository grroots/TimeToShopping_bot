"""
Tests package for TimeToShopping_bot
Unit and integration tests
"""

import pytest
import asyncio
import sys
import os

# Add bot package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test configuration
TEST_CONFIG = {
    "database_url": "sqlite+aiosqlite:///:memory:",  # In-memory for tests
    "openai_api_key": "test-key",
    "bot_token": "test:token",
    "authorized_users": [12345, 67890],
    "test_timeout": 10,  # seconds
}

# Test fixtures and utilities

@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create test database"""
    from bot.database.db import Database
    
    # Create in-memory database for testing
    db = Database()
    db.engine = None  # Will be recreated with test URL
    
    # Initialize test database
    await db.init_db()
    
    yield db
    
    # Cleanup
    await db.close()

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    class MockOpenAIClient:
        async def generate_post_text(self, post_format, keywords, additional_details=""):
            return f"Mock generated text for {post_format} with keywords: {keywords}"
        
        async def improve_text(self, original_text, instructions):
            return f"Improved: {original_text}"
        
        async def translate_text(self, text, target_language="ru"):
            return f"Translated to {target_language}: {text}"
        
        async def test_connection(self):
            return True
    
    return MockOpenAIClient()

@pytest.fixture
def sample_post_data():
    """Sample post data for testing"""
    return {
        "title": "Test Post",
        "keywords": "test, keywords",
        "text": "🔥 This is a test post in Armenian: Սա ստուգման փոստ է։ Գնել հիմա!",
        "media_type": "photo",
        "file_id": "test_file_id_12345",
        "status": "draft",
        "post_format": "selling",
        "created_by": 12345
    }

@pytest.fixture
def sample_analytics_data():
    """Sample analytics data for testing"""
    return {
        "post_id": 1,
        "action": "click_CTA",
        "user_id": "12345",
        "metadata": '{"source": "test"}'
    }

# Test utilities

def create_mock_message(user_id=12345, text="test message", **kwargs):
    """Create mock Telegram message for testing"""
    class MockUser:
        def __init__(self, user_id):
            self.id = user_id
            self.username = f"user{user_id}"
            self.first_name = "Test"
            self.last_name = "User"
    
    class MockChat:
        def __init__(self):
            self.id = -100123456789
            self.type = "channel"
    
    class MockMessage:
        def __init__(self, user_id, text, **kwargs):
            self.from_user = MockUser(user_id)
            self.chat = MockChat()
            self.text = text
            self.message_id = kwargs.get('message_id', 1)
            self.date = kwargs.get('date', None)
            
            # Add media attributes if needed
            self.photo = kwargs.get('photo')
            self.video = kwargs.get('video')
            self.animation = kwargs.get('animation')
        
        async def answer(self, text, **kwargs):
            return MockMessage(self.from_user.id, text)
    
    return MockMessage(user_id, text, **kwargs)

def create_mock_callback(user_id=12345, data="test:callback", **kwargs):
    """Create mock callback query for testing"""
    class MockCallbackQuery:
        def __init__(self, user_id, data, **kwargs):
            from tests import create_mock_message
            self.from_user = create_mock_message(user_id).from_user
            self.data = data
            self.id = kwargs.get('id', 'callback_id_123')
            self.message = kwargs.get('message')
        
        async def answer(self, text="", show_alert=False):
            return True
    
    return MockCallbackQuery(user_id, data, **kwargs)

# Test data generators

def generate_test_posts(count=10):
    """Generate test post data"""
    posts = []
    for i in range(count):
        posts.append({
            "title": f"Test Post {i+1}",
            "keywords": f"keyword{i+1}, test",
            "text": f"Test post content {i+1} in Armenian: Թեստ {i+1}",
            "status": "draft" if i % 2 == 0 else "published",
            "post_format": ["selling", "collection", "info", "promo"][i % 4],
            "created_by": 12345
        })
    return posts

def generate_test_analytics(post_ids, actions=None):
    """Generate test analytics data"""
    if actions is None:
        actions = ["click_CTA", "view", "share"]
    
    analytics = []
    for post_id in post_ids:
        for action in actions:
            analytics.append({
                "post_id": post_id,
                "action": action,
                "user_id": "12345"
            })
    return analytics

# Test assertions helpers

def assert_armenian_text(text):
    """Assert that text contains Armenian characters"""
    armenian_range = range(0x0530, 0x058F + 1)
    assert any(ord(char) in armenian_range for char in text), f"Text does not contain Armenian characters: {text}"

def assert_valid_post_format(post_format):
    """Assert valid post format"""
    valid_formats = ["selling", "collection", "info", "promo"]
    assert post_format in valid_formats, f"Invalid post format: {post_format}"

def assert_valid_media_type(media_type):
    """Assert valid media type"""
    valid_types = ["photo", "video", "gif", None]
    assert media_type in valid_types, f"Invalid media type: {media_type}"

# Test runner configuration
if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__])