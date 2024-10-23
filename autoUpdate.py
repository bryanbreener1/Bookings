import pandas as pd
from dbfread import DBF
import math 
import requests
import logging
from constantes import PRODUCTO_PATH, END_POINT_CLOUD_FUNCTIONS, PRECIOS_PATH, PRODUCTO_VP_PATH, PRECIPROD_VP_PATH

logger = logging.getLogger('autoupdate_logger')
handler = logging.FileHandler('autoUpdate.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

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
        logger.info(f"Cloud Function response: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logger.error(f"error in update_prices_auto: {e}")

#funcion para actualizar productos, se ejecuta cuando watchDog detecta un cambio
def update_products_auto():
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
                "productKey": product['CVE_PROD']
            })
            
    server_data = {"products": product_list}
    try:
        response = requests.post(f'{END_POINT_CLOUD_FUNCTIONS}/update_products', json=server_data)
        response.raise_for_status() 
        logger.info(f"Cloud Function response: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logger.error(e)
        
#update villa plata products     
def update_products_auto_VP():
    product_db = PRODUCTO_VP_PATH
    product_decoded = DBF(product_db, encoding='cp1252')  
    products = pd.DataFrame(iter(product_decoded))

    price_prod_db = PRECIPROD_VP_PATH
    price_decoded = DBF(price_prod_db, encoding='cp1252')  
    prices = pd.DataFrame(iter(price_decoded))

    product_list = []
    rent_prices = []
    for index, product in products.iterrows():
        if product['CSE_PROD'] == 'RESIDENTES':
            product_list.append({
                "CSE_PROD": product['CSE_PROD'],
                "productKey": product['CVE_PROD'],
                "description": product['DESC_PROD'],
                "priceVP":[],
                "parkName": "Villa Plata"
            })
            
    product_list_cve = [product['productKey'] for product in product_list]
    prices_room_type = [product for index, product in prices.iterrows() if product['CVE_PROD'] == 'RENTA']

    for index, prices in prices.iterrows():
        indice = product_list_cve.index(prices['CVE_PROD']) if prices['CVE_PROD'] in product_list_cve else -1
        
        if indice != -1:
            price_type = [precio for precio in prices_room_type if precio['NLISPRE'] == prices['NLISPRE']]
            product_list[indice]['price'] = round(prices['LPRECPROD'],2)
            product_list[indice]['priceVP'].append({
                    "type": prices['NLISPRE'],
                    "typeName": "habitación" if prices['NLISPRE'] == 1 else "departamento",
                    "price": round(prices['LPRECPROD'] + price_type[0]['LPRECPROD'],2)
            })                        
    server_data = {"products": product_list}
    try:
        response = requests.post(f'{END_POINT_CLOUD_FUNCTIONS}/update_products_villa_plata', json=server_data)
        response.raise_for_status() 
        logger.info(f"Cloud Function response: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logger.error({"VILLAPLATA-autoupdate": e})
