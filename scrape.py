from config import HEADERS, INFO_BOX_XPATH, TEST_URL, SEARCH_URL, BASE_URL
import requests
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
from math import ceil

class WebsiteScraper():
    """ Extract all the required data from SpareRoom. """

    def __init__(self):
        self.session = HTMLSession()
        self.headers = HEADERS
        self.info_box_xpath = INFO_BOX_XPATH
        self.search_url = SEARCH_URL
        self.base_url = BASE_URL
        self.testurl = TEST_URL

    def get_source(self, url):
        """ Return the source code for the given URL. """
        try:
            response = self.session.get(url, headers=self.headers)
            return response
        except requests.exceptions.RequestException as e:
            print(e)

    def extract_listings(self):
        response = self.get_source(self.search_url)
        num_listings = int(response.html.xpath('//*[@id="maincontent"]/div[2]/p/strong[2]')[0].text.split(' ')[0])
        num_search_pages = ceil(num_listings/10)

        search_urls = [self.search_url.replace('offset=0', 'offset={}'.format(page*10)) for page in range(num_search_pages)]
        search_responses = [self.get_source(url) for url in search_urls]

        listing_links = [response.html.xpath('//*[@id="maincontent"]/ul/li[{}]/article/header[1]/a/@href'.format(i)) for response in search_responses for i in range(1,12)]
        listing_links = [(self.base_url + link) for list in listing_links for link in list]

        return listing_links

    def get_info_box_element(self, response, element_path):
        try:
            info = response.html.xpath(self.info_box_xpath + element_path)[0].text.split('\n')[0]
            return info
        except:
            return None

    def extract_listing_data(self, url):
        """
        Scrapes the desired data from a given room listing.

        Returns: Dictionary of the room's details.

        """

        response = self.get_source(url)

        ad_ref = response.html.xpath('//*[@id="listing_ref"]/span/text()')[0]

        house_type = self.get_info_box_element(response, 'section[1]/ul/li[1]')
        area = self.get_info_box_element(response, 'section[1]/ul/li[2]')
        postcode = self.get_info_box_element(response, 'section[1]/ul/li[3]')
        price = self.get_info_box_element(response, '/section[2]/ul/li/strong')
        available = self.get_info_box_element(response, 'section[4]/dl/dd[1]')
        min_term = self.get_info_box_element(response, 'section[4]/dl/dd[2]')
        max_term = self.get_info_box_element(response, 'section[4]/dl/dd[3]')
        deposit = self.get_info_box_element(response, 'section[5]/dl/dd[1]')
        bills = self.get_info_box_element(response, 'section[5]/dl/dd[2]')
        furnished = self.get_info_box_element(response, 'section[6]/dl/dd[1]')
        balcony = self.get_info_box_element(response, 'section[6]/dl/dd[2]')
        disabled_access = self.get_info_box_element(response, 'section[6]/dl/dd[3]')
        living_room = self.get_info_box_element(response, 'section[6]/dl/dd[4]')
        broadband = self.get_info_box_element(response, 'section[6]/dl/dd[5]')
        num_flatmates = self.get_info_box_element(response, 'section[7]/dl/dd[1]')

        variables = dir()
        variables.remove('response')
        variables.remove('self')
        d = {}
        for v in variables:
            d[v] = eval(v)

        return d

    def get_data(self):

        #add control to change the number of pages found in extract_listings
        listing_links = self.extract_listings()[0:20]
        data = [self.extract_listing_data(url) for url in listing_links]
        df = pd.DataFrame(data)

        return df
