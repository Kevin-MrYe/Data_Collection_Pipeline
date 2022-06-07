import unittest
from unittest.mock import patch
from asos.asos_scraper import AsosScraper
import sqlalchemy


class TestAsosScraper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.scraper = AsosScraper("https://www.asos.com/")

    def test_load_and_accept_cookie(self):
        expected_url = "https://www.asos.com/"
        self.scraper.load_and_accept_cookie()
        result_url = self.scraper.driver.current_url
        self.assertEqual(expected_url,result_url)

    def test_try_to_find_elements(self):
        self.scraper.driver.get("https://www.asos.com/")
        element_1 = self.scraper.try_to_find_elements(
            "//input[@id='chrome-search']","search textbox")
        self.assertIsNotNone(element_1,"Can't find the element !")

    def test_search_for(self):
        self.scraper.driver.get("https://www.asos.com/")
        self.scraper.search_for("T-Shirt For Women")
        expected_url = "https://www.asos.com/search/?q=t-shirt+for+women"
        result_url = self.scraper.driver.current_url
        self.assertEqual(expected_url, result_url)

    def test_move_to_next_page(self):
        page3_url = "https://www.asos.com/search/?page=3&q=t-shirts%20for%20men"
        page4_url = "https://www.asos.com/search/?page=4&q=t-shirts%20for%20men"
        self.scraper.driver.get(page3_url)
        self.scraper.move_to_next_page()
        result_url = self.scraper.driver.current_url
        self.assertEqual(page4_url, result_url)

    def test_get_tshirt_page_links(self):
        page5_url = "https://www.asos.com/search/?page=5&q=t-shirts%20for%20men"
        tshirt_per_page = 72
        self.scraper.driver.get(page5_url)
        result_counts = len(self.scraper.get_tshirt_page_links())
        self.assertEqual(tshirt_per_page, result_counts)

    def test_get_n_page_tshirt_links(self):
        page1_url = "https://www.asos.com/search/?page=1&q=t-shirts%20for%20men"
        self.scraper.driver.get(page1_url)
        self.scraper.all_product_links = []
        self.scraper.get_n_page_tshirt_links(5)
        expected_links_count = 5*72
        result_links_count = len(self.scraper.all_product_links)
        self.assertEqual(expected_links_count, result_links_count)

    def test_get_all_tshirt_info(self):
        self.scraper.all_product_info = []
        self.scraper.all_product_links = ['''https://www.asos.com/tommy-hilfiger/tommy-hilfiger-authentic
                                    -lounge-t-shirt-side-logo-taping-in-navy/prd/10269381?
                                    clr=navy&colourWayId=16287314&SearchQuery=t-shirts+for+men''',
                                    '''https://www.asos.com/asos-design/asos-design-organic-t-shirt-
                                    with-crew-neck-in-black/prd/13112617?clr=black&colourWayId=16464618&
                                    SearchQuery=t-shirts+for+men '''
                                    ]
        self.scraper.get_all_tshirt_info()
        if self.scraper.all_product_info != []:
            for i in range(0,len(self.scraper.all_product_info)):
                self.assertIsInstance(self.scraper.all_product_info[i],dict)

    def test_get_image_links_for_tshirt(self):
        product_detail_url = '''https://www.asos.com/tommy-hilfiger/tommy-hilfiger-authentic
                                -lounge-t-shirt-side-logo-taping-in-navy/prd/10269381?
                                clr=navy&colourWayId=16287314&SearchQuery=t-shirts+for+men'''
        self.scraper.driver.get(product_detail_url)
        expected_img_counts = 4
        result_img_count = len(self.scraper.get_image_links_for_tshirt())
        self.assertEqual(expected_img_counts, result_img_count)


    @patch('asos_scraper.os.path.exists')
    @patch('asos_scraper.os.makedirs')
    def test_create_data_folders(self, mock_make_dirs, mock_exists):
        mock_exists.return_value = False
        self.scraper.create_data_folders()
        mock_make_dirs.assert_called()
        mock_exists.assert_called()

    @patch('asos_scraper.json.dump')
    @patch('builtins.open')
    def test_save_json_locally(self, mock_open, mock_json_dump):
        self.scraper.all_product_info = [{'id':'1','name':'A'},{'id':'2','name':'B'}]
        self.scraper.save_json_locally()

        mock_open.assert_called()
        mock_json_dump.assert_called()

    @patch('asos_scraper.request.urlretrieve')
    def test_download_images_locally(self, mock_download_images):
        self.scraper.all_product_info = [
                                {'id':'1','image_links':['url1','url2']},
                                {'id':'2','image_links':['url3','url4']}]
        self.scraper.download_images_locally()
        mock_download_images.assert_called()
    
    def test_connect_to_rds(self):
        conn = self.scraper.connect_to_rds()
        self.assertIsInstance(conn, sqlalchemy.engine.Engine )

    @patch('asos_scraper.pd.DataFrame.to_sql')
    def test_upload_data_to_rds_directly(self, mock_to_sql):
        mock_to_sql.return_value = 'result data'
        result = self.scraper.upload_data_to_rds_directly()
        self.assertEqual(result, 'result data')
        self.assertEqual(mock_to_sql.call_count, 1)

    @patch('asos_scraper.boto3.client')
    def tesr_upload_data_to_s3_directly(self, mock_client):
        self.scraper.upload_data_to_s3_directly()
        mock_client.assert_called()
        mock_client.return_value.put_object.assert_called()

    @patch('asos_scraper.boto3.client')
    def test_upload_data_folder_to_s3(self, mock_client):
        self.scraper.upload_data_folder_to_s3()
        mock_client.assert_called()
        mock_client.return_value.upload_file.assert_called()

    @patch('asos_scraper.pd.read_sql_query')
    def test_get_scraped_id_list(self, mock_read_sql):
        mock_read_sql.return_value['id'].values.tolist.return_value = [1,2,3]
        self.scraper.get_scraped_id_list()
        self.assertEqual(self.scraper.scraped_id_list,[1,2,3])
         


    @classmethod
    def tearDownClass(inst):
        inst.scraper.driver.quit()

if __name__ == '__main__':
    unittest.main(verbosity=2)