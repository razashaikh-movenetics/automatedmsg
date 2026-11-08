# Movenetics Website & UI/UX Analyzer

A terminal tool that takes any website link as input, audits the website for real UI/UX and structural flaws with **strict rules** (if no errors, it shows no errors), identifies high-impact features that can be added, and directly prints ready-to-use outreach drafts (**msg:** and **mail:**) for **Movenetics**.

---

## 🚀 How to Run

Navigate to the directory:
```bash
cd /Users/razashaikh/Desktop/automatedmsg/webanalyzer
```

### 1. Interactive Mode (Paste Link directly in terminal)
Simply run:
```bash
python3 main.py
```
You will be prompted:
```
Paste Link: https://example.com
```

### 2. Single-Command Mode
Pass the URL directly:
```bash
python3 main.py https://example.com
```
or
```bash
python3 main.py --url https://xoompark.co
```

---

## 📋 What It Outputs in Terminal

1. **Website Overview**: Title, domain, mobile viewport presence, heading structure, CTAs found, chat widgets.
2. **UI/UX Audit (Strict Rules)**:
   - If real errors exist: Lists each issue with Severity, Impact, and how Movenetics can fix it.
   - If no errors exist: Shows `[✓] No significant UI/UX errors detected.` (does not fabricate fake errors).
3. **Features Movenetics Can Add**: 2-3 modern, high-value feature recommendations tailored to the business.
4. **`msg:`**: A concise, punchy DM (under 90 words) for LinkedIn/WhatsApp/DM.
5. **`mail:`**: A personalized cold email pitch with Subject and Body ready to send.

