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

        super().__init__(homepage, target_nums)
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
                asos_scraper.save_all_json_locally()
                asos_scraper.save_csv_locally()
                asos_scraper.download__all_images_locally()
            elif self.save_locally == False:
                # batch process -- cloud
                asos_scraper.upload_all_data_to_rds_directly()
                asos_scraper.upload_all_data_to_s3_directly()





if __name__ == '__main__':
    save_locally = False
    stream_process = False
    asos_scraper = AsosScraper(
        "https://www.asos.com/",
        save_locally,
        stream_process,
        10)
    asos_scraper.run_scraper()
    
    