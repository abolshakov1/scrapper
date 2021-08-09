import requests
from datetime import datetime
import json
from bs4 import BeautifulSoup as _bs

from downloader import download_image
from stats.stats_helper import get_stats_from_file, save_to_file

class DtfScrapper:
    url = "https://dtf.ru/kek/"
    new_url = "https://dtf.ru/kek/entries/new/"
    url_more = "https://dtf.ru/kek/more?"

    page = 1
    last_id = None
    last_sorting_value = None
    min_likes_to_download = 30

    stats = None
    new_imgs = []

    def __init__(self):
        self.stats = get_stats_from_file()

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

        save_to_file(self.stats)

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

                if likes < self.min_likes_to_download:
                    print (f'Skipped{data_id} not enought likes {likes}')
                    continue
                if str(data_id) in self.stats or \
                   self.stats.get(str(data_id), {}).get('downloaded', False):
                   print(f'Skipped {data_id} already in list')
                   continue

                self._update_record(data_id, img_link, likes)
        print("==================================================================================")
        self._download_new_imgs()

    def _update_record(self, data_id, img_link, likes):
        self.stats[data_id] = { 'link': img_link,
                                'likes': likes,
                                'updated_at': datetime.now().ctime(),
                                'processed': False,
                                'downloaded': False}
        self.new_imgs.append(data_id)

    def _download_new_imgs(self):
        for id_ in self.new_imgs:
            url = self.stats[id_]['link']
            download_image(url)
            self.stats[id_]['downloaded'] = True

        self.new_imgs.clear()


    def _get_page_content(self, url, firstPage=False):
        page = requests.get(url)
        if firstPage:
            return page.content

        data = page.json()['data']
        self.last_id = data['last_id']
        self.last_sorting_value = data['last_sorting_value']

        return data['items_html']
