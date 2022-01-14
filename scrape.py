from config import HEADERS, INFO_BOX_XPATH, TEST_URL, SEARCH_URL, BASE_URL, SEARCH_ID
import requests
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
from math import ceil
from preprocessing import PropertyRemover, PriceExtractor, AvailabilityTransformer, TermTransformer, AdRefExtractor, PostcodeExtractor, DepositTransformer, TimeToStationExtractor, BinaryEncoder, OrdinalEncoder, OneHotEncoder

class SpareRoomScraper():
    """ Extract all the required data from SpareRoom. """

    def __init__(self):
        self.session = HTMLSession()
        self.headers = HEADERS
        self.search_id = SEARCH_ID
        self.search_url = SEARCH_URL
        self.base_url = BASE_URL
        self.testurl = TEST_URL
        self.info_box_xpath = INFO_BOX_XPATH

    def get_source(self, url):
        """ Return the source code for the given URL. """
        try:
            response = self.session.get(url, headers=self.headers)
            return response
        except requests.exceptions.RequestException as e:
            print(e)

    def extract_listings(self, num_listings = 0):
        response = self.get_source(self.search_url)

        if num_listings == 0:
            num_listings = int(response.html.xpath('//*[@id="maincontent"]/div[2]/p/strong[2]')\
                                                                [0].text.split(' ')[0].strip('+'))
        num_search_pages = ceil(num_listings/10)

        search_urls = [self.search_url.replace('offset=0', 'offset={}'.format(page*10))
                        for page in range(num_search_pages)]
        search_responses = [self.get_source(url) for url in search_urls]

        listing_links = [response.html.xpath('//*[@id="maincontent"]/ul/li[{}]/article/header[1]/a/@href'\
                                        .format(i)) for response in search_responses for i in range(1,12)]
        listing_links = [(self.base_url + link) for list in listing_links for link in list]

        return listing_links

    def get_info_box_element(self, response, element_path, element_path_2=None):
        try:
            info = response.html.xpath(self.info_box_xpath + element_path)[0].text.split('\n')[0]
            return info
        except:
            if (element_path_2 != None):
                try:
                    info = response.html.xpath(self.info_box_xpath + element_path_2)[0].text.split('\n')[0]
                    return info
                except:
                    return None
            else:
                return None

    def extract_listing_data(self, url):
        """
        Scrapes the desired data from a given room listing.

        Returns: Dictionary of the room's details.

        """

        response = self.get_source(url)

        try:
            ad_ref = response.html.xpath('//*[@id="listing_ref"]')[0].text.split('\n')[0]
        except:
            try:
                ad_ref = response.html.xpath('//*[@id="listing_ref"]/span/text()')[0]
            except:
                ad_ref = None
        try:
            distance_to_station = response.html.find('.key-features__station-distance', first=True).text.split('\n')[0]
        except:
            distance_to_station = None

        house_type = self.get_info_box_element(response, 'section[1]/ul/li[1]')
        area = self.get_info_box_element(response, 'section[1]/ul/li[2]')
        postcode = self.get_info_box_element(response, 'section[1]/ul/li[3]')
        price = self.get_info_box_element(response, '/section[2]/ul/li/strong', '/section[2]/h3')
        available_in = self.get_info_box_element(response, "section[4]/dl/dt[text() = 'Available']/following-sibling::dd")
        min_term = self.get_info_box_element(response, "section[4]/dl/dt[text() = 'Minimum term']/following-sibling::dd")
        max_term = self.get_info_box_element(response, "section[4]/dl/dt[text() = 'Maximum term']/following-sibling::dd")
        deposit = self.get_info_box_element(response, "section[5]/dl/dt[text() = 'Deposit']/following-sibling::dd")
        bills = self.get_info_box_element(response, "section[5]/dl/dt[text() = 'Bills included?']/following-sibling::dd")
        furnished = self.get_info_box_element(response, "section[6]/dl/dt[text() = 'Furnishings']/following-sibling::dd")
        balcony = self.get_info_box_element(response, "section[6]/dl/dt[text() = 'Balcony/Patio']/following-sibling::dd")
        disabled_access = self.get_info_box_element(response, "section[6]/dl/dt[text() = 'Disabled access']/following-sibling::dd")
        parking = self.get_info_box_element(response, "section[6]/dl/dt[text() = 'Parking']/following-sibling::dd")
        living_room = self.get_info_box_element(response, "section[6]/dl/dt[text() = 'Living room']/following-sibling::dd")
        broadband = self.get_info_box_element(response, "section[6]/dl/dt[text() = 'Broadband included']/following-sibling::dd")
        num_flatmates = self.get_info_box_element(response, "section[7]/dl/dd[1]")
        gender = self.get_info_box_element(response, "section[8]/dl/dt[text() = 'Gender']/following-sibling::dd")

        variables = dir()
        variables.remove('response')
        variables.remove('self')
        d = {}
        for v in variables:
            d[v] = eval(v)

        return d

    def get_data(self, num_listings = 0):

        listing_links = self.extract_listings(num_listings)
        data = [self.extract_listing_data(url) for url in listing_links]
        df = pd.DataFrame(data)

        return df


        #TODO: add in option to save properly formatted DataFrame
    def save_data(self, X, path = 'blank'):
        X = X.reset_index()
        if path == 'blank':
            X.to_feather('./data/{}.feather'.format(self.search_id))
        else:
            X.to_feather(path)
        pass
