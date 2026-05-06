import os
import requests
from bs4 import BeautifulSoup

def download_images(query, num_docs=3):
    url = f"https://portal.prizepapers.de/search/-/{query}/1/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = soup.find_all('a', href=True)
    doc_links = list(set([l['href'] for l in links if '/document/prizepapers_document_' in l['href']]))

    os.makedirs('downloaded_images', exist_ok=True)

    print(f"Found {len(doc_links)} documents for query '{query}'")

    count = 0
    for doc_url in doc_links[:num_docs]:
        print(f"Fetching {doc_url}...")
        doc_resp = requests.get(doc_url)
        doc_soup = BeautifulSoup(doc_resp.text, 'html.parser')

        images = doc_soup.find_all('img')
        for img in images:
            if 'src' in img.attrs and '/api/v1/records/' in img['src']:
                img_url = img['src']
                if img_url.startswith('/'):
                    img_url = "https://portal.prizepapers.de" + img_url

                print(f"Downloading image: {img_url}")
                img_data = requests.get(img_url).content
                img_name = f"downloaded_images/doc_{count}_{img_url.split('/')[-1]}"
                with open(img_name, 'wb') as f:
                    f.write(img_data)
                count += 1
                break # Just get the first image per doc for the sample

download_images("Baltic")
download_images("timber")
download_images("hemp")
