import requests
from bs4 import BeautifulSoup as _bs

from downloader import download_image
from scrappers.scrapper import Scrapper

class DtfScrapper(Scrapper):
    url = "https://dtf.ru/kek/"
    new_url = "https://dtf.ru/kek/entries/new/"
    url_more = "https://dtf.ru/kek/more?"

    page = 1
    last_id = None
    last_sorting_value = None

    def scrap_best_pages(self, count):
        for i in range(count):
            first_page = i == 0

            if first_page:
                url = self.url
            else:
                url = self.url_more + f'last_id={self.last_id}' \
                                      f'&page={self.page}' \
                                      f'&last_sorting_value={self.last_sorting_value}' \
                                      f'mode=raw'

            content = self._get_page_content(url, first_page)
            self._parse(content, first_page)
            self.page += 1

    def _get_last_sorting_value_from_first_page(self, soup):
        last_sorting_value_div = soup.find('div', class_='feed')
        last_sorting_value = last_sorting_value_div.attrs['data-feed-last-sorting-value']
        if last_sorting_value:
            self.last_sorting_value = last_sorting_value

    def _get_data_id(self, post):
        favorite_marker = post.find('div', class_='favorite_marker')
        data_id = None

        if favorite_marker:
            data_id = favorite_marker.attrs['data-id']

        return data_id

    def _get_img_link(self, post):
        img_div = post.find('div', class_='andropov_image')
        img_link = None
        if img_div:
            img_link = img_div.attrs['data-image-src']

        return img_link

    def _get_likes(self, post):
        likes_span = post.find('span', class_='vote__value__v')
        likes_count = 0

        if likes_span:
            try:
                likes_count = int(likes_span.text)
            except ValueError:
                likes_count = 0

        return likes_count

    def _parse(self, content, firstRequest=True):
        print("==================================================================================")

        soup = _bs(content, "html.parser")
        if firstRequest:
            self._get_last_sorting_value_from_first_page(soup)

        posts = soup.find_all("div", class_='feed__item l-island-round')
        for post in posts:
            data_id = self._get_data_id(post)
            img_link = self._get_img_link(post)
            likes = self._get_likes(post)

            if data_id and img_link:
                self.last_id = data_id
                print(data_id, img_link, likes)

        print("==================================================================================")

    def _get_page_content(self, url, firstPage=False):
        page = requests.get(url)
        if firstPage:
            return page.content

        data = page.json()['data']
        self.last_id = data['last_id']
        self.last_sorting_value = data['last_sorting_value']

        return data['items_html']
