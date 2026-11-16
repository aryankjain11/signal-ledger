# Putting Signal Ledger online

The simplest host is **Streamlit Community Cloud**: free, no server to manage, and it
can be restricted to people you invite. It deploys straight from a GitHub repository
and redeploys automatically whenever you push.

## 1. Put the code on GitHub

Your existing private repo is `aryankjain11/signal-ledger`. Replace its contents with
this folder (everything except `.venv`, which `.gitignore` already excludes):

```bash
cd signal-ledger
git init                      # skip if this folder is already a clone
git remote add origin https://github.com/aryankjain11/signal-ledger.git   # skip if already set
git add -A
git commit -m "Ticker data, market read, H&S, new navigation, deploy-ready config"
git branch -M main
git push -u origin main       # use --force only if you intend to overwrite the old history
```

No GitHub CLI? On github.com: open the repo → **Add file → Upload files**, drag in the
folder contents, then commit. (The `.streamlit` and `.github` folders start with a dot;
make sure they upload too.)

## 2. Deploy

1. Go to **share.streamlit.io** and sign in with the same GitHub account.
2. **Create app → Deploy a public app from GitHub** (the repo can stay private).
3. Repository `aryankjain11/signal-ledger`, branch `main`, main file `app.py`.
4. Optional: set a custom subdomain, for example `signal-ledger`.
5. **Advanced settings → Python version: 3.13.**
6. **Deploy.** The first build installs `requirements.txt` and takes a few minutes.

You get a link like `https://signal-ledger.streamlit.app`.

## 3. Choose who can open it

In the app's **Settings → Sharing**:

- **Only specific people**: add their email addresses. Each person signs in with
  Google, GitHub or an emailed link. Community Cloud allows a limited number of
  private apps per account.
- **Public**: anyone with the link.

## Things to know when it's hosted

- Each visitor gets an independent session. Uploads stay in that session's memory,
  are not shared with other visitors, and disappear when the tab is closed. Nothing
  is saved to a database yet.
- Yahoo Finance sometimes rate-limits cloud servers. Fetched data is cached for an hour,
  which helps. If tickers fail on the hosted app but work locally, that is the cause.
  Upload a CSV, or ask for a licensed data provider to be wired in (the `providers.py`
  layer is built for that).
- Free apps go to sleep after a period without visitors. The first visit afterward
  shows a "wake up" button and takes about 30 seconds.
- The app never places orders and holds no credentials, so there are no secrets to configure.

## Alternatives

Hugging Face Spaces (Streamlit SDK) or Render also work with the same repository.
Both need the start command
`streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.
