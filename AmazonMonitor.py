import requests
from bs4 import BeautifulSoup
import lxml
import requests
from bs4 import BeautifulSoup
from gevent.time import sleep

channeltelegram="-1002213667762"
channelSupreme='-1002207629021' #

#telegram function
def send_telegram_message(chat_id, text):
    base_url = "https://api.telegram.org/bot8153422759:AAHKQ50YVJj0w-ufRAtksHsPlvyvQZJR9-w/sendMessage"
    parameters = {
        "chat_id": chat_id,
        "text": text
    }
    resp = requests.get(base_url, params=parameters)
    return resp.text

def send_telegram_image(file, chat_id):
    base_url = "https://api.telegram.org/bot8153422759:AAFCqTnWNHvVnq-vA2jdUob31NLO3cIC6pQ/sendPhoto"
    parameters = {
        "chat_id": chat_id,  # questo è il codice chat lo trovi con RAWDATABOT BOT DI TELEGRAM AGGIUNGENDO IN CHAT

    }
    my_file = open(file, "rb")
    files = {
        "photo": my_file
    }
    resp = requests.get(base_url, data=parameters, files=files)
    print(resp.text)

def carica_link_prodotti(nome_file):
    try:
        with open(nome_file, 'r') as file:
            # Legge ogni riga del file e rimuove gli spazi bianchi (es. newline)
            lista_prodotti = [line.strip() for line in file if line.strip()]
        return lista_prodotti
    except FileNotFoundError:
        print(f"Il file {nome_file} non è stato trovato.")
        return []


def checkProdotti(link):
    URL = link
    headers = {
        'Accept-Language': "en-US,en;q=0.9",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }

    # Send a request to the URL
    response = requests.get(URL, headers=headers)

    flag = -1  # Default flag set to -1 (out of stock) initially
    name = "Title not found"  # Default title if not found
    price_message = "Price data not found."  # Default price message if not found

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, "lxml")

        # Extract the product title
        if soup.find(id="productTitle"):
            name = soup.find(id="productTitle").get_text().strip()

        '''
        #soup = BeautifulSoup(get_url.text, "html.parser")  # parsing the content of page to html parser
        sub_class = soup.find("div", {"id": "availability"})  # finding that particular div
        if sub_class:  # above result can be none so checking if result is not none
            print("availability : {}".format(sub_class.find("span", {
                "class": "a-size-medium a-color-success"}).text.strip()))  # if result is not none then finding sub class which is span and getting the text of span
        '''

        # Check if the "out of stock" div is present
        out_of_stock_div = soup.find("div", id="outOfStock")
        if out_of_stock_div:
            flag = -1  # Set flag to -1 if out of stock
            price_message = "The product is out of stock."
        else:
            flag = 1  # Set flag to 1 if in stock
            price_message = "The product is in stock."

            # Extract and set price if the product is in stock
            price_data = soup.find("span", class_="a-offscreen")
            if price_data:
                price = price_data.get_text()
                price_message = f"The price is: {price}"

    else:
        price_message = f"Failed to retrieve the page. Status code: {response.status_code}"

    return [flag, link, name, price_message]


##################################################
#main
# URL of the Amazon product page you want to monitor
while(True):
    lista_prodotti = carica_link_prodotti("listaProdotti.txt")

    for link in lista_prodotti:
        ris = checkProdotti(link)

        # Formatting the output based on product availability
        if ris[0] == 1:
            message = (
                f"✅ In Stock: {ris[2]}\n"
                f"   URL: {ris[1]}\n"
                f"   Price: {ris[3]}"
            )
            print(message)
            send_telegram_message(channeltelegram, message)
        else:
            message = (
                f"❌ Out of Stock: {ris[2]}\n"
                f"   URL: {ris[1]}"
            )

        # Sending the formatted message to the specified Telegram channel
        #print(message)
    #send_telegram_message(channelSupreme, "Status: on, check done")

    sleep(300)
