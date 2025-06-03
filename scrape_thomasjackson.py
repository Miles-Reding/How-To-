import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate
import time

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

SITEMAP_INDEX = 'https://thomasjacksonletters.com/sitemap_index.xml'
DOCUMENT_EXTS = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx']


def get_sitemaps(index_url=SITEMAP_INDEX):
    resp = requests.get(index_url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'xml')
    return [loc.text for loc in soup.find_all('loc')]


def parse_sitemap(url):
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'xml')
    for url_tag in soup.find_all('url'):
        loc = url_tag.loc.text
        lastmod_tag = url_tag.find('lastmod')
        lastmod = lastmod_tag.text if lastmod_tag else ''
        yield loc, lastmod


def scrape_page(url):
    try:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
    except requests.RequestException:
        return url, '', ''
    soup = BeautifulSoup(resp.text, 'html.parser')
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else url
    p_tag = soup.find('p')
    summary = p_tag.get_text(strip=True) if p_tag else ''
    doc_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if any(href.lower().endswith(ext) for ext in DOCUMENT_EXTS):
            if href.startswith('/'):
                href = 'https://thomasjacksonletters.com' + href
            doc_links.append(href)
    for img in soup.find_all('img', src=True):
        src = img['src']
        if any(src.lower().endswith(ext) for ext in DOCUMENT_EXTS):
            if src.startswith('/'):
                src = 'https://thomasjacksonletters.com' + src
            if src not in doc_links:
                doc_links.append(src)
    return title, summary, '; '.join(doc_links)


def main():
    sitemaps = get_sitemaps()
    entries = []
    for sitemap in sitemaps:
        for url, lastmod in parse_sitemap(sitemap):
            title, summary, docs = scrape_page(url)
            entries.append({'Title': title, 'URL': url, 'Last Modified': lastmod, 'Docs': docs, 'Summary': summary})
            time.sleep(0.5)
    df = pd.DataFrame(entries)
    print(tabulate(df, headers='keys', tablefmt='github', showindex=False))


if __name__ == '__main__':
    main()
