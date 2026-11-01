import getpass

import pandas as pd
import pymysql

clima = pd.read_csv("hyd01_clima.csv", parse_dates=["data"])

def f_para_c(f):
    return ((f - 32) / 1.8).round(2)

dados = pd.DataFrame({
    "data": clima["data"].dt.date,
    "temp_media_c": f_para_c(clima["tavg"]),
    "temp_max_c": f_para_c(clima["tmax"]),
    "temp_min_c": f_para_c(clima["tmin"]),
    "umid_max_pct": (clima["rhmax"] * 100).clip(upper=100).round(2),
    "umid_min_pct": (clima["rhmin"] * 100).clip(upper=100).round(2),
    "chuva_mm": (clima["chuva"] * 25.4).clip(lower=0).round(2),
    "eto_mm": (clima["eto"] * 25.4).round(2),
})
dados = dados.astype(object).where(dados.notna(), None)

#usuario = input("usuario do mysql (enter para root): ") or "root"
#senha = getpass.getpass("senha do mysql: ")
conexao = pymysql.connect(host="localhost", user="root", password="root", database="agrosensea3")
cursor = conexao.cursor()

cursor.execute("select id_estacao from estacao where codigo = %s", ("HYD01",))
id_estacao = cursor.fetchone()[0]

linhas = [(id_estacao, *linha) for linha in dados.itertuples(index=False, name=None)]
cursor.executemany(
    """insert into clima_diario
       (id_estacao, data, temp_media_c, temp_max_c, temp_min_c, umid_max_pct, umid_min_pct, chuva_mm, eto_mm)
       values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
       on duplicate key update
       temp_media_c = values(temp_media_c), temp_max_c = values(temp_max_c), temp_min_c = values(temp_min_c),
       umid_max_pct = values(umid_max_pct), umid_min_pct = values(umid_min_pct),
       chuva_mm = values(chuva_mm), eto_mm = values(eto_mm)""",
    linhas,
)
conexao.commit()
print(len(linhas), "linhas enviadas")

cursor.execute("select count(*), min(data), max(data) from clima_diario")
print(cursor.fetchone())
conexao.close()