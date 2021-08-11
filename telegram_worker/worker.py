import requests

api_request = 'https://api.telegram.org/bot'
bot_token = '1903625927:AAEksNDK1GupjYl_LOPI-kd0aaWyfxSIOv0'

bot_request = api_request + bot_token + '/'

hurma_id = '-1001560567257'



def send_message(text: str):
    url = bot_request + 'sendMessage?' + 'chat_id=' + hurma_id + '&text=' + text 
    requests.get(url)

def send_photo(photo_link: str):
    url = bot_request + 'sendPhoto?' + 'chat_id=' + hurma_id + '&photo=' + photo_link
    requests.get(url)


photo_link = 'https://leonardo.osnova.io/d1755d33-6e36-5676-b28f-0a00ac446873/'
send_photo(photo_link)
# send_message('hello world')