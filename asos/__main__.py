from asos_scraper import AsosScraper

save_locally = False
asos_scraper = AsosScraper("https://www.asos.com/",save_locally,10)
asos_scraper.run_scraper()