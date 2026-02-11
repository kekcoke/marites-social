from app import schemas

def test_schema_validation():
    """Test if payload matches schema"""
    payload = {
        "title": "Test Title",
        "content": "Test Content",
        "author": "Test Author",
        "published": True
    }
    
    # This should not raise an exception
    post = schemas.CreatePost(**payload)
    print(f"Schema validated: {post}")