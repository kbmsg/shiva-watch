# shiva-watch
Shiva webpage watcher to send whatsapps to the membership<p>

 I write a small script (Python) that fetches the page, compares it to the last-saved version, and calls the Make webhook if it changed.<p>
 It runs on a GitHub Actions cron schedule (every 15 minutes) — GitHub's servers do the fetching, not Make, not my sandbox, so neither of the walls we hit apply.<p>
 You'd need a free GitHub account and a (free) repository; I'd give you the exact files to add.<p>

GitHub Actions only handles the checking/detecting part.<p>
The actual delivery to WhatsApp still goes through Make (receives the webhook) → Whapi.Cloud (has your WhatsApp session connected, does the actual sending).<p>

So the full chain is:
GitHub Actions (checks the page every 15 min) → Make webhook → Whapi.Cloud → WhatsApp<p>
GitHub Actions can't send WhatsApp messages itself — it just replaces the piece that was failing (the automated page-checking), while Make + Whapi.Cloud remain the delivery mechanism, which we already confirmed works.<p>

A few concrete signals to check, in order of how quickly you'll see them:<p>

The Actions tab log, immediately. After you trigger it (or after the first automatic run), click into that run in GitHub's Actions tab — it'll print either "No change detected" or "Change detected - firing webhook."<p>
That tells you the fetch and comparison logic itself is working, independent of whether WhatsApp delivery is fast.<p>
The repo file last_snapshot.txt gets created/updated. If you see that file appear (or its timestamp update) after a run, state-saving is working.<p>
WhatsApp, eventually. Given the delivery delays we've seen from Whapi.Cloud before, don't panic if it doesn't land within a minute — but it should show up.<p>
Ongoing peace of mind: every 15 minutes a new run appears in the Actions tab whether or not anything changed, so you can spot-check anytime that it's still alive versus GitHub silently disabling it, which it does automatically if a repo goes 60 days with no activity.<p>

If you want a forced, deliberate test rather than waiting for a real site edit: edit last_snapshot.txt in the repo to any different text, then hit "Run workflow" manually — it'll compare against the real live page, see a mismatch, and fire the alert.<p>
That's a clean way to re-verify anytime without needing an actual change on the shul website.<p>
