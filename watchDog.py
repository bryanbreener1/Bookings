import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from autoUpdate import update_prices_auto, update_products_auto, update_products_auto_VP
import logging
from constantes import DIR_TO_WATCH, PRECIOS_PATH, PRODUCTO_PATH, PRECIPROD_VP_PATH, PRODUCTO_VP_PATH, DIR_TO_WATCH_VP

logger = logging.getLogger('watchdog_logger')
handler = logging.FileHandler('nucleaWatchDog.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info('Script Watchdog iniciado')

class Watcher:
    def __init__(self, directory_to_watch):
        self.directory_to_watch = directory_to_watch
        self.event_handler = Handler()
        self.observer = Observer()

    def run(self):
        for directory in self.directory_to_watch:
            self.observer.schedule(self.event_handler, directory, recursive=False)
            logger.info(f"Observando cambios en el directorio: {directory}")
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Observador detenido. Cerrando programa.")
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_modified(event):        
        if not event.is_directory:
            if event.src_path == PRECIOS_PATH:
                logger.info('Detecté un cambio en PRECIPROD.DBF')
                update_prices_auto()
            elif event.src_path == PRODUCTO_PATH:
                logger.info('Detecté un cambio en PRODUCTO.DBF')
                update_products_auto()
            elif event.src_path == PRODUCTO_VP_PATH:
                logger.info('Detecté un cambio en PRODUCTO_VP.DBF')
                update_products_auto_VP()

if __name__ == '__main__':

    if not os.path.isfile(PRECIOS_PATH):
        logger.info(f"El archivo {PRECIOS_PATH} no existe.")
    else:
        logger.info(f"Archivo a observar: {PRECIOS_PATH}")
        
    if not os.path.isfile(PRODUCTO_PATH):
        logger.info(f"El archivo {PRODUCTO_PATH} no existe.")
    else:
        logger.info(f"Archivo a observar: {PRODUCTO_PATH}")
        
    if not os.path.isfile(PRODUCTO_VP_PATH):
        logger.info(f"El archivo {PRODUCTO_VP_PATH} no existe.")
    else:
        logger.info(f"Archivo a observar: {PRODUCTO_VP_PATH}")
    # Iniciar Watcher
    w = Watcher([DIR_TO_WATCH, DIR_TO_WATCH_VP ])
    w.run()
