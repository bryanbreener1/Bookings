import pandas as pd
from dbfread import DBF
from cors_config import HEADERS_OPTIONS_POST, HEADERS_ORIGIN
import traceback
from flask import Flask, request
from flask import jsonify
import logging
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
import json
import config_imports
from constantes import PEDIDO_C_PATH, PEDIDO_D_PATH, PRODUCTO_PATH

app = Flask(__name__)

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
                    "productKey": int(product['CVE_PROD']) 
                    })
        
        return jsonify({"rooms": rooms_per_category_availables}), 200, HEADERS_ORIGIN

    except Exception as e:
            tb = traceback.format_exc()
            error = f"An error occurred: {e}, traceback: {tb}"
            logging.error(error)
            result = jsonify({"error": error, "tb": tb})
            return (result, 500, HEADERS_ORIGIN)

        
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
        #category =json.loads( request.args.get('category'))
        category =request.args.get('category')
        print(category)
        print(type(category))

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
            if (categoryName in category) and is_different_key: 
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
                "productKey": int(product['CVE_PROD']) 
                })
        
        return jsonify(rooms_availables), 200, HEADERS_ORIGIN

    except Exception as e:
            tb = traceback.format_exc()
            error = f"An error occurred: {e}, traceback: {tb}"
            logging.error(error)
            result = jsonify({"error": error, "tb": tb})
            return (result, 500, HEADERS_ORIGIN)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
