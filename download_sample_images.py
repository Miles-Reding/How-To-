import os
import requests
from bs4 import BeautifulSoup
import argparse
import time

def fetch_doc_links(query, max_documents):
    doc_links = set()
    page = 1

    print(f"Searching Prize Papers for query: '{query}'")
    while len(doc_links) < max_documents:
        url = f"https://portal.prizepapers.de/search/-/{query}/{page}/"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error fetching page {page}. Status: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        new_links = [l['href'] for l in links if '/document/prizepapers_document_' in l['href']]

        if not new_links:
            print(f"No more results found on page {page}.")
            break

        for link in new_links:
            doc_links.add(link)
            if len(doc_links) >= max_documents:
                break

        print(f"Page {page} processed. Found {len(doc_links)} unique document links so far...")
        page += 1
        time.sleep(0.5) # Polite scraping

    return list(doc_links)

def download_images(doc_links, output_dir="downloaded_images"):
    os.makedirs(output_dir, exist_ok=True)

    downloaded_paths = []

    for i, doc_url in enumerate(doc_links):
        print(f"[{i+1}/{len(doc_links)}] Fetching {doc_url}...")
        try:
            doc_resp = requests.get(doc_url)
            doc_soup = BeautifulSoup(doc_resp.text, 'html.parser')

            # The viewer uses an API endpoint for images
            images = doc_soup.find_all('img')
            for img in images:
                if 'src' in img.attrs and '/api/v1/records/' in img['src']:
                    img_url = img['src']
                    if img_url.startswith('/'):
                        img_url = "https://portal.prizepapers.de" + img_url

                    print(f"  Downloading image: {img_url}")
                    img_data = requests.get(img_url).content

                    doc_id = doc_url.split('/')[-2] if doc_url.endswith('/') else doc_url.split('/')[-1]
                    img_name = f"{output_dir}/{doc_id}.jpg"

                    with open(img_name, 'wb') as f:
                        f.write(img_data)
                    downloaded_paths.append(img_name)
                    break # Get the main image
        except Exception as e:
            print(f"  Error processing {doc_url}: {e}")

    return downloaded_paths

def main():
    parser = argparse.ArgumentParser(description="Scrape Prize Papers portal with pagination and limits.")
    parser.add_argument('--query', type=str, default="Baltic AND (timber OR tar OR pitch OR hemp)", help="Search query")
    parser.add_argument('--max_docs', type=int, default=5, help="Maximum number of documents to fetch (respects API limits)")
    parser.add_argument('--out_dir', type=str, default="downloaded_images", help="Output directory")

    args = parser.parse_args()

    links = fetch_doc_links(args.query, args.max_docs)
    print(f"\nTotal documents to process: {len(links)}")
    download_images(links, args.out_dir)

if __name__ == "__main__":
    main()
