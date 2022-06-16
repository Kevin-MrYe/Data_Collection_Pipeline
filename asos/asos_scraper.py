from .scraper import Scraper
from .transformer import TransformerMixin
from .loader import LoaderMixin
import pandas as pd
import os



class AsosScraper(Scraper, TransformerMixin, LoaderMixin):
    """A class used to scrape ASOS.

    Args:
        homepage(str): Homepage url of ASOS.
        save_locally(bool): True means save data locally, otherwise on the clound.
        stream_process(bool): True means stream process, otherwise batch process.
        target_nums(int): The number of items to be extracted.
    """
    def __init__(
            self, 
            homepage: str, 
            save_locally: bool, 
            stream_process: bool, 
            target_nums: int):

        Scraper.__init__(self,homepage,target_nums)
        TransformerMixin.__init__(self)
        LoaderMixin.__init__(self)
        self.save_locally = save_locally
        self.stream_process = stream_process

    def get_scraped_id_list(self) -> None:
        """Get the scraped id from RDS."""
        print("Strat to get scraped id list...")
        if self.save_locally ==  True:
            try:
                self.scraped_id_list = os.listdir(self.data_folder)
            except:
                self.scraped_id_list = []

        elif self.save_locally == False:
            self.engine = self.connect_to_rds()
            try:
                df_scraped_id = pd.read_sql_query(
                    'SELECT id FROM test_scraper',
                     self.engine)

                self.scraped_id_list = df_scraped_id['id'].values.tolist()
            except:
                self.scraped_id_list = []

    
    def run_scraper(self):
        """Run the scraper to extract,transform and load data."""
        self.get_ip_address()
        self.get_scraped_id_list()
        self.load_and_accept_cookie()
        self.search_for("T-shirt for men")
        self.get_n_page_item_links(1)
        self.get_all_item_info()
        self.save_if_batch_process()

    def save_if_batch_process(self):
        if self.stream_process == False:
            if self.save_locally == True:
                #batch process -- locally
                self.save_csv_locally()
                print("Strat to save all json locally...")
                self.save_all_json_locally()
                print("Strat to download all images locally...")
                self.download__all_images_locally()
            elif self.save_locally == False:
                # batch process -- cloud
                print("Strat to upload all data to rds...")
                self.upload_all_data_to_rds()
                print("Strat to upload all data to s3...")
                self.upload_all_data_to_s3()
            elif self.save_locally == None:
                pass





if __name__ == '__main__':
    #True means save data locally, Flase means save data on the cloud.
    save_locally = False
    #True means save data by stream, Flase means save data by batch.
    stream_process = True
    asos_scraper = AsosScraper(
        "https://www.asos.com/",
        save_locally,
        stream_process,
        10)
    asos_scraper.run_scraper()
    
    