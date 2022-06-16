from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from tqdm import tqdm
import numpy as np

class Scraper:
    """
    A class used to scrape website data.
    
    Args:
        homepage(str): Homepage url of ASOS.
        target_nums(int): The number of items to be extracted.
        stream_process(bool): True memas save data by stream,otherwise not save.

    Attributes:
        all_product_links (list): A list of all product links.
        all_product_info (list): A list of all product information.
        delay (int): The maximum time takes to find the element.
        page (int): The index of page which is currently being scraped.
        scraped_id_list (list): The id list of products that have beed scraped.
        chrome_options (Options): The object for customizing ChromeDriver.
        driver (webdriver.Chrome): The tool used to control Chrome browser


    """
    def __init__(self, 
        homepage: str, 
        target_nums: int, 
        stream_process: bool = False):
        """Please see help(Scraper) for more info."""
        self.homepage = homepage
        self.target_nums = target_nums
        self.stream_process = stream_process
        self.all_product_links = []
        self.all_product_info = []
        self.delay = 10
        self.page = 1
        self.scraped_id_list = []
        path = "user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005 Safari/537.36'"
        options = Options()      
        options.add_argument('--no-sandbox')        
        options.add_argument('--headless')       
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-setuid-sandbox") 
        options.add_argument('--disable-gpu')
        options.add_argument("--start-maximized")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument(path)
        # with open("config/proxy_list.txt") as f:
        #     proxy_list = f.readlines()
        # proxy = np.random.choice(proxy_list).strip()
        PROXY = '34.145.226.144:8080'
        options.add_argument('--proxy-server=%s' % PROXY)

        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options = options,
            )
        # self.driver = webdriver.Chrome()
    def get_ip_address(self):
        self.driver.get("http://checkip.amazonaws.com/")
        # time.sleep(10)
        body_text = self.driver.find_element(by=By.TAG_NAME,value='body').text
        print(f"Current ip:{body_text}")

    def load_and_accept_cookie(self) -> None: ## return annotation
        """Open ASOS and accept the cookies."""
        print("Start to load and accept cookie...")
        try:
            self.driver.get(self.homepage)
            self.driver.save_screenshot('/home/ubuntu/load.png')
            accept_cookies_button = self.try_to_find_elements(
                "//button[@id='onetrust-accept-btn-handler']",
                "accept cookie button")[0]
            
            accept_cookies_button.click()
        except:
            print("No cookie button")   

    def try_to_find_elements(self, element_path: str, element_name: str) -> list:
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
            print(f"Loading {element_name} took too much time. "+
                "check the element path!")
            element = []
        return element

        
    def search_for(self, search_content: str) -> None:
        """Search in the search textbox and get to the result url.

        Args:
            search_content (str): The product name to be search
        """
        print("Start to search for product...")
        search_bar = self.try_to_find_elements(
            "//input[@id='chrome-search']",
            "search textbox")[0]
        search_bar.send_keys(search_content)
        search_bar.send_keys(Keys.RETURN)
        self.driver.save_screenshot('/home/ubuntu/search.png')
        a = input("Press any key to strart..")

    def get_one_page_item_links(self) -> list:
        """Get the links for products in current page.
        
        Returns:
            list: A list consist of product links in current page  
        """
        item_elements = self.try_to_find_elements(
            "//div[@data-auto-id='productList']/section/article",
            "tshirt_elements")
        page_link_list = []
        for item in item_elements:
            a_tag = item.find_element(By.TAG_NAME,'a')
            item_link = a_tag.get_attribute('href')
            page_link_list.append(item_link)
        self.page += 1

        return page_link_list
    
    def move_to_next_page(self) -> None:
        """ Move to the next page."""

        next_page_tag = self.try_to_find_elements(
            "//a[@data-auto-id='loadMoreProducts']",
            "next page tag")[0]
        next_page_link = next_page_tag.get_attribute('href')
        self.driver.get(next_page_link)
        
    def get_n_page_item_links(self, page_nums: int) -> None:
        """Get the links for products in all N pages.

        Args:
            page_nums (int): The number of pages which to be extract links from
        """
        print("Start to collect product links...")
        for i in tqdm(range(0,page_nums)):
            item_page_links = self.get_one_page_item_links()
            self.all_product_links.extend(item_page_links)
            self.move_to_next_page()
    
    def push_data_to_dict(self, item_id: str, link: str) -> dict:
        """Push extracted data into a dictionary.
        
        Args:
            item_id (str): The id of the item
            link (str): The link of the item
        
        Returns:
            dict: The dictionary to store item data
        """
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
        colour = colour_ele[0].text if colour_ele != [] else None
        rating_avg = rating_avg_ele[0].text if rating_avg_ele != [] else None
        if price_ele != []:
            price = price_ele[0].text.replace('Now ','')
        else: 
            price = None

        if rating_nums_ele != []:
            rating_nums = rating_nums_ele[0].text.replace('(','').replace(')','')
        else:
            rating_nums = None


        image_links = self.get_image_links_for_item()
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
        item_dict['id'] = item_id
        item_dict['name'] = name
        item_dict['item_link'] = link
        item_dict['brand'] = brand
        item_dict['price'] = price
        item_dict['colour'] = colour
        item_dict['rating_avg'] = rating_avg
        item_dict['rating_nums'] = rating_nums
        item_dict['image_links'] = image_links

        return item_dict

    def get_all_item_info(self) -> None:
        """ Get the product infomation for all links."""
        print("Start to extract product information...")
        if len(self.all_product_links) < self.target_nums:
            raise ValueError("The target nums can't be less than link nums")
        i=1
        for link in tqdm(self.all_product_links[0:self.target_nums]):

            self.driver.get(link)
            #check whether the id was scraped before
            product_id_ele = self.try_to_find_elements(
                "//div[@class='product-code']/p[1]",
                "product_id")
            product_id = product_id_ele[0].text if product_id_ele != [] else None
            if product_id in self.scraped_id_list:
                print("This product has benn scraped before")
                continue
            elif product_id == None:
                print('---------------------------------------')
                print("This product details can't be extracted")
                print(f"The link is {link}")
                print('---------------------------------------')
                continue
            #push data into a dictionary
            item_dict = self.push_data_to_dict(product_id, link)

            # print("---------------------------------")
            # print(f"NO.{i}",end=" ")
            # print(f"The product id is: {item_dict['id']}")
            # print(f"The product name is: {item_dict['name']}")
            # print(f"The link is: {item_dict['item_link']}")
            # print(f"The brand is: {item_dict['brand']}")
            # print(f"The price is: {item_dict['price']}")
            # print(f"The colour is: {item_dict['colour']}")
            # print(f"The average rating is: {item_dict['rating_avg']}")
            # print(f"The rating numbers is: {item_dict['rating_nums']}")
            # print(f"The image links is: {item_dict['image_links']}")

            if self.stream_process == True:
                # #save data
                self.save_item_by_stream(item_dict)
            self.all_product_info.append(item_dict)
            self.scraped_id_list.append(product_id)
            i+=1

    def save_item_by_stream(self, item_dict: dict) -> None:
        """Save item data locally or on the cloud

        Args:
            item_dict (dict): The item dictionary to be saved
        """
        if self.save_locally == True:
            print("Start to save item josn locally...")
            self.save_item_json_locally(item_dict)
            print("Start to save item images locally...")
            self.download_item_images_locally(item_dict)
        elif self.save_locally == False:
            print("Start to upload item data to rds...")
            self.upload_item_data_to_rds(item_dict)
            print("Start to upload item data to s3...")
            self.upload_item_data_to_s3(item_dict)

    def get_image_links_for_item(self) -> list:
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