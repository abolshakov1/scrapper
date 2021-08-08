import shutil
import json
import requests
import wget

import os, sys

def download_image(url) -> str:

    # application_path = os.path.dirname(sys.executable)

    path = os.path.expanduser('~/Documents/scrapper/images/')

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
