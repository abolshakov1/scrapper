

class Scrapper:
    url: str

    def find_images_in_post(self, url):
        raise NotImplementedError

    def scrap_best_pages(self, count):
        raise NotImplementedError



