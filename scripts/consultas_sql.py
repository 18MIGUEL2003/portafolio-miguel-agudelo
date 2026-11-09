import sqlite3

RUTA_BASE_DATOS = "base_datos/ventas.db"

def ejecutar_consulta(consulta):
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()
    cursor.execute(consulta)
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


consultas = {
    "Total de ventas": """
        SELECT SUM(cantidad * precio_unitario) AS total_ventas
        FROM ventas;
    """,

    "Ventas por producto": """
        SELECT producto,
               SUM(cantidad) AS unidades_vendidas,
               SUM(cantidad * precio_unitario) AS total_ventas
        FROM ventas
        GROUP BY producto
        ORDER BY total_ventas DESC;
    """,

    "Ventas por cliente": """
        SELECT cliente,
               SUM(cantidad * precio_unitario) AS total_ventas
        FROM ventas
        GROUP BY cliente
        ORDER BY total_ventas DESC;
    """,

    "Ventas por mes": """
        SELECT strftime('%Y-%m', fecha) AS mes,
               SUM(cantidad * precio_unitario) AS total_ventas
        FROM ventas
        GROUP BY mes
        ORDER BY mes;
    """,

    "Productos con precio mayor a 500000": """
        SELECT producto,
               precio_unitario,
               cantidad
        FROM ventas
        WHERE precio_unitario > 500000;
    """,
}


for nombre, consulta in consultas.items():
    print("\n" + nombre)
    print("-" * len(nombre))

    for fila in ejecutar_consulta(consulta):
        print(fila)