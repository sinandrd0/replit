import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path

class WebDownloader:
    def __init__(self, base_url):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited = set()
        self.base_path = Path(self.domain)

    def download_page(self, url):
        """Download the content of a given URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return None

    def parse_html(self, html, current_url):
        """Parse HTML content and extract internal links."""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(current_url, href)
            if urlparse(full_url).netloc == self.domain:
                links.append(full_url)
        return links

    def save_content(self, url, content):
        """Save the content to a local file."""
        parsed_url = urlparse(url)
        path = parsed_url.path
        if path.endswith('/'):
            path += 'index.html'
        elif not path.endswith('.html'):
            path += '.html'

        file_path = self.base_path / path.lstrip('/')
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved: {file_path}")

    def download_recursive(self, url):
        """Recursively download pages from the given URL."""
        if url in self.visited:
            return
        self.visited.add(url)

        print(f"Downloading: {url}")
        content = self.download_page(url)
        if content is None:
            return

        self.save_content(url, content)
        links = self.parse_html(content, url)

        for link in links:
            self.download_recursive(link)

    def start_download(self):
        """Start the downloading process."""
        print(f"Starting download from: {self.base_url}")
        self.download_recursive(self.base_url)
        print("Download complete!")

if __name__ == "__main__":
    base_url = input("Enter the website URL to download: ")
    downloader = WebDownloader(base_url)
    downloader.start_download()
