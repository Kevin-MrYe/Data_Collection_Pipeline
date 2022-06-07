from sqlalchemy import create_engine
from sqlalchemy import engine
from dotenv import load_dotenv
import boto3
import os
import pandas as pd
import json
from urllib import request

class LoaderMixin:

    def connect_to_rds(self) -> engine.Engine:
        """Connect to AWS RDS using sqlalchemy.

        Returns:
            sqlalchemy.engine.Engine: The Object used to connect to AWS RDS.
        """

        load_dotenv()
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = os.getenv('RDS_ENDPOINT')
        USER = 'postgres'
        PASSWORD = os.getenv('RDS_PASSWORD')
        DATABASE = 'asos_scraper'
        PORT = 5432
        path = (f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@"
                +f"{ENDPOINT}:{PORT}/{DATABASE}")
        engine = create_engine(path)

        return engine
        
    def upload_data_to_rds_directly(self, engine: engine.Engine, item_dict: dict) -> int:
        """Upload all information to AWS RDS

        Returns:
            int: Number of rows affected by to_sql
        """
        print("Start to upload data to rds directly")
        df = pd.DataFrame(item_dict)
        df.set_index('id',inplace=True)
        table_name =  'test_scraper'
        affected_rows = df.to_sql(table_name, engine, if_exists='append')

        return affected_rows
    
    def upload_data_to_s3_directly(self, item_dict: dict) -> None:
        """Upload data to s3 directly, without saving them locally."""

        print("Start to upload all info to s3")
        load_dotenv()
        s3_client = boto3.client('s3')
        bucket_name = os.getenv('BUCKET_NAME')
        # self.get_scraped_id_list()

        ##upload json data to S3
        json_object = json.dumps(item_dict, indent=4)
        json_path = os.path.join('test_data',item_dict['id'],'data.json')
        s3_client.put_object(
            Body=json_object, 
            Bucket=bucket_name, 
            Key=json_path)

        ##Upload images data to S3
        image_links = item_dict['image_links']
        i=0
        for link in image_links:
            img_object = request.urlopen(link).read()
            img_name = str(i)+'.jpg'
            img_path = os.path.join('test_data',item_dict['id'],'images',img_name)
            s3_client.put_object(
                Body=img_object, 
                Bucket=bucket_name, 
                Key=img_path)
            i +=1



    
    def upload_data_folder_to_s3(self) -> None:
        """Upload data floder to S3 bucket."""

        print("Start to upload data folder to s3")
        load_dotenv()
        s3_client = boto3.client('s3')
        bucket_name = os.getenv('BUCKET_NAME')
        for root, dirs, files in os.walk(self.data_folder):
            for filename in files:

                local_path = os.path.join(root,filename)
                s3_client.upload_file(local_path, bucket_name, local_path)