import numpy as np
import pandas as pd

clima = pd.read_csv("hyd01_clima.csv", parse_dates=["data"]).sort_values("data").set_index("data")
clima[["tmax", "tmin"]] = clima[["tmax", "tmin"]].interpolate(limit=5)
minima = clima["tmin"].clip(lower=48)
clima["dd"] = np.where(clima["tmax"] > 48, (clima["tmax"] + minima) / 2 - 48, 0.0)
clima["dd_acum"] = clima.groupby(clima.index.year)["dd"].cumsum()
clima["rh"] = (clima["rhmax"] + clima["rhmin"]) / 2

# checagem do 2026: dias de marco com maxima acima de 48 F, por ano
marco = clima[clima.index.month == 3]
print(marco.groupby(marco.index.year)["tmax"].apply(lambda s: int((s > 48).sum())).to_string())

# caracteristicas: so usam dias ANTERIORES a visita
anterior = clima.shift(1)
car = pd.DataFrame(index=clima.index)
car["dd_acum"] = anterior["dd_acum"]
car["temp_7"] = anterior["tavg"].rolling(7, min_periods=4).mean()
car["rh_7"] = anterior["rh"].rolling(7, min_periods=4).mean()
car["chuva_7"] = anterior["chuva"].rolling(7, min_periods=4).sum()
car["eto_7"] = anterior["eto"].rolling(7, min_periods=4).sum()
car["dia_ano"] = clima.index.dayofyear

obs = pd.read_csv("observacao_praga_SIMULADO.csv", parse_dates=["observado_em"]).drop(columns=["dd_acum"])
dados = obs.merge(car, left_on="observado_em", right_index=True, how="left").dropna()
dados["ano"] = dados["observado_em"].dt.year

colunas = ["observado_em", "ano", "dd_acum", "temp_7", "rh_7", "chuva_7", "eto_7", "dia_ano",
           "quantidade", "atividade_regra"]
dados[colunas].to_csv("gorgulho_simulado.csv", index=False)
print(len(dados), "linhas salvas em gorgulho_simulado.csv")