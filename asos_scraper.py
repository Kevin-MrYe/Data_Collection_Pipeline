from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from sqlalchemy import create_engine
from sqlalchemy import engine
from dotenv import load_dotenv
from urllib import request
import pandas as pd
import numpy as np
from tqdm import tqdm
import json
import boto3
import os

class AsosScraper:
    """
    A class used to scrape ASOS(a British online fashion and cosmetic retailer).
    
    Args:
        homepage(str): Homepage url of ASOS.

    Attributes:
        all_product_links (list): A list of all product links.
        all_product_info (list): A list of all product information.
        delay (int): The maximum time takes to find the element.
        page (int): The index of page which is currently being scraped.
        data_folder (str): The name of folder where store all scraped data.
        scraped_id_list (list): The id list of products that have beed scraped.
        chrome_options (Options): The object for customizing ChromeDriver.
        driver (webdriver.Chrome): The tool used to control Chrome browser


    """
    def __init__(self, homepage):
        """
        """
        self.all_product_links = []
        self.all_product_info = []
        self.homepage = homepage
        self.delay = 10
        self.page = 1
        self.data_folder = 'raw_data'
        self.scraped_id_list = []
        self.chrome_options = Options()
        # chrome_options = Options()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--allow-running-insecure-content')        
        self.chrome_options.add_argument('--no-sandbox')        
        self.chrome_options.add_argument('--headless')       
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument("user-agent='Mozilla/5.0 \
        (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/93.0.4577.63 Safari/537.36'")

        self.chrome_options.add_argument("window-size=1920,1080")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        # self.driver = webdriver.Chrome()
        print(type(self.chrome_options))
        print(type(self.driver))

    def get_fake_agents(self):
        with open('rotation/user_agent.txt') as f:
             fake_agents = [line.strip() for line in f.readlines()]
        return fake_agents 

    def load_and_accept_cookie(self) -> None: ## return annotation
        """Open ASOS and accept the cookies."""
        try:
            self.driver.get(self.homepage)
            accept_cookies_button = self.try_to_find_elements(
                "//button[@id='onetrust-accept-btn-handler']",
                "accept cookie button")[0]
            
            accept_cookies_button.click()
        except:
            print("No cookie button")   

    def try_to_find_elements(self, element_path, element_name) -> list:
        """Find the elements as long as they are located.

        Args:
            element_path (str): The path of the elements to be located
            element_name (str): The name of the elements

        Returns:
            list: The element list found by element path
        """
        
        try:
            element = WebDriverWait(self.driver, self.delay).\
                        until(EC.presence_of_all_elements_located(
                        (By.XPATH, element_path)))
        except TimeoutException:
            print(f"Loading {element_name} took too much time,\
                check the element path!")
            element = []
        return element

        
    def search_for(self, search_content) -> None:
        """Search in the search textbox and get to the result url.

        Args:
            search_content (str): The product name to be search.
        """
        self.driver.save_screenshot('search.png')
        search_bar = self.try_to_find_elements(
            "//input[@id='chrome-search']",
            "search textbox")[0]
        search_bar.send_keys(search_content)
        search_bar.send_keys(Keys.RETURN)

    def get_tshirt_page_links(self) -> list:
        """Get the links for products in current page.
        
        Returns:
            list: A list consist of product links in current page.  
        """
        tshirt_elements = self.try_to_find_elements(
            "//div[@data-auto-id='productList']/section/article",
            "tshirt_elements")
        page_link_list = []
        for tshirt in tshirt_elements:
            a_tag = tshirt.find_element(By.TAG_NAME,'a')
            item_link = a_tag.get_attribute('href')
            page_link_list.append(item_link)
        print(f'Now in page {self.page}.\
            There are {len(page_link_list)} T-shirts !')
        self.page += 1

        return page_link_list
    
    def move_to_next_page(self) -> None:
        """ Move to the next page."""

        next_page_tag = self.try_to_find_elements(
            "//a[@data-auto-id='loadMoreProducts']",
            "next page tag")[0]
        next_page_link = next_page_tag.get_attribute('href')
        print(f"Turn to Page {self.page} successfully !")
        self.driver.get(next_page_link)
        
    def get_n_page_tshirt_links(self, page_nums) -> None:
        """Get the links for products in all N pages.

        Args:
            page_nums (int): The number of pages which to be extract links from.
        """
        for i in tqdm(range(0,page_nums)):
            tshirt_page_links = self.get_tshirt_page_links()
            self.all_product_links.extend(tshirt_page_links)
            self.move_to_next_page()

    def get_all_tshirt_info(self) -> None:
        """ Get the product infomation for all links."""

        i=0
        for link in tqdm(self.all_product_links[0:10]):

            self.driver.get(link)   

            product_id_ele = self.try_to_find_elements(
                "//div[@class='product-code']/p[1]",
                "product_id")
            product_id = product_id_ele[0].text if product_id_ele != [] else None
            # if product_id in self.scraped_id_list or product_id == None:
            #     print("This product has benn scraped before")
            #     continue
            name_ele = self.try_to_find_elements(
                "//div[@id='aside-content']/div/h1",
                "name")
            brand_ele = self.try_to_find_elements(
                "//div[@class='product-description']/p[1]/a[2]/strong",
                "brand")
            price_ele = self.try_to_find_elements(
                "//span[@data-id='current-price']",
                "price")
            colour_ele = self.try_to_find_elements(
                "//span[@class='product-colour']",
                "colour")
            rating_avg_ele = self.driver.find_elements(
                By.XPATH,"//div[@class='numeric-rating']")
            rating_nums_ele = self.driver.find_elements(
                By.XPATH,"//div[@class='total-reviews']")

          
            name = name_ele[0].text if name_ele != [] else None
            brand = brand_ele[0].text if brand_ele != [] else None
            price = price_ele[0].text.replace('Now ','') if price_ele != [] else None
            colour = colour_ele[0].text if colour_ele != [] else None
            rating_avg = rating_avg_ele[0].text if rating_avg_ele != [] else None
            rating_nums_temp = rating_nums_ele[0].text if rating_nums_ele != [] else None
            rating_nums = rating_nums_temp.replace('(','').replace(')','') 

            image_links = self.get_image_links_for_tshirt()
            item_dict = {}
            item_dict.fromkeys([
                'id',
                'name',
                'item_link',
                'brand',
                'price',
                'colour',
                'rating_avg',
                'rating_nums',
                'image_links'
                ])
            i+=1
            print("---------------------------------")
            print(f"NO.{i}",end=" ")
            print(f'The product id is: {product_id}')
            print(f"The product name is: {name}")
            print(f"The link is: {link}")
            print(f'The brand is: {brand}')
            print(f'The price is: {price}')
            print(f"The colour is: {colour}")
            print(f'The average rating is: {rating_avg}')
            print(f'The rating numbers is: {rating_nums}')
            print(f"The image links is: {image_links}")
            item_dict['id'] = product_id
            item_dict['name'] = name
            item_dict['item_link'] = link
            item_dict['brand'] = brand
            item_dict['price'] = price
            item_dict['colour'] = colour
            item_dict['rating_avg'] = rating_avg
            item_dict['rating_nums'] = rating_nums
            item_dict['image_links'] = image_links
            self.all_product_info.append(item_dict)
            self.scraped_id_list.append(product_id)
            # if i==10:
            #     break

    def get_image_links_for_tshirt(self) -> list:
        """Get all the image links corresponding to different product item.
        
        Returns:
            list: A list consist all image links for single product
        """
        thumbnails_container = self.try_to_find_elements(
            "//ul[@class='thumbnails']",
            "thumbnails container")[0]

        item_img_links = []
        thumbnails_elements = thumbnails_container.find_elements(By.XPATH,".//img")
        for element in thumbnails_elements:
            thumbnail_img_link = element.get_attribute('src')
            full_image_link = (thumbnail_img_link.split('$')[0]
                                +'$n_640w$&amp;wid=513&amp;fit=constrain')
            item_img_links.append(full_image_link)
        

        return item_img_links
    
    def create_data_folders(self) -> None:
        """Create the data folders for different product item."""

        print("Start to create folder")
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


    def save_json_locally(self) -> None:    
        """Save all the scraped data in local folders."""

        print("Start to save josn locally")
        for item_dict in tqdm(self.all_product_info):
            
            data_point_path = '/'.join([
                os.getcwd(), 
                self.data_folder, 
                item_dict['id']])

            with open(data_point_path +'/data.json',mode='w+') as f:
                json.dump(item_dict, f, indent=4)

    def download_images_locally(self) -> None:
        """Download all the images corresponding to different product item."""

        print("Start to save images locally")
        for item_dict in tqdm(self.all_product_info):
            image_folder_path = '/'.join([
                os.getcwd(), 
                self.data_folder, 
                item_dict['id'], 
                'images'])
            i=0
            for image_url in item_dict['image_links']:
                image_name = image_folder_path+ '/' + str(i) + '.jpg'
                request.urlretrieve(image_url,image_name)
                i += 1

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
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@\
            {ENDPOINT}:{PORT}/{DATABASE}")

        return engine
        
    def upload_data_to_rds_directly(self) -> int:
        """Upload all information to AWS RDS

        Returns:
            int: Number of rows affected by to_sql
        """
        print("Start to upload data to rds directly")
        engine = self.connect_to_rds()
        
        df = pd.DataFrame(self.all_product_info)
        df.set_index('id',inplace=True) 
        affected_rows = df.to_sql('test', engine, if_exists='append')

        return affected_rows
    
    def upload_data_to_s3_directly(self) -> None:
        """Upload data to s3 directly, without saving them locally."""

        print("Start to upload all info to s3")
        load_dotenv()
        s3_client = boto3.client('s3')
        bucket_name = os.getenv('BUCKET_NAME')
        # self.get_scraped_id_list()

        for item in tqdm(self.all_product_info):
            json_object = json.dumps(item, indent=4)
            json_path = os.path.join('test_data',item['id'],'data.json')
            s3_client.put_object(
                Body=json_object, 
                Bucket=bucket_name, 
                Key=json_path)

            image_links = item['image_links']
            i=0
            for link in image_links:
                img_object = request.urlopen(link).read()
                img_name = str(i)+'.jpg'
                img_path = os.path.join('test_data',item['id'],'images',img_name)
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
        

    def get_scraped_id_list(self) -> None:
        """Get the scraped id from RDS."""

        engine = self.connect_to_rds()
        print("Connected to RDS")
        try:
            df_scraped_id = pd.read_sql_query('SELECT id FROM test', engine)
            self.scraped_id_list = df_scraped_id['id'].values.tolist()
        except:
            self.scraped_id_list = []



if __name__ == '__main__':

    asos_scraper = AsosScraper("https://www.asos.com/")
    asos_scraper.get_scraped_id_list()
    asos_scraper.load_and_accept_cookie()
    asos_scraper.search_for("T-shirt for men")
    asos_scraper.get_n_page_tshirt_links(1)
    asos_scraper.get_all_tshirt_info()

    # asos_scraper.upload_data_to_rds_directly()
    # asos_scraper.upload_data_to_s3_directly()

    
    # asos_scraper.create_data_folders()
    # asos_scraper.save_json_locally()
    # asos_scraper.download_images_locally()
    # asos_scraper.upload_data_folder_to_s3()

