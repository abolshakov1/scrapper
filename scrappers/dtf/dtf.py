import requests

from bs4 import BeautifulSoup as _bs

from db_layer.db import DbConnection


class DtfScrapper:
    _url_first_page = "https://dtf.ru/kek/"
    _url_more = "https://dtf.ru/kek/more?"

    _page = 1
    _last_id = None
    _last_sorting_value = None
    _min_likes_to_download = 30
    _db = DbConnection()

    def scrap_best_pages(self, count=3):
        result = []

        for i in range(count):
            first_page = i == 0

            if first_page:
                url = self._url_first_page
            else:
                url = self._url_more + f'last_id={self._last_id}' \
                                      f'&page={self._page}' \
                                      f'&last_sorting_value={self._last_sorting_value}' \
                                      f'mode=raw'

            content = self._get_page_content(url, first_page)
            records = self._parse(content, first_page)
            result.extend(records)

            self._page += 1

        self._save_content(result)
        self._clear()

    def _save_content(self, records: list):
        self._db.open_connection()
        self._db.insert_many_dtf_records(records)
        self._db.close_connection()

    def _get_last_sorting_value_from_first_page(self, soup):
        last_sorting_value_div = soup.find('div', class_='feed')
        last_sorting_value = last_sorting_value_div.attrs['data-feed-last-sorting-value']
        if last_sorting_value:
            self._last_sorting_value = last_sorting_value

    def _get_data_id(self, post):
        favorite_marker = post.find('div', class_='favorite_marker')
        return favorite_marker.attrs['data-id'] if favorite_marker else None

    def _get_img_link(self, post):
        img_div = post.find('div', class_='andropov_image')
        return img_div.attrs['data-image-src'] if img_div else None

    def _get_likes(self, post):
        likes_span = post.find('span', class_='vote__value__v')
        likes_count = 0

        if likes_span:
            try:
                likes_count = int(likes_span.text)
            except ValueError:
                likes_count = 0

        return likes_count

    def _parse(self, content, first_request=True):
        print("==================================================================================")

        soup = _bs(content, "html.parser")
        if first_request:
            self._get_last_sorting_value_from_first_page(soup)

        posts = soup.find_all("div", class_='feed__item l-island-round')
        records = []

        for post in posts:
            data_id = self._get_data_id(post)
            img_link = self._get_img_link(post)
            likes = self._get_likes(post)

            if data_id and img_link:
                self._last_id = data_id
                print(data_id, img_link, likes)

                if likes < self._min_likes_to_download:
                    print(f'Skipped{data_id} not enough likes {likes}')
                    continue

                record = (data_id, img_link, likes)
                records.append(record)

        print("==================================================================================")
        return records

    def _get_page_content(self, url, first_page=False):
        page = requests.get(url)
        if first_page:
            return page.content

        data = page.json()['data']
        self._last_id = data['last_id']
        self._last_sorting_value = data['last_sorting_value']

        return data['items_html']

    def _clear(self):
        self._page = 1
        self._last_id = None
        self._last_sorting_value = None


if __name__ == "__main__":
    scrapper = DtfScrapper()
