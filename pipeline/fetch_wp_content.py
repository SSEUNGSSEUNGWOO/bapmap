import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

WP_URL = os.getenv("WORDPRESS_URL")
AUTH = (os.getenv("WORDPRESS_USER"), os.getenv("WORDPRESS_APP_PASSWORD"))

res = sb.table("spots").select("id, name, wp_post_id").not_.is_("wp_post_id", "null").is_("content", "null").execute()

for r in res.data:
    resp = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{r['wp_post_id']}", auth=AUTH)
    if resp.status_code != 200:
        print(f"  실패: {r['name']} (HTTP {resp.status_code})")
        continue

    content = resp.json().get("content", {}).get("raw") or resp.json().get("content", {}).get("rendered", "")
    if not content:
        print(f"  내용 없음: {r['name']}")
        continue

    sb.table("spots").update({"content": content}).eq("id", r["id"]).execute()
    print(f"  ✓ {r['name']}")

print("\n완료")
