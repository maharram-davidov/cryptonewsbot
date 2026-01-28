# 🤖 Crypto News Monitoring & Analysis Bot

**Crypto News Bot** is an event-driven Telegram bot designed to collect, analyze, and summarize cryptocurrency-related news in real time. The system combines RSS-based data ingestion with AI-assisted analysis to provide timely market insights and daily summaries.

---

## 🎯 Project Objectives

* **Real-time Monitoring:** Track major cryptocurrency news sources 24/7.
* **AI Insights:** Provide concise AI-assisted analysis for every news item.
* **Automation:** Generate daily market summaries automatically.
* **Personalization:** Configurable notification preferences for every user.
* **Stability:** Lightweight architecture designed for continuous operation.

---

## 🧠 Core Features

### 🔹 Real-Time News Monitoring

* **RSS Ingestion:** Data from major crypto news outlets.
* **Smart Polling:** Periodic checks (default: 90s) to ensure zero latency.
* **Deduplication:** Advanced caching to prevent duplicate alerts.

### 🔹 AI-Assisted News Analysis

* **Engine:** Powered by **Google Gemini**.
* **Classification:** Market impact (Bullish / Bearish / Neutral).
* **Risk Assessment:** Risk level estimation (Low / Medium / High).
* **Summarization:** Short, human-readable insights.

### 🔹 Daily AI Market Summary

* **Aggregation:** Summarizes the most relevant news from the last 24 hours.
* **Sentiment Tracking:** Overall market sentiment estimation.
* **Admin Control:** Manual trigger option for on-demand summaries.

### 🔹 User Preference Management

* Inline button-based configuration (`/settings`).
* Persistent storage for notification toggles (Instant alerts vs. Daily summaries).

---

## 🏗️ System Architecture

The bot follows a modular and event-driven design:

```text
CryptoNewsBot/
├── main.py               # Application entry point
├── telegram_bot.py       # Async Telegram bot (PTB v20.x)
├── news_fetcher.py       # RSS ingestion and parsing
├── ai_analyzer.py        # AI-based analysis module
├── config.py             # Configuration and parameters
├── test_bot.py           # Component-level testing
└── storage/              # JSON-based persistence (User data & Cache)

```

### Key Technical Highlights:

* **Separation of Concerns:** Clear boundaries between fetching, analysis, and delivery.
* **Stateless Processing:** Message processing is stateless while maintaining persistent user configurations.
* **Rate-Limit Friendly:** RSS-based ingestion avoids heavy API costs or limitations.

---

## ⚙️ Technologies Used

| Technology | Purpose |
| --- | --- |
| **Python** | Core programming language |
| **python-telegram-bot** | Async bot framework (v20.x) |
| **Google Gemini API** | AI-driven sentiment & risk analysis |
| **Feedparser** | RSS news ingestion |
| **APScheduler** | Scheduled jobs and automation |
| **JSON Storage** | Lightweight persistence |

---

## 🚀 Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/maharram-davidov/cryptonews-tgbot.git
cd cryptonews-tgbot

```


2. **Create and activate virtual environment**
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

```


3. **Install dependencies**
```bash
pip install -r requirements.txt

```


4. **Configure environment variables**
Create a `.env` file based on `env_example.txt`:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
ADMIN_USER_IDS=123456789

```


5. **Run the bot**
```bash
python main.py

```



---

## 📋 Bot Commands

| User Command | Description |
| --- | --- |
| `/start` | Initialize the bot |
| `/subscribe` | Enable news notifications |
| `/unsubscribe` | Disable notifications |
| `/settings` | Manage notification preferences |
| `/latest` | Fetch the most recent news |
| `/help` | Detailed usage instructions |

**Admin Commands:**

* `/daily_summary`: Trigger daily summary manually.
* `/reset_news`: Clear news cache for debugging.

---

## 📊 News Sources

The bot currently monitors high-authority sources via RSS:

* CoinDesk
* The Block
* Crypto News
* NewsBTC

---

## 🎓 Academic Relevance

This project is an excellent demonstration of:

1. **Applied AI:** Real-world implementation of LLMs in financial news.
2. **Software Architecture:** Practical application of event-driven and modular design.
3. **Data Pipelines:** Real-time data ingestion and processing workflows.
4. **User Experience:** Implementing stateful interactions in a stateless bot environment.

---

## 📄 License

This project is released under the **MIT License**.

---
