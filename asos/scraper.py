from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
import os
import pandas as pd

class Scraper:
    """
    A class used to scrape ASOS(a British online fashion and cosmetic retailer).
    
    Args:
        homepage(str): Homepage url of ASOS.
        save_locally(bool): True means save data locally, otherwise on the clound.

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
    def __init__(self, homepage: str, save_locally: bool, target_nums: int):
        """
        """
        self.homepage = homepage
        self.save_locally = save_locally
        self.target_nums = target_nums
        self.all_product_links = []
        self.all_product_info = []
        self.delay = 10
        self.page = 1
        self.data_folder = 'asos/test_data'
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

    def load_and_accept_cookie(self) -> None: ## return annotation
        """Open ASOS and accept the cookies."""
        print("Start to load and accept cookie...")
        try:
            self.driver.get(self.homepage)
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
            print(f"Loading {element_name} took too much time"+
                "check the element path!")
            element = []
        return element

        
    def search_for(self, search_content: str) -> None:
        """Search in the search textbox and get to the result url.

        Args:
            search_content (str): The product name to be search.
        """
        print("Start to search for product...")
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
        self.page += 1

        return page_link_list
    
    def move_to_next_page(self) -> None:
        """ Move to the next page."""

        next_page_tag = self.try_to_find_elements(
            "//a[@data-auto-id='loadMoreProducts']",
            "next page tag")[0]
        next_page_link = next_page_tag.get_attribute('href')
        self.driver.get(next_page_link)
        
    def get_n_page_tshirt_links(self, page_nums: int) -> None:
        """Get the links for products in all N pages.

        Args:
            page_nums (int): The number of pages which to be extract links from.
        """
        print("Start to collect product links...")
        for i in tqdm(range(0,page_nums)):
            tshirt_page_links = self.get_tshirt_page_links()
            self.all_product_links.extend(tshirt_page_links)
            self.move_to_next_page()

    def get_all_tshirt_info(self) -> None:
        """ Get the product infomation for all links."""
        print("Start to extract product information...")
        if len(self.all_product_links) < self.target_nums:
            raise ValueError("The target nums can't be less than link nums")
        i=0
        for link in tqdm(self.all_product_links[0:self.target_nums]):

            self.driver.get(link)
            product_id_ele = self.try_to_find_elements(
                "//div[@class='product-code']/p[1]",
                "product_id")
            product_id = product_id_ele[0].text if product_id_ele != [] else None
            if product_id in self.scraped_id_list:
                print("This product has benn scraped before")
                continue
            elif product_id == None:
                print("This product details can't be extracted")
                print(f"The link is {link}")
                continue
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
            if self.save_locally == False:
                pass
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
    
    def get_scraped_id_list(self) -> None:
        """Get the scraped id from RDS."""
        print("Strat to get scraped id list...")
        if self.save_locally ==  True:
            try:
                self.scraped_id_list = os.listdir(self.data_folder)
            except:
                self.scraped_id_list = []
            # print(self.scraped_id_list)

        elif self.save_locally == False:
            engine = self.connect_to_rds()
            try:
                df_scraped_id = pd.read_sql_query(
                    'SELECT id FROM test_scraper',
                     engine)

                self.scraped_id_list = df_scraped_id['id'].values.tolist()
            except:
                self.scraped_id_list = []