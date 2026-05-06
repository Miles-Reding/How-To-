import requests
from bs4 import BeautifulSoup
import json

url = "https://portal.prizepapers.de/search/-/(timber OR tar OR pitch OR hemp)/1/"
response = requests.get(url)
print("Status:", response.status_code)
soup = BeautifulSoup(response.text, 'html.parser')

items = soup.find_all('div', class_='box-element') # Goobi viewer often uses specific classes
if not items:
    # Try just grabbing some links
    links = soup.find_all('a', href=True)
    doc_links = [l['href'] for l in links if '/document/' in l['href']]
    print("Found doc links:", len(set(doc_links)))
    print(list(set(doc_links))[:5])
else:
    print("Found box elements:", len(items))
