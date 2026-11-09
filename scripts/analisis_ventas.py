import os
import sqlite3

import pandas as pd

RUTA_DATOS = os.path.join("datos", "ventas.csv")
RUTA_BASE_DATOS = os.path.join("base_datos", "ventas.db")
RUTA_RESULTADO = os.path.join("resultados", "resumen_ventas.xlsx")

COLUMNAS_REQUERIDAS = [
    "fecha",
    "producto",
    "cantidad",
    "precio_unitario",
    "cliente",
]


def validar_archivo(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    df = pd.read_csv(ruta)

    columnas_faltantes = [
        columna for columna in COLUMNAS_REQUERIDAS
        if columna not in df.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            f"Faltan columnas obligatorias: {', '.join(columnas_faltantes)}"
        )

    return df


def limpiar_datos(df):
    df = df.copy()

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
    df["precio_unitario"] = pd.to_numeric(
        df["precio_unitario"], errors="coerce"
    )

    df = df.dropna(
        subset=[
            "fecha",
            "producto",
            "cantidad",
            "precio_unitario",
            "cliente",
        ]
    )

    df = df.drop_duplicates()

    df = df[df["cantidad"] > 0]
    df = df[df["precio_unitario"] > 0]

    df["total_venta"] = df["cantidad"] * df["precio_unitario"]

    return df


def crear_base_datos(df):
    os.makedirs("base_datos", exist_ok=True)

    conexion = sqlite3.connect(RUTA_BASE_DATOS)

    df.to_sql(
        name="ventas",
        con=conexion,
        if_exists="replace",
        index=False,
    )

    conexion.commit()
    conexion.close()


def calcular_resumen(df):
    total_ventas = df["total_venta"].sum()

    productos_mas_vendidos = (
        df.groupby("producto")["cantidad"]
        .sum()
        .sort_values(ascending=False)
    )

    clientes_top = (
        df.groupby("cliente")["total_venta"]
        .sum()
        .sort_values(ascending=False)
    )

    ventas_por_mes = (
        df.assign(mes=df["fecha"].dt.to_period("M"))
        .groupby("mes")["total_venta"]
        .sum()
    )

    return {
        "total_ventas": total_ventas,
        "productos_mas_vendidos": productos_mas_vendidos,
        "clientes_top": clientes_top,
        "ventas_por_mes": ventas_por_mes,
    }


def guardar_resultados(resumen):
    os.makedirs("resultados", exist_ok=True)

    with pd.ExcelWriter(RUTA_RESULTADO) as writer:
        pd.DataFrame(
            [{"metrica": "Total de ventas", "valor": resumen["total_ventas"]}]
        ).to_excel(writer, sheet_name="Resumen", index=False)

        resumen["productos_mas_vendidos"].to_excel(
            writer, sheet_name="Productos", index=True
        )

        resumen["clientes_top"].to_excel(
            writer, sheet_name="Clientes", index=True
        )

        resumen["ventas_por_mes"].to_excel(
            writer, sheet_name="Ventas por mes", index=True
        )


def main():
    try:
        df = validar_archivo(RUTA_DATOS)
        df = limpiar_datos(df)

        if df.empty:
            raise ValueError("No hay datos válidos para analizar.")

        crear_base_datos(df)

        resumen = calcular_resumen(df)
        guardar_resultados(resumen)

        print("Datos cargados y validados correctamente.")
        print("Base de datos creada en:", RUTA_BASE_DATOS)
        print("Total de ventas:", resumen["total_ventas"])

    except FileNotFoundError as error:
        print("Error:", error)

    except ValueError as error:
        print("Error de datos:", error)

    except Exception as error:
        print("Error inesperado:", error)


if __name__ == "__main__":
    main()