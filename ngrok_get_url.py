import requests
import logging
from constantes import END_POINT_CLOUD_FUNCTIONS

logger = logging.getLogger('ngrok_url_logger')
handler = logging.FileHandler('ngrok_url.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

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