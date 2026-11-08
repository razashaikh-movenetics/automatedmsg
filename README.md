# Automated Personalized Outreach Mailer

An automated, intelligent outreach pipeline powered by **DeepSeek LLM** and **SMTP** that takes a prospective client's requirements/goals ("what the receiver wants") and their email address, crafts a high-converting, personalized cold email pitch matching your available product/service, and dispatches it directly from `raza.shaikh@moveneticsdigital.com`.

---

## 🚀 Features

- **Interactive Terminal Workflow**: Step-by-step interactive CLI prompting for:
  1. Your available product/service
  2. Receiver's email address
  3. Receiver's name / company
  4. What the receiver wants / needs / their specific pain points
  5. Pitch tone selection (Consultative, Executive, Friendly, ROI-focused)
- **DeepSeek LLM Integration**: Uses `deepseek-chat` via DeepSeek's OpenAI-compatible API to craft personalized, authentic pitches with high-converting subject lines and clear calls-to-action (CTAs).
- **Direct SMTP Dispatch**: Sends multipart emails (both Plain Text and clean HTML) directly via SMTP with TLS/SSL encryption.
- **Preview & Control**: Inspect the generated email subject and body in the terminal before sending, with options to **Send Now**, **Regenerate**, **Edit Manually**, or perform a **Dry Run**.
- **Audit & History Log**: Automatically records every sent/simulated email in `sent_history.json` with timestamp and status.
- **Fast CLI Mode**: Supports single-line command flags for non-interactive scripting.

---

## ⚙️ Configuration (`.env`)

Edit `/Users/razashaikh/Desktop/automatedmsg/.env`:

```env
# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# SMTP Mail Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=raza.shaikh@moveneticsdigital.com
SMTP_PASSWORD=your_email_or_app_password_here
SMTP_USE_TLS=true
SMTP_USE_SSL=false

# Sender Identity
SENDER_NAME=Raza Shaikh
SENDER_EMAIL=raza.shaikh@moveneticsdigital.com
SENDER_COMPANY=Movenetics Digital
SENDER_TITLE=Founder / Solutions Lead
```

### 🔑 Note on Google Workspace / Gmail SMTP Password:
If your email (`raza.shaikh@moveneticsdigital.com`) is hosted on Google Workspace:
1. Ensure 2-Step Verification is active on your Google Account.
2. Go to: **Google Account > Security > 2-Step Verification > App Passwords**.
3. Create a new App Password named `Antigravity Outreach`.
4. Copy the generated 16-character password into `SMTP_PASSWORD` in `.env`.

*(If using Microsoft 365 or Zoho Mail, set `SMTP_HOST=smtp.office365.com` or `smtppro.zoho.com` accordingly.)*

---

## 💻 How to Run

### 1. Interactive Terminal Mode (Recommended)
Simply run:

```bash
python3 main.py
```

The terminal will guide you through entering the receiver's details, generate the pitch with DeepSeek, preview the email, and let you send or dry-run it on the spot.

### 2. Direct CLI Mode (Single Command)

Test without sending (`--dry-run`):
```bash
python3 main.py \
  --to "client@company.com" \
  --name "Sarah Jenkins" \
  --wants "Need an automated lead pipeline that scrapes prospects and drafts emails" \
  --product "Movenetics AI Sales Automation Engine" \
  --dry-run \
  --send
```

Send directly via SMTP (`--send`):
```bash
python3 main.py \
  --to "client@company.com" \
  --name "Sarah Jenkins" \
  --wants "Need an automated lead pipeline that scrapes prospects and drafts emails" \
  --product "Movenetics AI Sales Automation Engine" \
  --send
```

---

## 📁 Project Structure

```
automatedmsg/
├── .env                  # Configuration file (DeepSeek key & SMTP credentials)
├── .env.example          # Template configuration
├── config.py             # Settings loader and validator
├── deepseek_mailer.py    # DeepSeek prompt engine & email generator
├── smtp_sender.py        # SMTP email delivery engine & audit logger
├── main.py               # Interactive CLI & terminal interface
├── sent_history.json     # Delivery audit log (auto-generated)
└── README.md             # Documentation
```

