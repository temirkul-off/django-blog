import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_full_api_flow():
    # Create a superuser
    user = User.objects.create_superuser(username="admin", password="adminpassword", email="admin@example.com")
    client = APIClient()
    client.login(username="admin", password="adminpassword")

    # 1. Create post with subposts
    post_payload = {
        "title": "Test Post",
        "body": "Test Body",
        "author": user.id,
        "subposts": [
            {"title": "Subpost 1", "body": "Body 1"},
            {"title": "Subpost 2", "body": "Body 2"}
        ]
    }
    create_post = client.post("/api/posts/", post_payload, format="json")
    assert create_post.status_code == 201
    post_id = create_post.data["id"]
    subpost_ids = [sp["id"] for sp in create_post.data["subposts"]]

    # 2. Update post: remove 1 subpost, update one, add one
    update_payload = {
        "title": "Updated Post",
        "body": "Updated Body",
        "author": user.id,
        "subposts": [
            {"id": subpost_ids[0], "title": "Updated Subpost", "body": "Updated body"},
            {"title": "New Subpost", "body": "New Body"}
        ]
    }
    update_post = client.put(f"/api/posts/{post_id}/", update_payload, format="json")
    assert update_post.status_code == 200

    # 3. Bulk create posts
    bulk_payload = [
        {"title": "Bulk 1", "body": "Bulk body 1", "author": user.id},
        {"title": "Bulk 2", "body": "Bulk body 2", "author": user.id}
    ]
    bulk_create = client.post("/api/posts/bulk_create/", bulk_payload, format="json")
    assert bulk_create.status_code == 201

    # 4. Like / Unlike
    like1 = client.post(f"/api/posts/{post_id}/like/")
    assert like1.data["status"] == "liked"
    like2 = client.post(f"/api/posts/{post_id}/like/")
    assert like2.data["status"] == "unliked"

    # 5. Views
    view1 = client.get(f"/api/posts/{post_id}/view/")
    assert "views_count" in view1.data
    view2 = client.get(f"/api/posts/{post_id}/view/")
    assert view2.data["views_count"] == view1.data["views_count"] + 1
