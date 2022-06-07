from scraper import Scraper
from transformer import TransformerMixin
from loader import LoaderMixin



class AsosScraper(Scraper, TransformerMixin, LoaderMixin):

    # def __init__(self, homepage: str, save_locally: bool, target_nums: int):
        # super().__init__(homepage, save_locally, target_nums)
    
    def run_scraper(self):

        asos_scraper.get_scraped_id_list()
        asos_scraper.load_and_accept_cookie()
        asos_scraper.search_for("T-shirt for men")
        asos_scraper.get_n_page_item_links(1)
        asos_scraper.get_all_item_info()

        ##batch process -- locally
        # asos_scraper.create_data_folders()
        # asos_scraper.save_all_json_locally()
        # asos_scraper.download__all_images_locally()

        ##stream process -- cloud
        # asos_scraper.upload_all_data_to_rds_directly()
        # asos_scraper.upload_all_data_to_s3_directly()





if __name__ == '__main__':
    save_locally = False
    asos_scraper = AsosScraper("https://www.asos.com/",save_locally,10)
    asos_scraper.run_scraper()
    
    