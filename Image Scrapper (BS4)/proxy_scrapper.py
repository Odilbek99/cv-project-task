import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

class ProxyScraper:
    def __init__(self, proxy_url):
        self.proxy_url = proxy_url
        self.proxies = []
        self.valid_proxies = []

    def get_all_proxies(self):
        """
        Scrapes proxy list from the given URL and stores it in self.proxies.
        """
        r = requests.get(self.proxy_url)
        soup = BeautifulSoup(r.content, 'html.parser').find_all('td',{'class': 'blob-code blob-code-inner js-file-line'})
        self.proxies = [proxy.text for proxy in tqdm(soup)]

    def get_valid_proxies(self):
        """
        Filters out the invalid proxies and stores valid ones in self.valid_proxies.
        """
        for proxy in tqdm(self.proxies):
            try:
                r = requests.get("https://www.google.com", proxies={'https': proxy}, timeout=3)
                if r.status_code == 200:
                    self.valid_proxies.append(proxy)

            except:
                pass

    def save_proxies(self):
        """
        Saves the valid proxies to a file.
        """
        with open('data/proxies.txt', 'a') as file:
            for proxy in tqdm(self.valid_proxies):
                file.write(f'{proxy}\n')

    def run(self):
        """
        Runs the whole process of scraping and filtering proxies.
        """
        self.get_all_proxies()
        self.get_valid_proxies()
        self.save_proxies()

proxy_scraper = ProxyScraper(proxy_url='https://github.com/clarketm/proxy-list/blob/master/proxy-list-raw.txt')
proxy_scraper.run()

