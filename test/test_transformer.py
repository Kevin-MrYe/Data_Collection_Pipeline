import unittest
from unittest import mock
from unittest.mock import patch
from asos.transformer import TransformerMixin

class TestTransformerMixin(unittest.TestCase):
    @classmethod
    def setUpClass(inst):
        inst.trans = TransformerMixin()
        inst.all_product_info = [{'id':'1','name':'A'},{'id':'2','name':'B'}]
    
    @patch('asos.transformer.pd.DataFrame.to_csv')
    @patch('asos.transformer.os.makedirs')
    @patch('asos.transformer.os.path.exists')
    def test_save_csv_locally(self, mock_exists, mock_makedirs, mock_to_csv):
        self.trans.all_product_info = [{'id':'1','name':'A'},{'id':'2','name':'B'}]
        mock_exists.return_value = False
        self.trans.save_csv_locally()
        mock_makedirs.assert_called()
        mock_to_csv.assert_called()

    @patch('asos.transformer.json.dump')
    @patch('builtins.open')
    @patch('asos.transformer.os.path.exists')
    def test_save_item_json_locally(self,mock_exists, mock_open, mock_dump):
        item_dict = {'id':'110','name':'AAA'}
        mock_exists.return_value = True
        self.trans.save_item_json_locally(item_dict)
        mock_open.assert_called()
        mock_dump.assert_called()

    @patch.object(TransformerMixin,'save_item_json_locally')
    def test_save_all_json_locally(self, mock_save_item_json):
        self.trans.all_product_info = range(0,10)
        self.trans.save_all_json_locally()
        self.assertEqual(mock_save_item_json.call_count,10)

    @patch('asos.transformer.request.urlretrieve')
    @patch('asos.transformer.os.path.exists')
    def test_download_item_images_locally(self,mock_exists, mock_urlret):
        item_dict = {'id':'AAA','image_links':[1,2,3]}
        mock_exists.return_value = True
        self.trans.download_item_images_locally(item_dict)
        self.assertEqual(mock_urlret.call_count,3)

    @patch.object(TransformerMixin,'download_item_images_locally')
    def test_download__all_images_locally(self, mock_download_item_images):
        self.trans.all_product_info = range(0,10)
        self.trans.download__all_images_locally()
        self.assertEqual(mock_download_item_images.call_count,10)




if __name__ == '__main__':
    unittest.main(verbosity=2)

