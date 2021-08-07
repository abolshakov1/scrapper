import shutil

import requests


def download_image(url) -> str:
    r = requests.get(url, stream=True)
    try:
        name = url.split('/')[-2] + ".jpg"
        if r.status_code == 200:
            with open(".\\images\\" + name, 'wb') as file:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, file)
                print('Image hase been saved successfully')
    except Exception as exc:
        print (exc)