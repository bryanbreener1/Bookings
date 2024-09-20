import requests
import logging

""" logging.basicConfig(filename='ngrok_url.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s') """

ngrok_api_url = 'http://localhost:4040/api/tunnels'
response = requests.get(ngrok_api_url)
if response.status_code == 200:
    tunnels = response.json()
    # Obtiene el primer túnel de la lista
    public_url = tunnels['tunnels'][0]['public_url']
    print(public_url)
    url = {"new_url": public_url}
    try:
        response = requests.post(f'https://us-central1-ore-dev-32608.cloudfunctions.net/update_ngrok_url', json=url)
        response.raise_for_status() 
        print(f"La URL pública de ngrok es: {public_url}")

    except requests.exceptions.RequestException as e:
        print(e)
 
else:
    print("No se pudo obtener la URL de ngrok.")