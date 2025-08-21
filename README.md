# 🏈 SEC Football Auto-updating Calendars

This project auto-scrapes ESPN for **all SEC football teams**, builds `.ics` files, and publishes them to GitHub Pages.

### ✅ Features
- 16 SEC teams (2025 conference)
- Each team has its own calendar file
- Duplicates removed (SEC vs SEC only shows once)
- Auto-refreshes every 12 hours

### 🚀 Setup
1. Fork this repo into your GitHub account.
2. Go to repo **Settings → Pages → Source → Deploy from branch → main branch /docs folder**.
3. Wait for GitHub Actions to run (can also trigger manually under Actions tab).
4. Your calendars will be hosted at:
   ```
   https://yourusername.github.io/yourrepo/lsu.ics
   https://yourusername.github.io/yourrepo/alabama.ics
   ...
   ```
5. On iPhone → Settings → Calendar → Accounts → Add Subscribed Calendar → paste the URL.

### 🔄 Updates
- GitHub Actions runs every 12 hours.
- ESPN changes (kickoff times/TV) flow into your calendars automatically.
