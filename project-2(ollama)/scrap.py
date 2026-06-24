from bs4 import BeautifulSoup
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def fetch_website_content(url):
    response = requests.get(url,headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.title.string if soup.title else 'No title found'

    if soup.body:
        for irrelevant_tag in soup.body(['script', 'style','image','input']):
            irrelevant_tag.decompose()

        text = soup.body.get_text(separator=' ', strip=True)
    else:
        text = 'No body content found'
    
    return (title + '\n\n' + text)[:2000]

