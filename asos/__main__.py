from asos_scraper import AsosScraper

save_locally = True
asos_scraper = AsosScraper("https://www.asos.com/",save_locally,10)
# print(asos_scraper.connect_to_rds().connect())
asos_scraper.get_scraped_id_list()
asos_scraper.load_and_accept_cookie()
asos_scraper.search_for("T-shirt for men")
asos_scraper.get_n_page_tshirt_links(1)
asos_scraper.save_all_scraped_data()