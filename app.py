from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)
DB_NAME = 'marisqueria.db'

def init_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)  # Borra base vieja para pruebas limpias

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT,
            tipo_producto TEXT,
            cantidad REAL,
            precio REAL,
            comentario TEXT,
            whatsapp TEXT,
            calificacion INTEGER,
            fecha TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT,
            cantidad REAL,
            unidad TEXT,
            costo_unitario REAL,
            proveedor TEXT,
            fecha TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT UNIQUE,
            cantidad REAL,
            unidad TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Descomenta esta línea si querés reiniciar la base cada vez
# init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/venta', methods=['POST'])
def registrar_venta():
    data = request.get_json()
    data['fecha'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ventas (producto, tipo_producto, cantidad, precio, comentario, whatsapp, calificacion, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['producto'], data['tipo_producto'], data['cantidad'], data['precio'],
        data.get('comentario', ''), data.get('whatsapp', ''), data.get('calificacion', None), data['fecha']
    ))
    conn.commit()
    conn.close()

    return jsonify({'mensaje': 'Venta registrada exitosamente'})

@app.route('/compra', methods=['POST'])
def registrar_compra():
    data = request.get_json()
    data['fecha'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO compras (producto, cantidad, unidad, costo_unitario, proveedor, fecha)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['producto'], data['cantidad'], data['unidad'],
        data['costo_unitario'], data.get('proveedor', ''), data['fecha']
    ))

    # Actualiza inventario
    cursor.execute('''
        SELECT cantidad FROM inventario WHERE producto = ?
    ''', (data['producto'],))
    fila = cursor.fetchone()

    if fila:
        nueva_cantidad = fila[0] + data['cantidad']
        cursor.execute('UPDATE inventario SET cantidad = ? WHERE producto = ?', (nueva_cantidad, data['producto']))
    else:
        cursor.execute('''
            INSERT INTO inventario (producto, cantidad, unidad)
            VALUES (?, ?, ?)
        ''', (data['producto'], data['cantidad'], data['unidad']))

    conn.commit()
    conn.close()

    return jsonify({'mensaje': 'Compra registrada e inventario actualizado'})

@app.route('/ventas', methods=['GET'])
def consultar_ventas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT producto, tipo_producto, cantidad, precio, comentario, fecha FROM ventas ORDER BY fecha DESC')
    columnas = [col[0] for col in cursor.description]
    ventas = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    conn.close()
    return jsonify(ventas)

@app.route('/compras', methods=['GET'])
def consultar_compras():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT producto, cantidad, unidad, costo_unitario, proveedor, fecha FROM compras ORDER BY fecha DESC')
    columnas = [col[0] for col in cursor.description]
    compras = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    conn.close()
    return jsonify(compras)

@app.route('/inventario', methods=['GET'])
def consultar_inventario():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT producto, cantidad, unidad FROM inventario ORDER BY producto')
    columnas = [col[0] for col in cursor.description]
    inventario = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    conn.close()
    return jsonify(inventario)

@app.route('/reporte')
def reporte():
    conn = sqlite3.connect(DB_NAME)
    ventas_df = pd.read_sql_query('SELECT * FROM ventas', conn)
    compras_df = pd.read_sql_query('SELECT * FROM compras', conn)
    conn.close()

    ventas_total = ventas_df['precio'].astype(float).multiply(ventas_df['cantidad']).sum() if not ventas_df.empty else 0
    compras_total = compras_df['costo_unitario'].astype(float).multiply(compras_df['cantidad']).sum() if not compras_df.empty else 0
    ganancia = ventas_total - compras_total

    html = f"""
    <style>
      table {{
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 20px;
      }}
      table, th, td {{
        border: 1px solid #ddd;
      }}
      th, td {{
        padding: 8px;
        text-align: left;
      }}
      tr:nth-child(even) {{
        background-color: #f2f2f2;
      }}
      th {{
        background-color: #3498db;
        color: white;
      }}
    </style>

    <h1>Reporte Financiero</h1>
    <p>Total en Ventas: ${ventas_total:.2f}</p>
    <p>Total en Compras: ${compras_total:.2f}</p>
    <p><strong>Ganancia Neta: ${ganancia:.2f}</strong></p>

    <h2>Detalle de Ventas</h2>
    {ventas_df.to_html(index=False)}

    <h2>Detalle de Compras</h2>
    {compras_df.to_html(index=False)}
    """

    return html

if __name__ == '__main__':
    app.run(debug=True)


