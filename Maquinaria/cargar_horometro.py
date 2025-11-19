import pandas as pd
import mysql.connector
from datetime import datetime

# --- CONFIGURACIÓN DE CONEXIÓN ---
config = {
    'host': '135.148.188.205',
    'port': 3306,
    'user': 'cso60906_dba',
    'password': 'Miscka-2025',
    'database': 'cso60906_Equipos'
}

# --- ARCHIVO Y TABLA ---
excel_file = '09-11.xlsx'
table_name = 'tdHorometro'
RUT_DEFECTO = 99999999  # operador genérico

try:
    # Leer el Excel
    df = pd.read_excel(excel_file)
    print(f"✅ Archivo '{excel_file}' leído correctamente. Registros encontrados: {len(df)}")

    # Normalizar nombres de columnas
    df.columns = df.columns.map(lambda x: str(x).strip())

    # Quitar columnas sin nombre
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False, na=False)]
    print(f"🧹 Columnas detectadas: {list(df.columns)}")

    id_col = df.columns[0]
    date_cols = df.columns[1:]

    # Mostrar encabezados de fechas para depuración
    print(f"📅 Encabezados de fechas detectados: {list(date_cols)}")

    # Reemplazar NaN por None
    df = df.where(pd.notnull(df), None)

    # Conexión MySQL
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("✅ Conexión establecida con la base de datos.")

    # Vaciar tabla
    cursor.execute(f"DELETE FROM `{table_name}`")
    conn.commit()
    print(f"⚠️ Todos los registros de '{table_name}' fueron eliminados antes de la carga.")

    # Insert SQL
    insert_query = f"""
        INSERT INTO `{table_name}` (`idTxt_Ppu`, `idNum_Rut`, `dtFec_Registro`, `dtNum_Horometro`)
        VALUES (%s, %s, %s, %s)
    """

    total_insertados = 0

    for i, row in df.iterrows():
        id_ppu = row[id_col]
        if not id_ppu:
            continue

        for col in date_cols:
            valor = row[col]
            if valor is None or str(valor).strip() == "":
                continue

            # --- NUEVO BLOQUE DE FECHAS ---
            try:
                # Forzar formato dd-mm-yyyy
                fecha = datetime.strptime(col.strip(), "%d-%m-%Y").strftime("%Y-%m-%d")
            except ValueError:
                print(f"⚠️ Encabezado '{col}' no se reconoció como fecha válida, se omite.")
                continue

            # Insertar registro
            cursor.execute(insert_query, (id_ppu, RUT_DEFECTO, fecha, valor))
            total_insertados += 1

    conn.commit()
    print(f"✅ Se cargaron {total_insertados} registros en la tabla '{table_name}' correctamente.")

except FileNotFoundError:
    print(f"❌ No se encontró el archivo '{excel_file}'. Verifica que esté en el mismo directorio del script.")
except mysql.connector.Error as db_error:
    print(f"❌ Error en la base de datos: {db_error}")
except Exception as e:
    print(f"❌ Error general durante la carga: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("🔒 Conexión cerrada.")
