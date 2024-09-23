import requests
import logging
from constantes import END_POINT_CLOUD_FUNCTIONS

logging.basicConfig(filename='ngrok_url.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')

ngrok_api_url = 'http://localhost:4040/api/tunnels'
response = requests.get(ngrok_api_url)
if response.status_code == 200:
    tunnels = response.json()
    # Obtiene el primer túnel de la lista
    public_url = tunnels['tunnels'][0]['public_url']
    url = {"new_url": public_url}
    try:
        response = requests.post(f'{END_POINT_CLOUD_FUNCTIONS}/update_ngrok_url', json=url)
        response.raise_for_status() 
        logging(f"La URL pública de ngrok es: {public_url}")

    except requests.exceptions.RequestException as e:
        logging.error(e)
 
else:
    logging.error("No se pudo obtener la URL de ngrok.")