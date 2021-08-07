from scrappers import dtf

URL = "https://dtf.ru/kek/819260"

dtf_scrapper = dtf.DtfScrapper()
dtf_scrapper.scrap_pages(3)

# img_url = dtf_scrapper.find_images_in_post(URL)
# download_image(img_url)

#dtf_scrapper.download_all_new()

