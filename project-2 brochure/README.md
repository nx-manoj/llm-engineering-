# AI Brochure Generator (Project 2)

An interactive, premium web application that automatically generates comprehensive business brochures from any company's website URL. The pipeline crawls the homepage, evaluates subpages to determine relevance using AI, scrapes their contents, and synthesizes a high-quality brochure in Markdown and PDF formats.

---

## 🌟 Key Features

*   **Intelligent Crawler**: Automatically extracts webpage text contents and discoverable anchor links.
*   **Dual LLM Provider Support**:
    *   **Ollama (Local)**: Runs completely offline using your local `llama3.2-8k` model.
    *   **Google Gemini (Cloud)**: Integrates with Gemini 2.5 Flash and Pro models (indicated as Coming Soon on the UI).
*   **Real-time SSE Streaming**: Streams the synthesized brochure text chunk-by-chunk to the UI as it's being generated.
*   **Interactive Terminal Console**: Shows live crawler logs and step-by-step progress checklists as the pipeline runs.
*   **Aura UI (AI-Assisted Frontend)**:
    *   *Design*: Sleek, glassmorphic dark-theme dashboard with custom neon indigo-to-purple accents.
    *   *Theme*: Built-in glowing light/dark mode switch.
    *   *Multi-Tab Workspace*: View rendered HTML (compiled via `marked.js`), raw Markdown source, and Page crawling insights.
    *   *Exports*: One-click copy, Markdown file download, and custom styled **PDF Export** (optimized with a clean white paper print layout).

> [!NOTE]
> **AI Development Note**: The interactive web frontend client (`templates/index.html` and style components) and its SSE integration with the Flask server were fully developed with the assistance of an AI coding agent (**Antigravity** by Google DeepMind).

---

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.8 or higher installed.
*   [Ollama](https://ollama.com) installed and running locally with the Llama 3.2 model.

### 1. Setup Ollama Model
Create a custom model named `llama3.2-8k` with expanded context size:
```bash
# Verify Ollama is running, then create the custom model using the Modelfile:
ollama create llama3.2-8k -f Modelfile
```

### 2. Configure Environment
Create a `.env` file in the project folder with your Gemini API key (optional):
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Launch the Server
Ensure you are in the `project-2 brochure` directory, activate the virtual environment, and run the Flask application:
```powershell
# Windows PowerShell
.\venv\Scripts\activate
python app.py
```

The application will launch on:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 📂 Project Structure

```
project-2 brochure/
├── app.py                  # Flask web server, SSE endpoints & Ollama/Gemini API handlers
├── scrap.py                # Core scraping modules (BeautifulSoup text & link parser)
├── test.py                 # Original CLI stream & Ollama connection code
├── Modelfile               # Ollama custom context configuration (num_ctx 8192)
├── README.md               # Project documentation (You are here)
├── .env                    # Local environment variables
├── .gitignore              # Git ignore rules (ignores virtual environments, cache, logs)
├── templates/
│   └── index.html          # Aura UI: HTML/JS frontend & glassmorphic print styling
└── venv/                   # Local Python virtual environment
```
