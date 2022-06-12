import unittest
from unittest import mock
from unittest.mock import patch
from asos.loader import LoaderMixin
from moto import mock_s3

class TestLoaderMixinn(unittest.TestCase):
    @classmethod
    def setUpClass(inst):
        inst.loader = LoaderMixin()

    @patch('asos.loader.create_engine')
    def test_connect_to_rds(self, mock_create_engine):
        self.loader.connect_to_rds()
        mock_create_engine.assert_called()

    @patch('asos.loader.pd.DataFrame.to_sql')
    def test_upload_item_data_to_rds(self, mock_to_sql):
        item_dict = {'id':'AAA'}
        mock_to_sql.return_value = 1
        result = self.loader.upload_item_data_to_rds(item_dict)
        self.assertEqual(result,1)

    @patch('asos.loader.pd.DataFrame.to_sql')
    def test_upload_all_data_to_rds(self, mock_to_sql):
        self.loader.all_product_info= [{'id':'AAA'}]
        mock_to_sql.return_value = 10
        result = self.loader.upload_all_data_to_rds()
        self.assertEqual(result,10)

    @patch('asos.loader.request.urlopen')
    @patch('asos.loader.os.path.join')
    @patch('asos.loader.boto3.client')
    def test_upload_item_data_to_s3(self,mock_client,mock_join,mock_urlopen,):

        item_dict = {'id':'00001','image_links':[1,2,3]}

        # mock_urlopen.return_value.read.return_value = 'put_img'
        mock_join.return_value = True
        mock_urlopen.return_value.read.return_value = True
        self.loader.upload_item_data_to_s3(item_dict)
        self.assertTrue(mock_client.return_value.put_object.call_count == 4)

    @patch.object(LoaderMixin,'upload_item_data_to_s3')
    def test_upload_all_data_to_s3(self, mock_upload_item_data_to_s3):
        self.loader.all_product_info = range(0,10)
        self.loader.upload_all_data_to_s3()
        self.assertEqual(mock_upload_item_data_to_s3.call_count,10)

    @patch('asos.loader.os.walk')
    @patch('asos.loader.boto3.client')
    def test_upload_data_folder_to_s3(self, mock_client,mock_walk):
        self.loader.data_folder = True
        mock_walk.return_value = [('1','2',['3','4','5'])]
        self.loader.upload_data_folder_to_s3()
        mock_client.assert_called()
        mock_client.return_value.upload_file.assert_called()

if __name__ == '__main__':
    unittest.main(verbosity=2)
