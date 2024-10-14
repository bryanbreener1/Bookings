import pandas as pd
from dbfread import DBF
from cors_config import HEADERS_OPTIONS_POST, HEADERS_ORIGIN
import traceback
from flask import Flask, request
from flask import jsonify
import logging
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from constantes import PEDIDO_D_PATH, PRODUCTO_PATH, CLIENTS_VP_PATH, SUBZONAS_VP_PATH, PRODUCTO_VP_PATH, PRECIPROD_VP_PATH
import json
app = Flask(__name__)

logger = logging.getLogger('server_logger')
handler = logging.FileHandler('server.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

#CORESUITES
@app.route('/availabilityCategory', methods=['GET', 'OPTIONS', 'POST'])
def availabilityCategory():
    if request.method == 'OPTIONS':
            return ('', 204, HEADERS_OPTIONS_POST)

    try:
        pedidod_db = PEDIDO_D_PATH
        pedido_decoded = DBF(pedidod_db, encoding='cp1252')  
        pedidos = pd.DataFrame(iter(pedido_decoded))

        product_db = PRODUCTO_PATH
        product_decoded = DBF(product_db, encoding='cp1252')  
        products = pd.DataFrame(iter(product_decoded))

        rooms_busy = []
        rooms_per_category_availables = []
 
        check_in = datetime.strptime(request.args.get('check_in'),'%Y-%m-%d %H:%M:%S.%f')
        check_out = datetime.strptime(request.args.get('check_out'), '%Y-%m-%d %H:%M:%S.%f')
        
        for index, row in pedidos.iterrows():
            if row['FECHA_ENT'] == None:
                continue

            if isinstance(row['FECHA_ENT'], date) and not isinstance(row['FECHA_ENT'], datetime):
                pedido_check_in = datetime.combine(row['FECHA_ENT'], datetime.min.time())
            else:
                pedido_check_in = row['FECHA_ENT']
            total_months = int(row['CANT_PROD'])
            years = total_months // 12
            months = total_months % 12

            pedido_check_out = pedido_check_in + relativedelta(years=years, months=months)

            if not (pedido_check_out <= check_in or pedido_check_in >= check_out):
                categoryName = next((room['CSE_PROD'] + ' con terraza' if room['CVEDE1'] == 2 else room['CSE_PROD'] for index, room in products.iterrows() if room['CVE_PROD'] == row['CVE_PROD']),None)
                rooms_busy.append({'productKey':row['CVE_PROD'], "category":categoryName})         

        for index, product in products.iterrows():
            categoryName = product['CSE_PROD'] + ' con terraza' if product['CVEDE1'] == 2 else product['CSE_PROD']
            is_different_key = not (product['CVE_PROD'] in [room['productKey'] for room in rooms_busy])
            if (product['CSE_PROD'] == 'SUITES' or product['CSE_PROD'] == 'JUNIORSUIT') and is_different_key:
                if categoryName not in [prod['categoryName'] for prod in rooms_per_category_availables]:
                    rooms_per_category_availables.append({
                    "availabilityStatus": "available",
                    "description": product['DESC_PROD'],
                    "isFurnished": True if product['CVEDE3'] == 1 else False,
                    "name": product['DESC_PROD'],
                    "parkName": "CoreSuites",
                    "price": 0,
                    "productType": "Renta",
                    "quantity": 1,
                    "status": "active",
                    "stock": 1,
                    "unity": "m2",
                    "categoryName":categoryName,
                    "productKey": product['CVE_PROD']
                    })
        
        return jsonify({"rooms": rooms_per_category_availables}), 200, HEADERS_ORIGIN

    except Exception as e:
            tb = traceback.format_exc()
            error = f"An error occurred: {e}, traceback: {tb}"
            logger.error({"CORESUITES": error})
            result = jsonify({"error": error, "tb": tb})
            return (result, 500, HEADERS_ORIGIN)

#CORESUITES
@app.route('/roomsByCategory', methods=['GET', 'OPTIONS', 'POST'])
def roomsByCategory():
    if request.method == 'OPTIONS':
            return ('', 204, HEADERS_OPTIONS_POST)

    try:
        pedidod_db = PEDIDO_D_PATH
        pedido_decoded = DBF(pedidod_db, encoding='cp1252')  
        pedidos = pd.DataFrame(iter(pedido_decoded))

        product_db = PRODUCTO_PATH
        product_decoded = DBF(product_db, encoding='cp1252')  
        products = pd.DataFrame(iter(product_decoded))
        
        rooms_busy = []
        rooms_availables = []
 
        check_in = datetime.strptime(request.args.get('check_in'),'%Y-%m-%d %H:%M:%S.%f')
        check_out = datetime.strptime(request.args.get('check_out'), '%Y-%m-%d %H:%M:%S.%f')
        category = request.args.get('category')
        category = category.replace("'", '"')

        category =json.loads(category)

        for index, row in pedidos.iterrows():
            if row['FECHA_ENT'] == None:
                continue

            if isinstance(row['FECHA_ENT'], date) and not isinstance(row['FECHA_ENT'], datetime):
                pedido_check_in = datetime.combine(row['FECHA_ENT'], datetime.min.time())
            else:
                pedido_check_in = row['FECHA_ENT']
                

            total_months = int(row['CANT_PROD'])
            years = total_months // 12
            months = total_months % 12

            pedido_check_out = pedido_check_in + relativedelta(years=years, months=months)

            if not (pedido_check_out <= check_in or pedido_check_in >= check_out):
                #categoryName = next((room['CSE_PROD'] + ' con terraza' if room['CVEDE1'] == 2 else room['CSE_PROD'] for index, room in products.iterrows() if room['CVE_PROD'] == row['CVE_PROD']),None)
                rooms_busy.append({'productKey':row['CVE_PROD']})
                     
        for index, product in products.iterrows():
            categoryName = 'SUITE' if product['CSE_PROD'] == 'SUITES' else 'JR SUITE'
            categoryName = categoryName + ' CON TERRAZA' if product['CVEDE1'] == 2 else categoryName
            is_different_key = not (product['CVE_PROD'] in [room['productKey'] for room in rooms_busy])

            if (categoryName in category) and is_different_key and (product['CSE_PROD'] == 'SUITES' or product['CSE_PROD'] == 'JUNIORSUIT'): 
                rooms_availables.append({
                "availabilityStatus": "available",
                "description": product['DESC_PROD'],
                "isFurnished": True if product['CVEDE3'] == 1 else False,
                "name": product['DESC_PROD'],
                "parkName": "CoreSuites",
                "price": 0,
                "productType": "Renta",
                "quantity": 1,
                "status": "active",
                "stock": 1,
                "unity": "m2",
                "categoryName":categoryName,
                "productKey": product['CVE_PROD']
                })
        
        return jsonify(rooms_availables), 200, HEADERS_ORIGIN

    except Exception as e:
            tb = traceback.format_exc()
            error = f"An error occurred: {e}, traceback: {tb}"
            logger.error({"CORESUITES": error})
            result = jsonify({"error": error, "tb": tb})
            return (result, 500, HEADERS_ORIGIN)

#VILLA PLATA
departamentos = [215,307,306,214,507,314,315,207,514,515,415,406,506,407,414,407]
def getRoomsAvailable():
    client_db = CLIENTS_VP_PATH
    client_decoded = DBF(client_db, encoding='cp1252')  
    clients = pd.DataFrame(iter(client_decoded))
    
    sub_zonas_db = SUBZONAS_VP_PATH
    sub_zonas_decoded = DBF(sub_zonas_db, encoding='cp1252')
    sub_zonas = pd.DataFrame(iter(sub_zonas_decoded))
    
    rooms_busy = []
    for index, row in clients.iterrows():
        if(row['CVEDE3'] == 1 and row['CVE_SUB'] != 99999):
            rooms_busy.append(row['CVE_SUB'])
            
    rooms_available = []
    for index, row in sub_zonas.iterrows():
        if(row['CVE_SUB'] not in rooms_busy and row['CVE_SUB'] != 99999):
            rooms_available.append({
                "CVE_ZON": row['CVE_ZON'],
                "CVE_SUB":row['CVE_SUB'],
                "NOM_SUB":row['NOM_SUB'],
                "typeName": "departamento" if row['CVE_SUB'] in departamentos else "habitación",
                "type": 2 if row['CVE_SUB'] in departamentos else 1
            })
            
    return rooms_available

def getPriceProducts():
    products_db = PRODUCTO_VP_PATH
    products_decoded = DBF(products_db, encoding='cp1252')
    products = pd.DataFrame(iter(products_decoded))
    
    prices_db = PRECIPROD_VP_PATH
    prices_decoded = DBF(prices_db, encoding='cp1252')
    prices = pd.DataFrame(iter(prices_decoded))
    
    products_relevants = []
    for index, row  in products.iterrows():
        if row['CSE_PROD'] == 'RESIDENTES':
            products_relevants.append(row)
    
    price_per_product = []
    for index, row in prices.iterrows():
        if row['CVE_PROD'] in [product['CVE_PROD'] for product in products_relevants]:
            price_per_product.append({
                "clave_Prod": row['CVE_PROD'],
                "type": row['NLISPRE'],
                "price": row['LPRECPROD']
            })
    return price_per_product

@app.route('/availability_villa_plata', methods=['GET', 'POST', 'OPTIONS'])
def availability():
    if request.method == 'OPTIONS':
        return ('', 204, HEADERS_OPTIONS_POST)

    try:
        rooms_availables = getRoomsAvailable()
        if len(rooms_availables) > 0:
            return jsonify(rooms_availables), 200, HEADERS_ORIGIN
        else:
            logger.info({"VILLAPLATA": "se hizo una solicitud con exito a availability_villa_plata"})
            return jsonify([]), 200, HEADERS_ORIGIN

    except Exception as e:
            tb = traceback.format_exc()
            error = f"An error occurred: {e}, traceback: {tb}"
            logger.error({"VILLAPLATA": error})
            result = jsonify({"error": error, "tb": tb})
            return (result, 500, HEADERS_ORIGIN)

@app.route('/prices_villa_plata', methods=['GET', 'POST', 'OPTIONS'])
def prices():
    if request.method == 'OPTIONS':
        return ('', 204, HEADERS_OPTIONS_POST)

    try:
        rooms_availables = getRoomsAvailable()
        if len(rooms_availables) > 0:
            prices = getPriceProducts()
            return jsonify(prices), 200, HEADERS_ORIGIN
        else:
            logger.info({"VILLAPLATA": "se hizo una solicitud con exito a prices_villa_plata"})
            return jsonify([]), 200, HEADERS_ORIGIN

    except Exception as e:
            tb = traceback.format_exc()
            error = f"An error occurred: {e}, traceback: {tb}"
            logger.error({"VILLAPLATA": error})
            result = jsonify({"error": error, "tb": tb})
            return (result, 500, HEADERS_ORIGIN)
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
