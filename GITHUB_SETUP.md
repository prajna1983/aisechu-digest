# Publishing to GitHub Pages — Step-by-Step Guide

Your public URL will be: **`https://YOUR-USERNAME.github.io/aisechu-digest/`**

---

## Step 1 — Create a GitHub account (if you don't have one)

Go to [github.com](https://github.com) and sign up. It's free.

---

## Step 2 — Create a new public repository

1. Click the **+** icon (top-right) → **New repository**
2. Name it: `aisechu-digest`
3. Set visibility to **Public**
4. Leave everything else as default
5. Click **Create repository**

---

## Step 3 — Upload the project files

In Terminal, run these commands (replace `YOUR-USERNAME` with your GitHub username):

```bash
cd ~/Desktop/aisechu_digest

# Initialise git and push to GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/aisechu-digest.git
git push -u origin main
```

If prompted, sign in with your GitHub credentials.
(If you haven't used git before, you may first need to run:
`git config --global user.email "you@example.com"` and
`git config --global user.name "Your Name"`)

---

## Step 4 — Add your Anthropic API key as a secret

GitHub Actions needs your API key to call Claude. It's stored securely as a secret — it never appears in any logs.

1. Go to your repo on GitHub: `github.com/YOUR-USERNAME/aisechu-digest`
2. Click **Settings** (top tab) → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: paste your `sk-ant-...` key
6. Click **Add secret**

---

## Step 5 — Enable GitHub Pages

1. In your repo, go to **Settings** → **Pages** (left sidebar)
2. Under **Source**, select **Deploy from a branch**
3. Branch: `main` — Folder: `/docs`
4. Click **Save**

GitHub will show you your public URL — it takes about 1 minute to go live.

Your URL: `https://YOUR-USERNAME.github.io/aisechu-digest/`

---

## Step 6 — Trigger your first digest

Rather than waiting until 7 AM tomorrow, run it now manually:

1. Go to your repo → **Actions** tab
2. Click **Daily AISecHub Digest** in the left sidebar
3. Click **Run workflow** → **Run workflow** (green button)
4. Wait ~60 seconds — it will fetch messages, call Claude, and commit the HTML
5. Refresh your GitHub Pages URL — your digest is live!

---

## How it works going forward

Every day at **07:00 UTC** the workflow runs automatically:

1. Fetches the last 24 hours of AISecHub messages
2. Sends them to Claude for categorization and summarization
3. Generates `docs/index.html` (the archive) and `docs/aisechu_digest_YYYY-MM-DD.html`
4. Commits and pushes — GitHub Pages updates within seconds
5. Digests older than 90 days are automatically deleted

No action needed from you — just visit your URL any time to see the latest digest.

---

## Changing the schedule

The workflow runs at 07:00 UTC by default. To change it, edit `.github/workflows/daily_digest.yml` and update the cron line:

```yaml
- cron: '0 7 * * *'   # 07:00 UTC daily
```

Cron format: `minute hour * * *`
Examples:
- `0 6 * * *` → 6:00 AM UTC
- `0 8 * * 1-5` → 8:00 AM UTC, weekdays only
- `0 18 * * *` → 6:00 PM UTC

---

## Cost estimate

Each daily run makes one Claude API call with ~50–200 messages. Cost is typically **$0.01–$0.05 per day** depending on channel volume, using claude-opus-4-5. GitHub Actions is free for public repos.
