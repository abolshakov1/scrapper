import shutil
import requests

import os

def download_images(urls: list, dir_name: str) -> None:
    home = os.path.expanduser('~/scrapper/images/')
    path = os.path.join(home, dir_name+'/')
    try:
        os.mkdir(path)
    except FileExistsError as exc:
        pass
    
    # path.join('/')
    for url in urls:
        download_image(url, path)


def download_image(url: str, path: str) -> None:
    r = requests.get(url, stream=True)
    try:
        name = url.split('/')[-2] + ".jpg"
        if r.status_code == 200:
            with open(path + name, 'wb+') as file:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, file)
                print('Image hase been saved successfully', file)
    except Exception as exc:
        print (exc)
