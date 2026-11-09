import os
import pandas as pd

RUTA_DATOS = os.path.join("datos", "ventas.csv")
RUTA_RESULTADO = os.path.join("resultados", "resumen_ventas.xlsx")

def cargar_datos(ruta):
    df = pd.read_csv(ruta)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["total_venta"] = df["cantidad"] * df["precio_unitario"]
    return df

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
    df = cargar_datos(RUTA_DATOS)
    resumen = calcular_resumen(df)

    print("Total de ventas:", resumen["total_ventas"])
    print("\nProductos más vendidos:")
    print(resumen["productos_mas_vendidos"])
    print("\nClientes con mayor compra:")
    print(resumen["clientes_top"])
    print("\nVentas por mes:")
    print(resumen["ventas_por_mes"])

    guardar_resultados(resumen)
    print("\nReporte generado en:", RUTA_RESULTADO)

if __name__ == "__main__":
    main()