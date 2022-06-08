import os
from tqdm import tqdm
import pandas as pd
import json
from urllib import request

class TransformerMixin:

    def create_data_folders(self) -> None:
        """Create the data folders for different product item."""

        print("Start to create folder...")
        if not os.path.exists(self.data_folder):
                os.makedirs(self.data_folder)
        
        for item_dict in tqdm(self.all_product_info):
        
            image_folder_path = '/'.join([
                os.getcwd(), 
                self.data_folder, 
                item_dict['id'], 
                'images'])
            if not os.path.exists(image_folder_path):
                os.makedirs(image_folder_path)

    #save json locally by batch
    def save_all_json_locally(self) -> None:    
        """Save all data in local json files."""

        print("Start to save josn locally...")
        for item_dict in tqdm(self.all_product_info):
            self.save_json_locally(item_dict)
    
    #save csv
    def save_csv_locally(self) -> None:
        """Save all data to csv file locally"""
        csv_path = self.data_folder+'/final_data.csv'
        df = pd.DataFrame(self.all_product_info)
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode='a',header=False,index=False)
        else:
            df.to_csv(csv_path,mode='a',index=False)
    
    #save images locally by batch
    def download__all_images_locally(self) -> None:
        """Download all the images corresponding to different product item."""

        print("Start to save images locally...")
        for item_dict in tqdm(self.all_product_info):
            self.download_images_locally(item_dict)

    ##save data locally by stream
    def save_json_locally(self, item_dict: dict) -> None:    
        """Save json files corresponding to one item."""
            
        data_point_path = '/'.join([
            os.getcwd(), 
            self.data_folder, 
            item_dict['id']])
        
        if not os.path.exists(data_point_path):
                os.makedirs(data_point_path)
        with open(data_point_path +'/data.json',mode='w+') as f:
            json.dump(item_dict, f, indent=4)

    ##save data locally by stream
    def download_images_locally(self, item_dict: dict) -> None:
        """Download images corresponding to one item."""

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
    


    