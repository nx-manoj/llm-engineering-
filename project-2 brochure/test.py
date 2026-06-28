import os 
import json 
import re
import time
from openai import OpenAI
from dotenv import load_dotenv
from IPython.display import display, Markdown,update_display
from scrap import fetch_website_contents, fetch_website_links
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown as RichMarkdown

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")


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

def get_links_user_prompt(url):
    user_prompt = f"""
You are provided with a list of links found on the webpage at {url}.
Please identify which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
Do not include any links that are not relevant to a company brochure.
And also don't include terms or service, privacy policy, or any other legal pages and email links.
""" 
    links = fetch_website_links(url)
    user_prompt += "\n\nHere are the links found on the webpage:\n"
    for link in links:
        user_prompt += f"- {link}\n"
    return user_prompt

def select_relevant_links(url):
    print(f"Fetching relevant links from: {url}")
    client = OpenAI(base_url="http://localhost:11434/v1/" ,api_key='ollama')
    user_prompt = get_links_user_prompt(url)
    response = client.chat.completions.create(
        model="llama3.2-8k",
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    result =  response.choices[0].message.content
    if not result:
        raise ValueError("The model returned an empty response instead of JSON.")

    match = re.search(r"\{.*\}", result, re.DOTALL)
    if match:
        result = match.group(0)

    links = json.loads(result)
    print(f"Relevant links found: {len(links['links'])}")
    return links


def fetch_all_page_and_relevant_links(url):
    page_content = fetch_website_contents(url)
    relevant_links = select_relevant_links(url)
    result = f'## Landing Page Content\n\n{page_content}\n\n## Relevant Links\n\n'
    for link in relevant_links['links']:
        result += f"- [{link['type']}]({link['url']})\n"
    return result


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

def get_brochure_user_prompt(company_name, url):
    user_prompt = f"""
    You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages;
use this information to build a short brochure of the company in markdown without code blocks.\n\n
"""
    
    user_prompt += fetch_all_page_and_relevant_links(url)
    user_prompt = user_prompt[:5000]
    return user_prompt


def create_brochure(company_name, url):
    client = OpenAI(base_url="http://localhost:11434/v1/", api_key='ollama')
    user_prompt = get_brochure_user_prompt(company_name, url)
    response = client.chat.completions.create(
        model="llama3.2-8k",
        messages=[
            {"role": "system", "content": brochure_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    brochure_content = response.choices[0].message.content
    console = Console()
    console.print(RichMarkdown(brochure_content))

##created with AI
def stream_brochure(company_name, url):
    client = OpenAI(base_url="http://localhost:11434/v1/", api_key='ollama')
    user_prompt = get_brochure_user_prompt(company_name, url)
    stream = client.chat.completions.create(
        model="llama3.2-8k",
        messages=[
            {"role": "system", "content": brochure_system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True
    )
    console = Console()
    brochure_content = ""

    print("Streaming raw generation...[Local model has bugs while streaming so not printing delta. If anyone knows the fix then please let me know]")
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if not delta:
            continue
        brochure_content += delta


    print("\n\n--- Final Rendered Brochure ---")
    console.print(RichMarkdown(brochure_content))

    return brochure_content

if __name__ == '__main__':
    stream_brochure('OpenAI', 'https://openai.com')

