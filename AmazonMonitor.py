import requests
from bs4 import BeautifulSoup
import lxml
import requests
from bs4 import BeautifulSoup
from gevent.time import sleep
import csv

channeltelegram = "-1002213667762"
channelSupreme = '-1002207629021'  #


# telegram function
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


# Function to load and read the CSV file
def load_csv(file_path):
    data = []

    # Open the CSV file for reading
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file)

        # Skip the header row
        header = next(csv_reader, None)
        if not header or len(header) < 2:
            print("Error: CSV file does not have the expected format (at least two columns).")
            return []

        # Read the rows in the CSV file
        for row in csv_reader:
            # Skip empty rows or rows with insufficient columns
            if not row or len(row) < 2:
                continue

            # Extract the availability and product link from each row
            availability = row[0].strip()
            link = row[1].strip()

            # Ensure valid data is present before adding it to the list
            if availability and link:
                data.append({"Old_Available": availability, "Product Link": link})
            else:
                print(f"Skipping invalid row: {row}")

    return data


# Save CSV data
def save_csv(file_path, data, fieldnames):
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


##################################################
# main
send_telegram_message('-1002469064066', 'check')
# Load the CSV data into 'products'
products = load_csv("listaProdotti.csv")
output = []  #crea una struttura dati con prodotto link, disponibita old salvata , e ris check in cui conterra la nuova disponibilta e altre info
print('Checking new status of the products...\n')
for product in products:
    old_available = product.get('Old_Available')  # Get the 'Old_Available' value
    print('old available statusl:',old_available)
    product_link = product.get('Product Link')  # Get the 'Product Link' value

    try:
        # Check product availability and store results in 'ris'
        ris = checkProdotti(product_link)
        output.append({'Product Link': product_link, 'Old_Available': old_available, 'Check Result': ris})
        print(ris)  # Print result for each product
        print('------------------------------------')
    except Exception as e:
        print(f"Error checking product {product_link}: {e}")



# Prepare data for CSV output
updated_data = []

# Process each item
for item in output:
    old_available = item['Old_Available']
    new_available = item['Check Result'][0]
    product_link = item['Product Link']

    # Check if availability has changed
    if str(old_available) != str(new_available):
        change = f"Availability status changed for product {product_link}. Old: {old_available}, New: {new_available}"
        print(change)
        if(int(old_available)==-1 and int(new_available)==1): #questo e unico caso che senda un mex

            message = (
                f"✅ In Stock: {item['Check Result'][2]}\n"
                f"   URL: {item['Check Result'][1]}\n"
                f"   Price: {item['Check Result'][3]}"
            )
            print(message)
            send_telegram_message(channeltelegram, message)




    # Append to updated data with the new availability
    updated_data.append({'Available': new_available, 'Product Link': product_link})

# Write to CSV
csv_file_path = 'listaProdotti.csv'
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['Available', 'Product Link'])
    writer.writeheader()
    writer.writerows(updated_data)

print(f"Data saved to {csv_file_path}")





