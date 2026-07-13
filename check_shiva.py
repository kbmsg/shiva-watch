import html
import json
import os
import re
import sys
import time
import urllib.request
 
PAGE_URL = "https://www.bermanshul.org/shiva"
WEBHOOK_URL = "https://hook.eu1.make.com/6pp66t7d2bjeem9e4w3ei3so5dfyc8bx"
SNAPSHOT_FILE = "last_snapshot.txt"
PAGE_LINK = "https://bermanshul.org/shiva"
MAX_MESSAGE_LEN = 1000
 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
 
HEBREW_RANGE = chr(0x0590) + "-" + chr(0x05FF)
 
 
def heb(*codepoints):
    return "".join(chr(c) for c in codepoints)
 
 
SEE_MORE_HE = heb(0x05DC, 0x05E8, 0x05D0, 0x05D5, 0x05EA) + " " + heb(0x05E2, 0x05D5, 0x05D3)
 
 
def fetch_page():
    url = f"{PAGE_URL}?cb={int(time.time())}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")
 
 
def extract_notices_raw(page_html):
    """Grab just the Bereavement Notices section so the daily date line
    and other boilerplate don't cause false-positive alerts."""
    start_marker = "Bereavement Notices"
    end_marker = "Meals for Shiva Homes"
    start = page_html.find(start_marker)
    end = page_html.find(end_marker)
    if start == -1 or end == -1 or end < start:
        # Site structure changed unexpectedly - fall back to full page
        # so we still catch changes rather than silently failing.
        return page_html
    return page_html[start:end]
 
 
def html_to_text(raw):
    """Strip HTML tags/entities down to clean, readable plain text."""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()
 
 
def first_english_sentence(text):
    match = re.search(r".+?[.!?](\s|$)", text)
    return match.group(0).strip() if match else text[:200].strip()
 
 
def first_hebrew_sentence(text):
    match = re.search(rf"([{HEBREW_RANGE}][^.!?\n]*[.!?])", text)
    return match.group(1).strip() if match else None
 
 
def build_message(clean_text):
    if len(clean_text) <= MAX_MESSAGE_LEN:
        # Full section already naturally contains both English and Hebrew,
        # since each notice is written in both languages back to back.
        return f"\U0001F514 Shiva page updated:\n\n{clean_text}\n\nFull page: {PAGE_LINK}"
 
    # Too long - send first sentence in English and in Hebrew, plus a link.
    en_sentence = first_english_sentence(clean_text)
    he_sentence = first_hebrew_sentence(clean_text)
 
    parts = [f"\U0001F514 Shiva page updated:", en_sentence]
    if he_sentence:
        parts.append(he_sentence)
    parts.append(f"For more information / {SEE_MORE_HE}: {PAGE_LINK}")   
 parts.append(f"{SEE_MORE_HE}: {PAGE_LINK}")
    return "\n\n".join(parts)
 
 
def main():
    page_html = fetch_page()
    clean_notices = html_to_text(extract_notices_raw(page_html))
 
    old = ""
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            old = f.read()
 
    if clean_notices.strip() == old.strip():
        print("No change detected.")
        return
 
    print("Change detected - firing webhook.")
    message = build_message(clean_notices)
 
    payload = json.dumps({
        "message": message,
        "page": PAGE_LINK,
        "checked_at": str(int(time.time())),
    }).encode("utf-8")
 
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": HEADERS["User-Agent"]},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print(f"Webhook call failed: {e}", file=sys.stderr)
        # Still save the snapshot below so we don't re-alert every run
        # if the webhook itself is temporarily down.
 
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        f.write(clean_notices)
 
 
if __name__ == "__main__":
    main()
