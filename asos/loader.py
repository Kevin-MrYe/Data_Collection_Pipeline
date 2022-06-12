from sqlalchemy import create_engine
from sqlalchemy import engine
import yaml
import boto3
import os
import pandas as pd
import json
from urllib import request
from tqdm import tqdm

class LoaderMixin:
    """
    A Class used to upload data to the cloud.
    
    Attributes:
        rds_table_name (str): The table name of rds which stores data.
        s3_folder_name (str): The folder name of s3 bucket which stores data.
        bucket_name (str) : The name of bucket which stores data. 
        engine (engine.Engine): The Engine used to connect to AWS RDS.
    """

    def __init__(self):
        with open('config/rds_creds.yaml','r') as f:
            self.rds_creds = yaml.safe_load(f)
        with open('config/s3_creds.yaml','r') as f:
            s3_creds = yaml.safe_load(f)
        self.rds_table_name = 'test_scraper'
        self.s3_folder_anme = 'test_data'
        self.bucket_name = s3_creds['BUCKET_NAME']
        print(self.bucket_name)
        self.engine = self.connect_to_rds()

    def connect_to_rds(self) -> engine.Engine:
        """Connect to AWS RDS using sqlalchemy.

        Returns:
            sqlalchemy.engine.Engine: The Engine used to connect to AWS RDS.
        """
        DATABASE_TYPE = self.rds_creds['DATABASE_TYPE']
        DBAPI = self.rds_creds['DBAPI']
        ENDPOINT = self.rds_creds['ENDPOINT']
        USER = self.rds_creds['USER']
        PASSWORD = self.rds_creds['PASSWORD']
        DATABASE = self.rds_creds['DATABASE']
        PORT = self.rds_creds['PORT']
        path = (f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@"
                +f"{ENDPOINT}:{PORT}/{DATABASE}")
        print(path)
        engine = create_engine(path)

        return engine
        
    def upload_item_data_to_rds(self, item_dict: dict) -> int:
        """Upload one item data to AWS RDS.

        Args:
            item_dict (dict): The dictionary to be uploaded to AWS RDS.

        Returns:
            int: Number of rows affected by to_sql
        """
        df = pd.DataFrame.from_dict(item_dict,orient='index').transpose()
        df.set_index('id',inplace=True)
        affected_rows = df.to_sql(
            self.rds_table_name, 
            self.engine, 
            if_exists='append')

        return affected_rows

    def upload_all_data_to_rds(self) -> int:
        """Upload all items' data to AWS RDS.

        Returns:
            int: Number of rows affected by to_sql
        """
        df = pd.DataFrame(self.all_product_info)
        df.set_index('id',inplace=True)
        affected_rows = df.to_sql(
            self.rds_table_name, 
            self.engine, 
            if_exists='append')

        return affected_rows

    def upload_item_data_to_s3(self, item_dict: dict) -> None:
        """Upload json and images for one itme to S3..
        
        Args:
            item_dict (dict): The dictionary to be uploaded to AWS S3.
        """
        s3_client = boto3.client('s3')
        ##upload json data to S3
        json_object = json.dumps(item_dict, indent=4)
        json_path = os.path.join(self.s3_folder_anme,item_dict['id'],'data.json')
        s3_client.put_object(
            Body=json_object, 
            Bucket=self.bucket_name, 
            Key=json_path)

        ##Upload images data to S3
        image_links = item_dict['image_links']
        i=0
        for link in image_links:
            img_object = request.urlopen(link).read()
            img_name = str(i)+'.jpg'
            img_path = os.path.join(self.s3_folder_anme,item_dict['id'],'images',img_name)
            s3_client.put_object(
                Body=img_object, 
                Bucket=self.bucket_name, 
                Key=img_path)
            i +=1
    
    def upload_all_data_to_s3(self) -> None:
        """Upload json and images for all itmes to S3."""
        # self.get_scraped_id_list()

        for item_dict in tqdm(self.all_product_info):
            self.upload_item_data_to_s3(item_dict)

    def upload_data_folder_to_s3(self) -> None:
        """Upload data floder to S3 bucket."""
        s3_client = boto3.client('s3')
        print("Start to upload data folder to S3")
        for root, dirs, files in os.walk(self.data_folder):
            for filename in files:

                local_path = os.path.join(root,filename)
                s3_client.upload_file(
                    local_path, 
                    self.bucket_name, 
                    local_path)