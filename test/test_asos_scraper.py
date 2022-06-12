import unittest
from unittest import mock
from unittest.mock import patch
from asos.asos_scraper import AsosScraper


class TestAsosScraper(unittest.TestCase):

    @classmethod
    def setUpClass(inst):
        inst.asos_scraper = AsosScraper(
        "https://www.asos.com/",
        True,
        True,
        20)
    
    @patch('asos.asos_scraper.pd.read_sql_query')
    @patch('asos.asos_scraper.os.listdir')
    @patch.object(AsosScraper,'connect_to_rds')
    def test_get_scraped_id_list_locally(self,mock_conn, mock_listdir, mock_read_sql):
        self.asos_scraper.get_scraped_id_list()
        mock_listdir.assert_called()
        mock_conn.assert_not_called()
        mock_read_sql.assert_not_called()

    @patch('asos.asos_scraper.pd.read_sql_query')
    @patch('asos.asos_scraper.os.listdir')
    @patch.object(AsosScraper,'connect_to_rds')
    def test_get_scraped_id_list_cloud(self,mock_conn, mock_listdir, mock_read_sql):    
        self.asos_scraper.save_locally = False
        self.asos_scraper.get_scraped_id_list()
        mock_conn.assert_called()
        mock_read_sql.assert_called()
        mock_listdir.assert_not_called()

    @patch.object(AsosScraper,'save_if_batch_process')
    @patch.object(AsosScraper,'get_all_item_info')
    @patch.object(AsosScraper,'get_n_page_item_links')
    @patch.object(AsosScraper,'search_for')
    @patch.object(AsosScraper,'load_and_accept_cookie')
    @patch.object(AsosScraper,'get_scraped_id_list')
    def test_run_scraper(self,
            mock_get_scraped_id_list,
            mock_load_and_accept_cookie,
            mock_search_for,
            mock_get_n_page_item_links,
            mock_get_all_item_info,
            mock_save_if_batch_process):
        self.asos_scraper.run_scraper()
        mock_get_scraped_id_list.assert_called_once()
        mock_load_and_accept_cookie.assert_called_once()
        mock_search_for.assert_called_once()
        mock_get_n_page_item_links.assert_called_once()
        mock_get_all_item_info.assert_called_once()
        mock_save_if_batch_process.assert_called_once()
    
    @patch.object(AsosScraper,'upload_all_data_to_s3')
    @patch.object(AsosScraper,'upload_all_data_to_rds')
    @patch.object(AsosScraper,'download__all_images_locally')
    @patch.object(AsosScraper,'save_all_json_locally')
    @patch.object(AsosScraper,'save_csv_locally')
    def test_save_if_batch_process_locally(self,
            mock_save_csv_locally,
            mock_save_all_json_locally,
            mock_download__all_images_locally,
            mock_upload_all_data_to_rds,
            mock_upload_all_data_to_s3,
            ):
        self.asos_scraper.stream_process = False
        self.asos_scraper.save_locally = True
        self.asos_scraper.save_if_batch_process()
        mock_save_csv_locally.assert_called_once()
        mock_save_all_json_locally.assert_called_once()
        mock_download__all_images_locally.assert_called_once()
        mock_upload_all_data_to_rds.assert_not_called()
        mock_upload_all_data_to_s3.assert_not_called()

    @patch.object(AsosScraper,'upload_all_data_to_s3')
    @patch.object(AsosScraper,'upload_all_data_to_rds')
    @patch.object(AsosScraper,'download__all_images_locally')
    @patch.object(AsosScraper,'save_all_json_locally')
    @patch.object(AsosScraper,'save_csv_locally')
    def test_save_if_batch_process_cloud(self,
            mock_save_csv_locally,
            mock_save_all_json_locally,
            mock_download__all_images_locally,
            mock_upload_all_data_to_rds,
            mock_upload_all_data_to_s3,
            ):
        self.asos_scraper.stream_process = False
        self.asos_scraper.save_locally = False
        self.asos_scraper.save_if_batch_process()
        mock_save_csv_locally.assert_not_called()
        mock_save_all_json_locally.assert_not_called()
        mock_download__all_images_locally.assert_not_called()
        mock_upload_all_data_to_rds.assert_called_once()
        mock_upload_all_data_to_s3.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=1)