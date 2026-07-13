import os
import sys
import time
import urllib.request

PAGE_URL = "https://www.bermanshul.org/shiva"
WEBHOOK_URL = "https://hook.eu1.make.com/6pp66t7d2bjeem9e4w3ei3so5dfyc8bx?message=Shiva%20page%20updated%2C%20check%20site&page=shiva&checked_at=now"
SNAPSHOT_FILE = "last_snapshot.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_page():
    url = f"{PAGE_URL}?cb={int(time.time())}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_notices(html):
    """Grab just the Bereavement Notices section so the daily date line
    and other boilerplate don't cause false-positive alerts."""
    start_marker = "Bereavement Notices"
    end_marker = "Meals for Shiva Homes"
    start = html.find(start_marker)
    end = html.find(end_marker)
    if start == -1 or end == -1 or end < start:
        # Site structure changed unexpectedly - fall back to full page
        # so we still catch changes rather than silently failing.
        return html
    return html[start:end]


def main():
    html = fetch_page()
    notices = extract_notices(html)

    old = ""
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            old = f.read()

    if notices.strip() == old.strip():
        print("No change detected.")
        return

    print("Change detected - firing webhook.")
    try:
        req = urllib.request.Request(WEBHOOK_URL, headers={"User-Agent": HEADERS["User-Agent"]})
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print(f"Webhook call failed: {e}", file=sys.stderr)
        # Still save the snapshot below so we don't re-alert every run
        # if the webhook itself is temporarily down.

    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        f.write(notices)


if __name__ == "__main__":
    main()
