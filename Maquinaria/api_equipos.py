from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# --- CONFIGURACIÓN DE CONEXIÓN ---
config = {
    'host': '135.148.188.205',
    'port': 3306,
    'user': 'cso60906_dba',
    'password': 'Miscka-2025',
    'database': 'cso60906_Equipos'
}

@app.route('/api/equipos/<string:ppu>', methods=['GET'])
def buscar_equipo(ppu):
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        # Buscar el equipo por idTxt_Ppu
        query = "SELECT * FROM tdEquipos WHERE idTxt_Ppu = %s"
        cursor.execute(query, (ppu,))
        equipo = cursor.fetchone()

        if equipo:
            return jsonify({
                "existe": True,
                "datos": equipo
            })
        else:
            return jsonify({
                "existe": False,
                "mensaje": "Código no encontrado"
            })

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
