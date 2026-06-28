import os
import json
import re
import time
from flask import Flask, request, Response, render_template, jsonify
from openai import OpenAI
from google import genai
from dotenv import load_dotenv
from scrap import fetch_website_contents, fetch_website_links

# Load environment variables
load_dotenv(override=True)

app = Flask(__name__)

# System prompts
link_system_prompt = """
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""

brochure_system_prompt = """
Role: You are an expert business analyst and marketing copywriter.

Analyze the provided pages from a company's website and create a polished, professional brochure in Markdown (no code blocks). Synthesize information across all pages into a single cohesive overview rather than summarizing each page individually.

Include, where available:

Company overview (mission, vision, history, location)
Products and services
Value proposition and competitive advantages
Target customers and industries served
Technology and innovation
Company culture and values
Careers, hiring, internships, and employee benefits
Key achievements, partnerships, certifications, or awards
Contact information

Use clear headings, concise paragraphs, and bullet points where appropriate. Write for prospective customers, investors, partners, and job seekers. Do not invent missing information—omit sections that are not supported by the provided content. Prioritize factual accuracy, readability, and a professional, engaging tone.
"""

def get_links_user_prompt(url, links):
    user_prompt = f"""
You are provided with a list of links found on the webpage at {url}.
Please identify which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
Do not include any links that are not relevant to a company brochure.
And also don't include terms of service, privacy policy, or any other legal pages and email links.
""" 
    user_prompt += "\n\nHere are the links found on the webpage:\n"
    for link in links:
        user_prompt += f"- {link}\n"
    return user_prompt

def select_relevant_links(url, provider, model_name, all_links):
    user_prompt = get_links_user_prompt(url, all_links)
    
    if provider == 'gemini':
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
        client = genai.Client(api_key=api_key)
        # For Gemini structured JSON output, we can specify a system instruction
        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config={
                'system_instruction': link_system_prompt,
                'response_mime_type': 'application/json'
            }
        )
        result = response.text
    else:
        # Ollama / Local OpenAI API
        client = OpenAI(base_url="http://localhost:11434/v1/", api_key='ollama')
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": link_system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        result = response.choices[0].message.content

    if not result:
        raise ValueError("The model returned an empty response instead of JSON.")

    match = re.search(r"\{.*\}", result, re.DOTALL)
    if match:
        result = match.group(0)

    try:
        links_json = json.loads(result)
        # Ensure correct structure
        if "links" not in links_json:
            links_json = {"links": []}
        return links_json
    except json.JSONDecodeError:
        # If json load fails, parse links manually or return empty
        print(f"Failed to parse JSON from: {result}")
        # Simple fallback parsing using regex
        urls = re.findall(r'"url":\s*"([^"]+)"', result)
        types = re.findall(r'"type":\s*"([^"]+)"', result)
        fallback_links = []
        for i in range(min(len(urls), len(types))):
            fallback_links.append({"type": types[i], "url": urls[i]})
        return {"links": fallback_links}

@app.route('/')
def index():
    # Render front-end
    return render_template('index.html')

@app.route('/api/status')
def status():
    # Return available configurations
    gemini_available = bool(os.getenv("GEMINI_API_KEY"))
    return jsonify({
        "gemini_available": gemini_available,
        "default_ollama_model": "llama3.2-8k",
        "default_gemini_model": "gemini-2.5-flash"
    })

@app.route('/api/generate')
def generate():
    company_name = request.args.get('company_name', 'Company')
    url = request.args.get('url')
    provider = request.args.get('provider', 'ollama')
    model_name = request.args.get('model', '')

    if not url:
        return Response("data: " + json.dumps({"error": "URL parameter is required"}) + "\n\n", mimetype="text/event-stream")

    if not model_name:
        model_name = "gemini-2.5-flash" if provider == "gemini" else "llama3.2-8k"

    def stream_events():
        # Step 1: Scrape landing page
        yield f"event: progress\ndata: {json.dumps({'message': 'Scraping landing page contents...'})}\n\n"
        try:
            page_content = fetch_website_contents(url)
            all_links = fetch_website_links(url)
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'message': f'Failed to scrape website: {str(e)}'})}\n\n"
            return

        yield f"event: progress\ndata: {json.dumps({'message': f'Extracted {len(all_links)} raw links. Selecting relevant pages using {provider}...'})}\n\n"
        
        # Step 2: Select relevant links
        try:
            relevant_links = select_relevant_links(url, provider, model_name, all_links)
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'message': f'Failed to select relevant links: {str(e)}. Attempting to proceed with landing page only.'})}\n\n"
            relevant_links = {"links": []}

        # Stream relevant links to UI
        yield f"event: links\ndata: {json.dumps(relevant_links)}\n\n"

        # Construct the user prompt for the brochure
        yield f"event: progress\ndata: {json.dumps({'message': 'Compiling research and initiating brochure generation...'})}\n\n"
        
        # Format links text for LLM context
        links_context = ""
        for link in relevant_links.get('links', []):
            links_context += f"- [{link['type']}]({link['url']})\n"

        user_prompt = f"""
You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages;
use this information to build a short brochure of the company in markdown without code blocks.

## Landing Page Content
{page_content}

## Relevant Links
{links_context}
"""
        # Limit prompt length
        user_prompt = user_prompt[:6000]

        # Step 3: Stream brochure generation
        try:
            if provider == 'gemini':
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("GEMINI_API_KEY is not set.")
                client = genai.Client(api_key=api_key)
                
                # Using generate_content_stream for streaming response
                response_stream = client.models.generate_content_stream(
                    model=model_name,
                    contents=user_prompt,
                    config={
                        'system_instruction': brochure_system_prompt
                    }
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield f"event: content\ndata: {json.dumps({'text': chunk.text})}\n\n"
            else:
                client = OpenAI(base_url="http://localhost:11434/v1/", api_key='ollama')
                response_stream = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": brochure_system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    stream=True
                )
                for chunk in response_stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        yield f"event: content\ndata: {json.dumps({'text': text})}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'message': f'Generation error: {str(e)}'})}\n\n"
            return

        yield f"event: done\ndata: {json.dumps({'message': 'Brochure generated successfully!'})}\n\n"

    return Response(stream_events(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Run server on port 5000
    app.run(debug=True, port=5000)
