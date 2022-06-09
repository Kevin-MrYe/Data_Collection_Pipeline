import unittest
from unittest import mock
from unittest.mock import patch
from asos.loader import LoaderMixin
import boto3

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

    @patch('botocore.client.S3.put_object')
    @patch('asos.loader.request.urlopen')
    @patch('asos.loader.json.dumps')
    def test_upload_item_data_to_s3(self,mock_dumps, mock_urlopen,mock_put_object):
        item_dict = {'id':'00001','image_links':[1,2,3]}
        self.loader.upload_item_data_to_s3(item_dict)
        mock_dumps.assert_called()
        mock_urlopen.assert_called()
        mock_put_object.assert_called()
        


if __name__ == '__main__':
    unittest.main(verbosity=2)
