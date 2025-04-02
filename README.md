# 📊 Dashboard for Streaming Data

This project runs a Python script (`main.py`) that:

- Reads data from `athens_routes.csv`
- Processes the data
- Stores it in a **PostgreSQL** database on **Google Cloud SQL**

All of this runs **automatically every 15 minutes** using GitHub Actions.

---

## 🚀 How it works

1. `main.py` loads data from the CSV file.
2. It connects securely to Google Cloud SQL using a **Cloud SQL Proxy**.
3. The script is triggered **every 15 minutes** (cron schedule) via GitHub Actions.
4. GitHub Secrets are used to protect credentials.

---

## 🔐 GitHub Secrets

| Secret Name       | Description                          |
|-------------------|--------------------------------------|
| `API_KEY`         | External API key (if needed)         |
| `DATABASE_URL`    | Connection string to PostgreSQL      |
| `GCP_CREDENTIALS` | JSON key from Google Cloud service account |

---

## ⚙️ Technologies Used

- Python 3.10
- GitHub Actions (CI)
- Google Cloud SQL (PostgreSQL)
- Cloud SQL Proxy
- GitHub Secrets

---

## 🛡️ Security Features

- No credentials exposed in code
- `.gitignore` protects local/secret files
- Public access (`0.0.0.0/0`) removed from Cloud SQL
- Secure IAM-based access only via service account

---

## 📁 Project Files

| File                     | Description                          |
|--------------------------|--------------------------------------|
| `main.py`                | Python script that processes and saves data |
| `athens_routes.csv`      | CSV file with route data             |
| `requirements.txt`       | Python dependencies                  |
| `.github/workflows/...`  | GitHub Actions workflow              |

---

## ✍️ Author

Built by [@eleftheriosvarv](https://github.com/eleftheriosvarv)  
*Runs while you sleep 😴*
