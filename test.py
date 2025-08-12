import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000/api"
USERNAME = "temirkul_off"           # superuser username
PASSWORD = "Deucalion_324"   # superuser password
SUPERUSER_ID = 1             # superuser ID (likely 1 if first user)

auth = HTTPBasicAuth(USERNAME, PASSWORD)

print("\n=== FULL SMOKE TEST START ===")

# --- 1. Create a post with 2 subposts ---
post_payload = {
    "title": "Smoke Test Post",
    "body": "Main post body",
    "author": SUPERUSER_ID,
    "subposts": [
        {
            "title": "First subpost",
            "body": "This is the first subpost"
        },
        {
            "title": "Second subpost",
            "body": "This is the second subpost"
        }
    ]
}

create_post = requests.post(f"{BASE_URL}/posts/", json=post_payload, auth=auth)
if create_post.status_code != 201:
    print("❌ Failed to create post:", create_post.status_code, create_post.text)
    exit()
post_data = create_post.json()
post_id = post_data["id"]
subpost_ids = [sp["id"] for sp in post_data["subposts"]]
print(f"✅ Created post {post_id} with subposts {subpost_ids}")

# --- 2. Update post: change title/body, update first subpost, add new, remove second ---
update_payload = {
    "title": "Updated Smoke Test Post",
    "body": "Updated main body",
    "author": SUPERUSER_ID,
    "subposts": [
        {
            "id": subpost_ids[0],
            "title": "Updated first subpost",
            "body": "Updated subpost body"
        },
        {
            "title": "New subpost after update",
            "body": "This is a newly added subpost"
        }
    ]
}
update_post = requests.put(f"{BASE_URL}/posts/{post_id}/", json=update_payload, auth=auth)
if update_post.status_code != 200:
    print("❌ Failed to update post:", update_post.status_code, update_post.text)
    exit()
print(f"✅ Updated post {post_id} successfully")

# --- 3. Bulk create posts ---
bulk_payload = [
    {
        "title": "Bulk Post 1",
        "body": "Body of bulk post 1",
        "author": SUPERUSER_ID
    },
    {
        "title": "Bulk Post 2",
        "body": "Body of bulk post 2",
        "author": SUPERUSER_ID
    }
]
bulk_create = requests.post(f"{BASE_URL}/posts/bulk_create/", json=bulk_payload, auth=auth)
if bulk_create.status_code != 201:
    print("❌ Bulk create failed:", bulk_create.status_code, bulk_create.text)
    exit()
print(f"✅ Bulk created {len(bulk_payload)} posts")

# --- 4. Like / Unlike ---
like1 = requests.post(f"{BASE_URL}/posts/{post_id}/like/", auth=auth)
print(f"👍 Like response: {like1.json()}")
like2 = requests.post(f"{BASE_URL}/posts/{post_id}/like/", auth=auth)
print(f"👎 Unlike response: {like2.json()}")

# --- 5. Views ---
view1 = requests.get(f"{BASE_URL}/posts/{post_id}/view/", auth=auth)
print(f"👀 First view count: {view1.json()}")
view2 = requests.get(f"{BASE_URL}/posts/{post_id}/view/", auth=auth)
print(f"👀 Second view count: {view2.json()}")

# --- 6. Final list ---
final_posts = requests.get(f"{BASE_URL}/posts/", auth=auth)
if final_posts.status_code == 200:
    print(f"📄 Final posts count: {len(final_posts.json())}")
else:
    print("❌ Failed to fetch posts:", final_posts.status_code, final_posts.text)

print("=== FULL SMOKE TEST COMPLETE ===\n")