import pandas as pd
import mysql.connector

# --- CONFIGURACIÓN DE CONEXIÓN ---
config = {
    'host': '135.148.188.205',
    'port': 3306,
    'user': 'cso60906_dba',
    'password': 'Miscka-2025',
    'database': 'cso60906_Equipos'
}

excel_file = 'operadores.xlsx'
table_name = 'tdOperadores'

try:
    # Leer el Excel
    df = pd.read_excel(excel_file)
    print(f"✅ Archivo '{excel_file}' leído correctamente. Registros encontrados: {len(df)}")

    # Eliminar columnas sin nombre
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # Reemplazar NaN por None para que se inserten como NULL
    df = df.where(pd.notnull(df), None)

    print(f"🧹 Columnas limpias: {list(df.columns)}")

    # Conectar a la base de datos
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("✅ Conexión establecida con la base de datos.")

    # Vaciar la tabla
    cursor.execute(f"DELETE FROM {table_name}")
    conn.commit()
    print(f"⚠️ Todos los registros de '{table_name}' fueron eliminados.")

    # Preparar consulta parametrizada
    cols = ', '.join([f"`{col}`" for col in df.columns])
    placeholders = ', '.join(['%s'] * len(df.columns))
    insert_query = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"

    # Insertar los registros
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))
    conn.commit()

    print(f"✅ Se cargaron {len(df)} registros en la tabla '{table_name}' correctamente.")

except Exception as e:
    print("❌ Error durante la carga:", e)

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("🔒 Conexión cerrada.")
