# TLDR-Browser: Gemini Web Summarizer

A lightweight, local AI Engineering pipeline that extracts plain text from any website URL, sanitizes the data stream, and uses Google's Gemini LLM to generate a short, snarky, and humorous summary. Built completely from scratch as a foundational project in LLM Engineering.

---

## 🚀 Features
* **Custom Web Scraper:** Built with `Requests` and `BeautifulSoup4` to download HTML and systematically decompose non-text assets (`<script>`, `<style>`, images, inputs).
* **Token Optimization:** Automatically clamps the inbound web data stream to a 2,000-character safety window.
* **Gemini Integration:** Communicates via the modern official `google-genai` SDK to feed system architecture instructions and user context to the `gemini-2.5-flash` model.
* **Elegant Notebook UI:** Uses IPython display utilities to dynamically render live Markdown responses from the AI directly into your workspace.

---

## 🛠️ Architecture Workflow

1. **User Input:** A URL is passed to the execution function.
2. **Ingestion & Parsing:** The local engine downloads raw HTML and strips out layout noise.
3. **Prompt Engineering:** The clean text is compiled with specific system instructions defining the AI's persona.
4. **Inference:** The data payload is sent across the Google GenAI API client.
5. **UI Rendering:** The structured response is rendered as stylized Markdown.

---

## 💻 Tech Stack
* **Language:** Python 3.11+
* **LLM Engine:** Google Gemini (`gemini-2.5-flash`)
* **Libraries:** `google-genai`, `beautifulsoup4`, `requests`, `python-dotenv`
* **Environment:** Jupyter Notebook / Cursor IDE

---

## ⚙️ Installation & Setup

1. **Clone the project directory** and navigate to your workspace.

2. **Configure Environment Variables:**
   Create a hidden text file named `.env` in the root directory and append your official Gemini developer API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
