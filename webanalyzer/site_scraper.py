import io
import re
import base64
import urllib.parse
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
from PIL import Image

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def clean_url(raw_url: str) -> str:
    """Cleans and extracts target URL, including LinkedIn safety redirect URLs."""
    url = raw_url.strip()
    if not url:
        return ""

    if "linkedin.com/safety/go/" in url and "url=" in url:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        if "url" in params and params["url"]:
            url = urllib.parse.unquote(params["url"][0])

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    return url


def download_and_encode_image(img_url: str, max_dimension: int = 1000) -> Optional[str]:
    """
    Downloads an image, resizes it with Pillow if needed, and encodes as base64 data URL.
    """
    try:
        resp = requests.get(img_url, headers=HEADERS, timeout=6, stream=True)
        if resp.status_code != 200:
            return None

        # Check content length (skip files larger than 10MB)
        content_length = resp.headers.get("Content-Length")
        if content_length and int(content_length) > 10 * 1024 * 1024:
            return None

        image_data = resp.content
        if len(image_data) < 200:
            return None  # Skip empty or tracking pixel

        img = Image.open(io.BytesIO(image_data))
        # Skip tiny tracking pixels or tiny icons
        if img.width < 100 or img.height < 100:
            return None

        # Convert to RGB if needed
        if img.mode in ("RGBA", "P", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Resize if exceeding max dimensions to keep request fast and within token limits
        if img.width > max_dimension or img.height > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=82, optimize=True)
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"

    except Exception:
        return None


def scrape_website(raw_url: str, timeout: int = 15) -> Dict[str, Any]:
    """
    Fetches and inspects a website, extracting objective UI/UX signals, DOM facts,
    and downloads key visual images for DeepSeek vision analysis.
    """
    target_url = clean_url(raw_url)
    if not target_url:
        return {"error": "Empty or invalid URL provided."}

    try:
        response = requests.get(
            target_url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
            verify=True
        )
    except requests.exceptions.SSLError:
        try:
            response = requests.get(
                target_url,
                headers=HEADERS,
                timeout=timeout,
                allow_redirects=True,
                verify=False
            )
        except Exception as e:
            return {"error": f"Failed to connect to website: {str(e)}", "url": target_url}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}", "url": target_url}

    if response.status_code >= 400:
        return {
            "error": f"Website returned HTTP status {response.status_code}",
            "status_code": response.status_code,
            "url": response.url
        }

    soup = BeautifulSoup(response.text, "html.parser")

    # 1. Page Title & Meta
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    meta_desc = ""
    desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
    if desc_tag and desc_tag.get("content"):
        meta_desc = desc_tag["content"].strip()

    # 2. Viewport (Critical for Mobile UI/UX)
    viewport_tag = soup.find("meta", attrs={"name": "viewport"})
    has_viewport = viewport_tag is not None

    # 3. Heading Structure
    h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)]
    h2_count = len(soup.find_all("h2"))
    h3_count = len(soup.find_all("h3"))

    # 4. Images & Alt Attributes
    img_tags = soup.find_all("img")
    total_images = len(img_tags)
    images_missing_alt = sum(1 for img in img_tags if not img.get("alt") or not img.get("alt").strip())

    # 5. Extract Candidate Visual Images (og:image, hero image, prominent images)
    candidate_img_urls: List[str] = []

    # og:image (high quality visual banner)
    og_img = soup.find("meta", property=re.compile(r"og:image", re.I)) or soup.find("meta", attrs={"name": re.compile(r"twitter:image", re.I)})
    if og_img and og_img.get("content"):
        candidate_img_urls.append(urllib.parse.urljoin(response.url, og_img["content"].strip()))

    # Prominent images from DOM
    for img in img_tags[:12]:
        src = img.get("src") or img.get("data-src")
        if src:
            full_src = urllib.parse.urljoin(response.url, src.strip())
            # Skip SVGs, base64 strings, or common tracking keywords
            if (full_src.startswith("http")
                and not full_src.endswith(".svg")
                and not any(k in full_src.lower() for k in ["icon", "pixel", "tracking", "avatar", "logo-small", "badge"])
                and full_src not in candidate_img_urls):
                candidate_img_urls.append(full_src)

    # Download and base64-encode top 2 prominent visual images for DeepSeek Vision
    encoded_images: List[str] = []
    processed_urls: List[str] = []
    for img_url in candidate_img_urls[:4]:
        b64_str = download_and_encode_image(img_url)
        if b64_str:
            encoded_images.append(b64_str)
            processed_urls.append(img_url)
        if len(encoded_images) >= 2:
            break

    # 6. Buttons & Calls to Action (CTA)
    cta_keywords = re.compile(
        r"(book|schedule|demo|contact|get started|sign up|start|buy|order|quote|try|free|pricing|consultation|talk to us)",
        re.I
    )
    buttons = soup.find_all(["button", "a"])
    cta_found = []
    for el in buttons:
        text = el.get_text(strip=True)
        if text and len(text) < 35 and cta_keywords.search(text):
            if text not in cta_found:
                cta_found.append(text)
        if len(cta_found) >= 8:
            break

    # 7. Forms
    forms = soup.find_all("form")
    has_contact_or_lead_form = False
    for f in forms:
        inputs = [i.get("type", "").lower() for i in f.find_all("input")]
        if "email" in inputs or "tel" in inputs or "submit" in inputs or f.find("textarea"):
            has_contact_or_lead_form = True
            break

    # 8. Navigation
    nav_present = bool(soup.find(["nav", "header"]) or soup.find(class_=re.compile(r"(nav|menu|navbar|header)", re.I)))

    # 9. Interactive Widgets / Chatbots
    page_html = response.text.lower()
    has_chat_widget = any(chat in page_html for chat in [
        "intercom", "drift", "crisp", "tawk.to", "zendesk", "livechat", "hubspot", "tidio"
    ])

    # 10. Placeholder Links
    placeholder_links = sum(1 for a in soup.find_all("a", href=True) if a["href"] in ["#", "", "javascript:void(0)", "javascript:;"])

    # 11. Clean Visible Text
    for script in soup(["script", "style", "noscript", "svg"]):
        script.extract()

    visible_text = soup.get_text(separator=" ", strip=True)
    visible_text = re.sub(r"\s+", " ", visible_text)[:3200]

    domain = urllib.parse.urlparse(response.url).netloc

    return {
        "url": response.url,
        "domain": domain,
        "status_code": response.status_code,
        "title": title,
        "meta_description": meta_desc,
        "has_viewport": has_viewport,
        "h1_tags": h1_tags[:3],
        "h1_count": len(h1_tags),
        "h2_count": h2_count,
        "h3_count": h3_count,
        "total_images": total_images,
        "images_missing_alt": images_missing_alt,
        "cta_found": cta_found,
        "has_cta": len(cta_found) > 0,
        "forms_count": len(forms),
        "has_contact_or_lead_form": has_contact_or_lead_form,
        "has_navigation": nav_present,
        "has_chat_widget": has_chat_widget,
        "placeholder_links_count": placeholder_links,
        "text_sample": visible_text,
        "encoded_images": encoded_images,
        "visual_image_count": len(encoded_images),
        "visual_image_urls": processed_urls
    }
