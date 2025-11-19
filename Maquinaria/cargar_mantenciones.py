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

# --- ARCHIVO Y TABLA ---
excel_file = '09-11.xlsx'
table_name = 'tdHorometro'

try:
    # Leer el Excel
    df = pd.read_excel(excel_file)
    print(f"✅ Archivo '{excel_file}' leído correctamente. Registros encontrados: {len(df)}")

    # Asegurar que todos los nombres de columnas sean strings
    df.columns = df.columns.map(str)

    # Limpiar columnas sin nombre
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False, na=False)]
    print(f"🧹 Columnas detectadas: {list(df.columns)}")

    # Obtener encabezados de fechas (todas menos la primera columna)
    date_cols = df.columns[1:]
    print(f"📅 Encabezados de fechas detectados: {list(date_cols)}")

    # Convertir encabezados a formato 'YYYY-MM-DD'
    date_cols_formatted = [pd.to_datetime(c, errors='coerce').strftime('%Y-%m-%d') for c in date_cols]
    print(f"📆 Fechas formateadas: {date_cols_formatted}")

    # Conectar a la base de datos
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("✅ Conexión establecida con la base de datos.")

    # Vaciar la tabla antes de cargar nuevos datos
    cursor.execute(f"DELETE FROM `{table_name}`")
    conn.commit()
    print(f"⚠️ Todos los registros de '{table_name}' fueron eliminados antes de la carga.")

    # Preparar la consulta de inserción
    insert_query = f"""
        INSERT INTO `{table_name}` (`idTxt_Ppu`, `dtFec_Registro`, `dtNum_Horometro`, `idNum_Rut`)
        VALUES (%s, %s, %s, %s)
    """

    registros_insertados = 0

    # Recorrer filas del DataFrame
    for _, row in df.iterrows():
        idTxt_Ppu = str(row[df.columns[0]]).strip()
        if not idTxt_Ppu or idTxt_Ppu.lower() == 'nan':
            continue

        for i, date_col in enumerate(date_cols):
            fecha_str = date_cols_formatted[i]
            if pd.isna(fecha_str):
                continue  # Si el encabezado no es fecha válida

            valor = row[date_col]
            if pd.isna(valor):
                continue

            try:
                horas = float(valor)
            except:
                continue

            cursor.execute(insert_query, (idTxt_Ppu, fecha_str, horas, 1))
            registros_insertados += 1

            if registros_insertados <= 5:
                print(f"🟢 Insertado: {idTxt_Ppu} | {fecha_str} | {horas}")

    conn.commit()
    print(f"✅ Se insertaron {registros_insertados} registros en '{table_name}' correctamente.")

except Exception as e:
    print(f"❌ Error general durante la carga: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("🔒 Conexión cerrada.")
