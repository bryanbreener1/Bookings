import os
import pandas as pd
from dbfread import DBF

# Ruta al archivo .dbf que deseas convertir
dbf_file = 'C:\VSAI\Empresas\DEMO\PRODUCTO.DBF'  # Cambia 'nombre_del_archivo.dbf' por el nombre del archivo específico

# Ruta a la carpeta donde se guardará el archivo .xlsx
output_folder = './'

# Crear la carpeta de salida si no existe
os.makedirs(output_folder, exist_ok=True)

# Leer el archivo .dbf
table = DBF(dbf_file, encoding='cp1252')  # Ajusta el encoding si es necesario

# Convertir el archivo .dbf a un DataFrame de pandas
df = pd.DataFrame(iter(table))
print(df)

# Construir la ruta del archivo .xlsx de salida en la carpeta de destino
xlsx_file = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(dbf_file))[0]}.xlsx")

# Guardar el DataFrame como un archivo .xlsx
df.to_excel(xlsx_file, index=False)

print(f'Archivo {dbf_file} convertido y guardado como {xlsx_file}')

print('Conversión completada para el archivo especificado.')
