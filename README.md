 # FinPulse(https://stockanalysisbymanishkumar.streamlit.app/):
 # 📊 FinPulse – AI-Powered Stock Analysis Assistant

FinPulse is an intelligent stock analysis assistant that combines **real-time financial data**, **Twitter sentiment**, and **AI-driven natural language insights** to answer investment questions like:

> 🗨️ “Should I buy TSLA?”

Built using **Streamlit**, **LangChain**, **Ollama (Mistral)**, and **yFinance**, FinPulse helps investors make more informed decisions by turning complex data into actionable insights.

---

## 🚀 Features

- 🔍 **Natural Language Q&A** — Ask questions like “What’s the outlook for NVDA?”
- 📈 **Live Market Data** — Fetches stock prices using `yfinance`
- 🐦 **Social Sentiment Analysis** — Extracts latest tweets to assess public mood
- 🧠 **LLM-Powered Reasoning** — Uses Mistral via Ollama + LangChain agents
- 🗺️ **Tool Chaining via LangGraph** — Dynamically routes queries through the right tools
- ⚡️ **Lightweight UI** — Built with Streamlit for fast and clean deployment

---

## 🛠️ Tech Stack

| Component       | Description                         |
|----------------|-------------------------------------|
| **Streamlit**   | Frontend UI for user interaction    |
| **yFinance**    | Stock data API                      |
| **Tweepy**      | Twitter API integration (via scraping/API) |
| **LangChain**   | LLM agents, prompt templates        |
| **LangGraph**   | Orchestrates tool usage dynamically |
| **Ollama + Mistral** | Runs open-source LLM locally      |
| **Python**      | Glue logic and tool chaining        |

---

## 📷 Demo

![Demo](https://github.com/AniEE107/FinPulse/blob/main/Stock.png)
