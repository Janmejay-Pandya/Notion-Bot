# 🧭 Notion AI Agent — Smart Note & Task Creator
This project is an **AI-powered Notion Assistant** built with **LangGraph**, **Gemini (Google Generative AI)**, and the **Notion API**.  
It allows you to **create beautifully structured notes, checklists, and tables directly in Notion** — just by typing natural language prompts into a sleek React + Tailwind UI.

---

## 🚀 Overview

Imagine saying:

> "Plan a trip to Mumbai with 5–6 places to visit, each with best visiting time, formatted as checkboxes."

And instantly getting a fully formatted Notion note like:

- ✅ Interactive checkboxes for each place  
- 🏷️ Headings & sub-sections  
- 📅 Tables summarizing times  
- ✍️ Properly formatted paragraphs  

This app acts as your **personal AI-driven Notion content creator**, letting you manage travel plans, meeting summaries, to-do lists, or project notes — all hands-free.

---

## 🧩 Tech Stack

| Layer | Tech |
|-------|------|
| **Frontend** | React + Tailwind CSS |
| **Backend** | FastAPI (Python) |
| **AI Engine** | Gemini (via `langchain-google-genai`) |
| **Workflow Orchestration** | LangGraph |
| **Database / Notes** | Notion API |
| **Environment** | Python 3.10+ / Node 18+ |

---

## ⚙️ Features

✅ Create structured notes in Notion using natural language  
✅ Automatically formats:
- Headings (`#`, `##`)
- Checkboxes (`- [ ] Task`)
- Tables (`| col1 | col2 |`)
✅ Supports markdown → native Notion block conversion  
✅ React + Tailwind frontend for user prompts  
✅ FastAPI backend integrated with LangGraph  
✅ Secure `.env`-based credential management  

---
