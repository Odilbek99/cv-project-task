from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
import json 
from tqdm import tqdm
import os
from selenium.webdriver.chrome.options import Options

class RalphLaurenScraper:
    def __init__(self, url):
        self.url = url
        self.ajax_urls = []
        self.product_details = {}

    def get_request_links(self):

        """
        This method uses Selenium webdriver to scrape the page at `self.url` for 
        the number of products and returns the links to access all of the products.
        """

        driver = webdriver.Chrome()
        driver.get(self.url)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Get the count of products and compute the total number of links to be created
        products_count = soup.find("div", {"class": "results-hits"}).text.strip().split('\n')[-1].split(' ')[-2]
        n_products = (int(products_count)//32) * 32 + 1
        for i in tqdm(range(0,n_products,32)):
            self.ajax_urls.append(f'{self.url}&start={i}&sz=32')
        driver.close()
    
    def get_product_details(self):

        """
        This method uses Selenium webdriver to scrape all of the ajax urls 
        in `self.ajax_urls` and returns a dictionary of all of the product details.
        """

        urls = self.ajax_urls
        driver = webdriver.Firefox()
        # driver.implicitly_wait(10)
        wait = WebDriverWait(driver, 20)
        for url in urls:
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            parent = soup.find_all("div", {"class": "product-tile"})
            c = 0
            for child in tqdm(parent):
                product_name = child.find("a", {"class": "name-link"}).text.strip()
                brand_name = child.find("div", {"class": "brand-name"}).text.strip()
                weared_image = child.find("source", {"class": 'rlc-image-src-desktop'}).get('srcset')
                not_weared_image = child.find("img", {"class": ["rlc-image", "rlc-plp-image", "default-img", "rlc-imgLoaded"]}).get('src')
                if brand_name == 'Polo Ralph Lauren':
                    self.product_details[product_name] = {
                        'product_name': product_name,
                        'brand_name': brand_name,
                        'weared_image': weared_image,
                        'not_weared_image': not_weared_image,
                    }
        driver.close()


    def export_json(self):

        """
        This function exports the product detail links information as a JSON file.
        """

        with open('data/product_details.json', 'w') as file:
            json.dump(self.product_details, file)


    def save_images(self):

        """
        Saves the images of weared and not weared products to their respective folders.

        Args:
        product_details (dict): Dictionary containing the product information, including weared and not weared image URLs.
        """

        for key, value in tqdm(self.product_details.items()):
            weared_image = self.product_details[key]['weared_image']
            weared_image_name = self.product_details[key]['product_name'] + 'Weared'
            not_weared_image = self.product_details[key]['not_weared_image']
            not_weared_image_name = self.product_details[key]['product_name'] + 'Not-Weared'

            # Removes double quotes from image names if present
            if '"' in weared_image_name:
                weared_image_name = weared_image_name.replace('"', '')
            if '"' in not_weared_image_name:
                not_weared_image_name = not_weared_image_name.replace('"', '')

            # Checks if there is not weared image
            if weared_image != not_weared_image:

                # Writes weared image to the folder
                with open(f'data/Images/Weared/{weared_image_name}.jpg', 'wb') as im:
                    img = requests.get(weared_image)
                    im.write(img.content)

                # Writes not weared image to the folder
                with open(f'data/Images/Not Weared/{not_weared_image_name}.jpg', 'wb') as im:
                    img = requests.get(not_weared_image)
                    im.write(img.content)
        
    def run(self):
        """
        Runs the whole process of scraping and saving images.
        """
        self.get_request_links()
        self.get_product_details()
        self.export_json()
        self.save_images()

scrapper = RalphLaurenScraper('https://www.ralphlauren.nl/en/men/clothing/hoodies-sweatshirts/10204?webcat=men%7Cclothing%7Cmen-clothing-hoodies-sweatshirts')
scrapper.run()