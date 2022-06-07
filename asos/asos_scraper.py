import traceback
from scraper import Scraper
from transformer import TransformerMixin
from loader import LoaderMixin



class AsosScraper(Scraper, TransformerMixin, LoaderMixin):

    def __init__(self, homepage: str, save_locally: bool, target_nums: int):
        super().__init__(homepage, save_locally, target_nums)
        self.engine = self.connect_to_rds()
    

    def save_all_scraped_data(self) -> None:
        """Save data locally or on the clound"""
        if self.save_locally == True:
            try:
                self.get_all_tshirt_info()
            ## if exception was raised, save current data locally.
            except Exception:
                print(traceback.format_exc())
                self.create_data_folders()
                self.save_json_locally()
                self.download_images_locally()
            ## if no exception, save all data locally.
            else:
                self.create_data_folders()
                self.save_json_locally()
                self.download_images_locally()

        elif self.save_locally == False:
            try:
                self.get_all_tshirt_info()
            ## if exception was raised, save current data on the clound.
            except Exception:
                print(traceback.format_exc())
                self.upload_data_to_rds_directly()
                self.upload_data_to_s3_directly()
            ## if no exception, save all data on the clound.
            else:
                self.upload_data_to_rds_directly()
                self.upload_data_to_s3_directly()
        print("All done !!!")



if __name__ == '__main__':

    ##True save data locally, False save data to cloud.
    save_locally = True
    asos_scraper = AsosScraper("https://www.asos.com/",save_locally,10)
    # print(asos_scraper.connect_to_rds().connect())
    asos_scraper.get_scraped_id_list()
    asos_scraper.load_and_accept_cookie()
    asos_scraper.search_for("T-shirt for men")
    asos_scraper.get_n_page_tshirt_links(1)
    asos_scraper.save_all_scraped_data()

    

    # asos_scraper.upload_data_folder_to_s3()