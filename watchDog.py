import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from autoUpdate import update_prices_auto, update_products_auto
import logging
from constantes import DIR_TO_WATCH, PRECIOS_PATH, PRODUCTO_PATH

logging.basicConfig(filename='nucleaWatchDog.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')

logging.info('Script Watchdog iniciado')

class Watcher:
    def __init__(self, directory_to_watch):
        self.directory_to_watch = directory_to_watch
        self.event_handler = Handler()
        self.observer = Observer()

    def run(self):
        self.observer.schedule(self.event_handler, self.directory_to_watch, recursive=False)
        self.observer.start()
        logging.info(f"Observando cambios en el directorio: {self.directory_to_watch}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Observador detenido. Cerrando programa.")
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_modified(event):        
        if not event.is_directory:
            if event.src_path == PRECIOS_PATH:
                logging.info('Detecté un cambio en PRECIPROD.DBF')
                update_prices_auto()
            elif event.src_path == PRODUCTO_PATH:
                logging.info('Detecté un cambio en PRODUCTO.DBF')
                update_products_auto()

if __name__ == '__main__':

    if not os.path.isfile(PRECIOS_PATH):
        logging.info(f"El archivo {PRECIOS_PATH} no existe.")
    else:
        logging.info(f"Archivo a observar: {PRECIOS_PATH}")
        
    if not os.path.isfile(PRODUCTO_PATH):
        logging.info(f"El archivo {PRODUCTO_PATH} no existe.")
    else:
        logging.info(f"Archivo a observar: {PRODUCTO_PATH}")

    # Iniciar Watcher
    w = Watcher(DIR_TO_WATCH)
    w.run()
