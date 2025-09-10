import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://www.apiit.lk"
visited = set()

def get_all_links(base_url):
    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = set()

        for a_tag in soup.find_all("a", href=True):
            full_url = urljoin(base_url, a_tag['href'])
            if full_url.startswith(base_url):
                links.add(full_url)
        return links
    except:
        return set()

all_links = get_all_links(url)

for link in all_links:
    print(link)

print(len(all_links))
