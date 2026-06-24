# Project Overview

This project is a website summarizer powered by a local LLM workflow. It fetches content from a URL, sends the extracted text to an Ollama-hosted model through the OpenAI-compatible API, and returns a concise summary with the main points.

## What it does

- Fetches website content from a given URL.
- Uses a system prompt to guide the model toward short, useful summaries.
- Summarizes webpages in a readable format.
- Displays the result directly in a notebook using Markdown.

## How it works

1. A website URL is passed to `summarize_website()`.
2. The project calls `fetch_website_content(url)` from `scrap.py` to collect page text.
3. The content is combined with a prompt that asks for a short summary.
4. The prompt is sent to a local Ollama model using the OpenAI client.
5. The response is displayed with `display_summary(url)`.

## Main technologies

- Python
- OpenAI Python client
- Ollama
- IPython / Jupyter Notebook
- Website scraping helper module

## Example usage

The notebook shows examples for:

- `https://time.is/`
- `https://www.thehindu.com/`

## Project goal

The goal of this project is to quickly summarize website content without relying on a remote hosted LLM, while keeping the workflow simple and notebook-friendly.

## Notes

- The model used in the notebook is `llama3.2:latest`.
- The OpenAI client is configured to talk to Ollama at `http://localhost:11434/v1/`.
- The project assumes the local Ollama server is running before executing the notebook.
