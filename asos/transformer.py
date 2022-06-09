import os
from tqdm import tqdm
import pandas as pd
import json
from urllib import request

class TransformerMixin:
    """
    A Class used to transform data to local files.
    
    Attributes:
        data_folder (str): The name of folder where store all scraped data.
    """
    def __init__(self):
        self.data_folder = 'asos/test_data'
        ##save data locally by stream
        
    def save_item_json_locally(self, item_dict: dict) -> None:    
        """Save one json file for one item locally."""
            
        data_point_path = '/'.join([
            os.getcwd(), 
            self.data_folder, 
            item_dict['id']])
        
        if not os.path.exists(data_point_path):
                os.makedirs(data_point_path)
        with open(data_point_path +'/data.json',mode='w+') as f:
            json.dump(item_dict, f, indent=4)

    ##save data locally by stream
    def download_item_images_locally(self, item_dict: dict) -> None:
        """Download one group images for one item locally."""

        image_folder_path = '/'.join([
            os.getcwd(), 
            self.data_folder, 
            item_dict['id'], 
            'images'])
        if not os.path.exists(image_folder_path):
                os.makedirs(image_folder_path)
        i=0
        for image_url in item_dict['image_links']:
            image_name = image_folder_path+ '/' + str(i) + '.jpg'
            request.urlretrieve(image_url,image_name)
            i += 1
    #save csv
    def save_csv_locally(self) -> None:
        """Save all data to one csv file locally"""
        if not os.path.exists(self.data_folder):
                os.makedirs(self.data_folder)

        csv_path = self.data_folder+'/final_data.csv'
        df = pd.DataFrame(self.all_product_info)
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode='a',header=False,index=False)
        else:
            df.to_csv(csv_path,mode='a',index=False)
    
    #save json locally by batch
    def save_all_json_locally(self) -> None:    
        """Save all json files locally."""
        for item_dict in tqdm(self.all_product_info):
            self.save_item_json_locally(item_dict)

    #save images locally by batch
    def download__all_images_locally(self) -> None:
        """Download all the images locally."""

        for item_dict in tqdm(self.all_product_info):
            self.download_item_images_locally(item_dict)

    


    