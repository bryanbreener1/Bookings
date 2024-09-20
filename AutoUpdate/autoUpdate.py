import pandas as pd
from dbfread import DBF
import math 
import requests
from constantes import PRODUCTO_PATH, END_POINT_CLOUD_FUNCTIONS, PRECIOS_PATH
import logging
import sys
import os

sys.path.append(os.path.abspath('..'))

logging.basicConfig(filename='autoUpdate.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')

#funcion para actualizar precios, se ejecuta cuando watchDog detecta un cambio
def update_prices_auto():
    price_prod_db = PRECIOS_PATH
    price_decoded = DBF(price_prod_db, encoding='cp1252')  
    prices = pd.DataFrame(iter(price_decoded))
    schemes_to_update = []
    for index, row in prices.iterrows():
        schemes_to_update.append({
            "amountWithDiscount": int(row['LPRECPROD']),
            "days": math.ceil(row['LEXCDESD']) * 30,
            "productKey": row['CVE_PROD']
        })

    server_data = {"server_data": schemes_to_update}
    try:
        response = requests.post(f'{END_POINT_CLOUD_FUNCTIONS}/update_prices_coming_from_core_server', json=server_data)
        response.raise_for_status() 
        logging.info(f"Cloud Function response: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"error in update_prices_auto: {e}")




#funcion para actualizar productos, se ejecuta cuando watchDog detecta un cambio
def update_products_auto():
    print('ejecuto la funcion update products auto')
    product_db = PRODUCTO_PATH
    product_decoded = DBF(product_db, encoding='cp1252')  
    products = pd.DataFrame(iter(product_decoded))

    price_prod_db = PRECIOS_PATH
    price_decoded = DBF(price_prod_db, encoding='cp1252')  
    prices = pd.DataFrame(iter(price_decoded))

    product_list = []

    for index, product in products.iterrows():
        if product['CSE_PROD'] == 'SUITES' or product['CSE_PROD'] == 'JUNIORSUIT':
            price = prices[(prices['CVE_PROD'] == product['CVE_PROD']) & (prices['NLISPRE'] == 1)]['LPRECPROD']
            categoryName = 'SUITE' if product['CSE_PROD'] == 'SUITES' else 'JR SUITE'
            product_list.append({
                "availabilityStatus": "available",
                "description": product['DESC_PROD'],
                "isFurnished": True if product['CVEDE3'] == 1 else False,
                "name": product['DESC_PROD'],
                "parkName": "CoreSuites",
                "price": float(price.iloc[0]) if not price.empty else 0,
                "productType": "Renta",
                "quantity": 1,
                "status": "active",
                "stock": 1,
                "unity": "m2",
                "categoryName": categoryName + ' CON TERRAZA' if product['CVEDE1'] == 2 else categoryName,
                "productKey": int(product['CVE_PROD']) 
            })
            
    server_data = {"products": product_list}
    try:
        print('envio la peticion al GCP')
        response = requests.post(f'{END_POINT_CLOUD_FUNCTIONS}/update_products', json=server_data)
        response.raise_for_status() 
        logging.info(f"Cloud Function response: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(e)

