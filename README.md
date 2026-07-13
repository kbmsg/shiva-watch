# shiva-watch
Shiva webpage watcher to send whatsapps to the membership

 I write a small script (Python) that fetches the page, compares it to the last-saved version, and calls the Make webhook if it changed.
 It runs on a GitHub Actions cron schedule (every 15 minutes) — GitHub's servers do the fetching, not Make, not my sandbox, so neither of the walls we hit apply.
 You'd need a free GitHub account and a (free) repository; I'd give you the exact files to add.
