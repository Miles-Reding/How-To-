import requests
from bs4 import BeautifulSoup

doc_url = "https://portal.prizepapers.de/document/prizepapers_document_ddb18f88-bcf7-4699-9aac-2155ba2102b1/"
response = requests.get(doc_url)
print("Status:", response.status_code)
soup = BeautifulSoup(response.text, 'html.parser')

images = soup.find_all('img')
img_urls = [img['src'] for img in images if 'src' in img.attrs]
print(img_urls[:5])
