from typing import Tuple
from scraper import Scraper
from transformer import TransformerMixin
from loader import LoaderMixin



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
        print("Here is asosScraper")

        Scraper.__init__(self,homepage,target_nums)
        TransformerMixin.__init__(self)
        LoaderMixin.__init__(self)
        self.save_locally = save_locally
        self.stream_process = stream_process

    
    def run_scraper(self):
        """Run the scraper to extract,transform and load data."""

        asos_scraper.get_scraped_id_list()
        asos_scraper.load_and_accept_cookie()
        asos_scraper.search_for("T-shirt for men")
        asos_scraper.get_n_page_item_links(1)
        asos_scraper.get_all_item_info()

        if self.stream_process == False:
            if self.save_locally == True:
                #batch process -- locally
                asos_scraper.save_csv_locally()
                print("Strat to save all json locally...")
                asos_scraper.save_all_json_locally()
                print("Strat to download all images locally...")
                asos_scraper.download__all_images_locally()
            elif self.save_locally == False:
                # batch process -- cloud
                print("Strat to upload all data to rds...")
                asos_scraper.upload_all_data_to_rds()
                print("Strat to upload all data to s3...")
                asos_scraper.upload_all_data_to_s3()





if __name__ == '__main__':
    #True means save data locally, Flase means save data on the cloud.
    save_locally = False
    #True means save data by stream, Flase means save data by batch.
    stream_process = False
    asos_scraper = AsosScraper(
        "https://www.asos.com/",
        save_locally,
        stream_process,
        20)
    asos_scraper.run_scraper()
    
    