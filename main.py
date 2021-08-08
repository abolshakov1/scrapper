from scrappers.dtf import dtf
from downloader import download_image

dtf_scrapper = dtf.DtfScrapper()
dtf_scrapper.scrap_best_pages(3)

# img_url = dtf_scrapper.find_images_in_post(URL)

# img_url = 'https://leonardo.osnova.io/433c9771-fa22-535e-baac-3416569d5bad/'
# download_image(img_url)

#dtf_scrapper.download_all_new()
