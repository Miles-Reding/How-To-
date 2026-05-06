import os
import requests
from bs4 import BeautifulSoup
import argparse
import time

def fetch_doc_links(query, max_documents, fetch_all):
    doc_links = set()
    page = 1

    print(f"Searching Prize Papers for query: '{query}'")
    while True:
        if not fetch_all and len(doc_links) >= max_documents:
            break

        url = f"https://portal.prizepapers.de/search/-/{query}/{page}/"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error fetching page {page}. Status: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        new_links = [l['href'] for l in links if '/document/prizepapers_document_' in l['href']]

        if not new_links:
            print(f"No more results found on page {page}. End of search results.")
            break

        added_on_page = 0
        for link in new_links:
            if link not in doc_links:
                doc_links.add(link)
                added_on_page += 1
                if not fetch_all and len(doc_links) >= max_documents:
                    break

        # If we didn't add any new links and we are paginating deeply, we might be looping or stuck.
        # But Goobi viewer often has consistent page sizes. Let's just monitor.
        print(f"Page {page} processed. Found {len(doc_links)} unique document links so far...")
        page += 1
        time.sleep(0.5) # Polite scraping

    return list(doc_links)

def download_images(doc_links, output_dir="downloaded_images"):
    os.makedirs(output_dir, exist_ok=True)

    downloaded_paths = []

    for i, doc_url in enumerate(doc_links):
        doc_id = doc_url.split('/')[-2] if doc_url.endswith('/') else doc_url.split('/')[-1]
        img_name = f"{output_dir}/{doc_id}.jpg"

        # Skip if already downloaded (allows resume)
        if os.path.exists(img_name):
            print(f"[{i+1}/{len(doc_links)}] Already downloaded: {img_name}")
            downloaded_paths.append(img_name)
            continue

        print(f"[{i+1}/{len(doc_links)}] Fetching {doc_url}...")
        try:
            doc_resp = requests.get(doc_url)
            doc_soup = BeautifulSoup(doc_resp.text, 'html.parser')

            images = doc_soup.find_all('img')
            for img in images:
                if 'src' in img.attrs and '/api/v1/records/' in img['src']:
                    img_url = img['src']
                    if img_url.startswith('/'):
                        img_url = "https://portal.prizepapers.de" + img_url

                    print(f"  Downloading image: {img_url}")
                    img_data = requests.get(img_url).content

                    with open(img_name, 'wb') as f:
                        f.write(img_data)
                    downloaded_paths.append(img_name)
                    time.sleep(0.5) # Polite scraping
                    break # Get the main image
        except Exception as e:
            print(f"  Error processing {doc_url}: {e}")

    return downloaded_paths

def main():
    parser = argparse.ArgumentParser(description="Scrape Prize Papers portal.")
    parser.add_argument('--query', type=str, default="Baltic AND (timber OR tar OR pitch OR hemp)", help="Search query")
    parser.add_argument('--max_docs', type=int, default=5, help="Maximum number of documents to fetch")
    parser.add_argument('--all', action='store_true', help="Fetch ALL available documents for the query (ignores max_docs)")
    parser.add_argument('--out_dir', type=str, default="downloaded_images", help="Output directory")

    args = parser.parse_args()

    if args.all:
        print("WARNING: --all flag provided. This will scrape the entire database for this query and may take hours.")

    links = fetch_doc_links(args.query, args.max_docs, args.all)
    print(f"\nTotal documents to process: {len(links)}")
    download_images(links, args.out_dir)

if __name__ == "__main__":
    main()
