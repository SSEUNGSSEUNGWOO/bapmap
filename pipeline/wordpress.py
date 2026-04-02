import os
import json
import requests
import markdown as md
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WORDPRESS_URL")
WP_USER = os.getenv("WORDPRESS_USER")
WP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD")
AUTH = (WP_USER, WP_PASSWORD)


def upload_image(image_url: str, filename: str) -> int | None:
    try:
        img_data = requests.get(image_url, timeout=10).content
    except Exception:
        return None

    resp = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        auth=AUTH,
        headers={"Content-Disposition": f'attachment; filename="{filename}.jpg"'},
        files={"file": (f"{filename}.jpg", img_data, "image/jpeg")},
    )
    if resp.status_code == 201:
        return resp.json()["id"]
    return None


def get_or_create_category(name: str) -> int:
    resp = requests.get(f"{WP_URL}/wp-json/wp/v2/categories", auth=AUTH, params={"search": name})
    cats = resp.json()
    if cats:
        return cats[0]["id"]

    resp = requests.post(f"{WP_URL}/wp-json/wp/v2/categories", auth=AUTH, json={"name": name})
    data = resp.json()
    return data.get("id", 1)


def make_slug(english_name: str) -> str:
    return english_name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace("'", "")


def upload_post(restaurant: dict, content: str) -> dict:
    category_id = get_or_create_category(restaurant.get("region", "Seoul"))

    slug = make_slug(restaurant.get("english_name") or restaurant["name"])

    # 이미지 최대 3개 업로드
    image_urls = restaurant.get("image_urls") or ([restaurant["image_url"]] if restaurant.get("image_url") else [])
    media_ids = []
    for i, url in enumerate(image_urls[:3]):
        mid = upload_image(url, f"{slug}-{i+1}")
        if mid:
            media_ids.append(mid)

    featured_media = media_ids[0] if media_ids else None

    # 갤러리 블록 HTML 생성 (WordPress Gutenberg 형식)
    gallery_html = ""
    if len(media_ids) > 1:
        gallery_items = "".join(
            f'<!-- wp:image {{"id":{mid}}} --><figure class="wp-block-image"><img src="{url}" class="wp-image-{mid}" /></figure><!-- /wp:image -->'
            for mid, url in zip(media_ids[1:], image_urls[1:3])
        )
        gallery_html = f'<!-- wp:gallery {{"columns":2,"linkTo":"none"}} --><figure class="wp-block-gallery has-nested-images columns-2">{gallery_items}</figure><!-- /wp:gallery -->\n\n'

    html_content = gallery_html + md.markdown(content, extensions=["tables", "nl2br"])

    post = {
        "title": restaurant.get("english_name") or restaurant["name"],
        "content": html_content,
        "status": "draft",
        "slug": slug,
        "categories": [category_id],
        "meta": {
            "description": f"Local Korean restaurant guide: {restaurant.get('english_name', restaurant['name'])} in {restaurant.get('region', '')} {restaurant.get('city', '')}. Rating: {restaurant.get('rating', '')}★"
        }
    }

    if featured_media:
        post["featured_media"] = featured_media

    wp_post_id = restaurant.get("wp_post_id")
    if wp_post_id:
        resp = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{wp_post_id}", auth=AUTH, json=post)
    else:
        resp = requests.post(f"{WP_URL}/wp-json/wp/v2/posts", auth=AUTH, json=post)
    return resp.json()


if __name__ == "__main__":
    import sys
    from supabase import create_client
    from generator import generate_post

    sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

    name = sys.argv[1] if len(sys.argv) > 1 else None
    if name:
        res = sb.table("spots").select("*").eq("name", name).limit(1).execute()
    else:
        res = sb.table("spots").select("*").eq("status", "메모완료").limit(1).execute()

    if not res.data:
        print("대상 없음")
        exit()

    target = res.data[0]

    print(f"생성 중: {target['name']}")
    content = generate_post(target)

    print("WordPress 업로드 중...")
    result = upload_post(target, content)

    if result.get("id"):
        post_url = result.get("link", "")
        print(f"완료: {post_url}")
        print(f"편집: {WP_URL}/wp-admin/post.php?post={result['id']}&action=edit")

        sb.table("spots").update({
            "status": "업로드완료",
            "wp_post_id": result["id"],
            "wp_url": post_url,
        }).eq("id", target["id"]).execute()
    else:
        print(f"실패: {result}")
