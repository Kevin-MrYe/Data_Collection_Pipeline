import unittest
from unittest.mock import patch
from asos.scraper import Scraper
from asos.transformer import TransformerMixin
from asos.loader import LoaderMixin

class TestScraper(unittest.TestCase):
    @classmethod
    def setUpClass(inst):
        inst.scraper = Scraper("https://www.asos.com/",10)

    def test_load_and_accept_cookie(self):
        expected_url = "https://www.asos.com/men/"
        self.scraper.load_and_accept_cookie()
        result_url = self.scraper.driver.current_url
        self.assertEqual(expected_url,result_url)

    def test_try_to_find_elements(self):
        self.scraper.driver.get("https://www.asos.com/")
        element_1 = self.scraper.try_to_find_elements(
            "//input[@id='chrome-search']","search textbox")
        self.assertIsInstance(element_1,list)

    def test_search_for(self):
        self.scraper.driver.get("https://www.asos.com/")
        self.scraper.search_for("T-Shirt For Women")
        expected_url = "https://www.asos.com/search/?q=t-shirt+for+women"
        result_url = self.scraper.driver.current_url
        self.assertEqual(expected_url, result_url)

    def test_get_one_page_item_links(self):
        page5_url = "https://www.asos.com/search/?page=5&q=t-shirts%20for%20men"
        tshirt_per_page = 72
        self.scraper.driver.get(page5_url)
        result_counts = len(self.scraper.get_one_page_item_links())
        self.assertEqual(tshirt_per_page, result_counts)

    def test_move_to_next_page(self):
        page3_url = "https://www.asos.com/search/?page=3&q=t-shirts%20for%20men"
        page4_url = "https://www.asos.com/search/?page=4&q=t-shirts%20for%20men"
        self.scraper.driver.get(page3_url)
        self.scraper.move_to_next_page()
        result_url = self.scraper.driver.current_url
        self.assertEqual(page4_url, result_url)

    def test_get_n_page_item_links(self):
        page1_url = "https://www.asos.com/search/?page=1&q=t-shirts%20for%20men"
        self.scraper.driver.get(page1_url)
        self.scraper.all_product_links = []
        self.scraper.get_n_page_item_links(3)
        expected_links_count = 3*72
        result_links_count = len(self.scraper.all_product_links)
        self.assertEqual(expected_links_count, result_links_count)

    def test_push_data_to_dict(self):
        item_link = "https://www.asos.com/tommy-hilfiger/tommy-hilfiger-embroidered-flag-logo-t-shirt-in-white/prd/12591347?clr=snow-white&colourWayId=16396295&SearchQuery=t-shirt+for+men"
        self.scraper.driver.get(item_link)
        item_dict = self.scraper.push_data_to_dict('111','link')
        self.assertIsInstance(item_dict,dict)

    def test_get_all_item_info(self):
        self.scraper.all_product_info = []
        self.scraper.all_product_links = ['''https://www.asos.com/tommy-hilfiger/tommy-hilfiger-authentic
                                    -lounge-t-shirt-side-logo-taping-in-navy/prd/10269381?
                                    clr=navy&colourWayId=16287314&SearchQuery=t-shirts+for+men''',
                                    '''https://www.asos.com/asos-design/asos-design-organic-t-shirt-
                                    with-crew-neck-in-black/prd/13112617?clr=black&colourWayId=16464618&
                                    SearchQuery=t-shirts+for+men '''
                                    ]
        self.scraper.target_nums = 2
                                    
        self.scraper.stream_process = False
        self.scraper.get_all_item_info()
        if self.scraper.all_product_info != []:
            for i in range(0,len(self.scraper.all_product_info)):
                self.assertIsInstance(self.scraper.all_product_info[i],dict)


    def test_get_image_links_for_item(self):
        product_detail_url = '''https://www.asos.com/tommy-hilfiger/tommy-hilfiger-authentic
                                -lounge-t-shirt-side-logo-taping-in-navy/prd/10269381?
                                clr=navy&colourWayId=16287314&SearchQuery=t-shirts+for+men'''
        self.scraper.driver.get(product_detail_url)
        expected_img_counts = 4
        result_img_count = len(self.scraper.get_image_links_for_item())
        self.assertEqual(expected_img_counts, result_img_count)
    
        

    @classmethod
    def tearDownClass(inst):
        inst.scraper.driver.quit()

if __name__ == '__main__':
    unittest.main(verbosity=2)