from asos_scraper import AsosScraper

#True means save data locally, Flase means save data on the cloud.
save_locally = False
#True means save data by stream, Flase means save data by batch.
stream_process = True
asos_scraper = AsosScraper(
    "https://www.asos.com/",
    save_locally,
    stream_process,
    20)
asos_scraper.run_scraper()
    