import numpy as np
import pandas as pd

clima = pd.read_csv("hyd01_clima.csv", parse_dates=["data"]).sort_values("data")
clima[["tmax", "tmin"]] = clima[["tmax", "tmin"]].interpolate(limit=5)

# graus-dia, base 48 F: se a maxima passa de 48, soma (max + max(min, 48)) / 2 - 48
minima = clima["tmin"].clip(lower=48)
clima["dd"] = np.where(clima["tmax"] > 48, (clima["tmax"] + minima) / 2 - 48, 0.0)
clima["ano"] = clima["data"].dt.year
clima["dd_acum"] = clima.groupby("ano")["dd"].cumsum()

# atividade larval: 0 antes de 300, 1 de 450 a 600, 0 de novo em 900 (subida e descida sao suposicao nossa)
clima["atividade"] = np.interp(clima["dd_acum"], [300, 450, 600, 900], [0, 1, 1, 0], left=0, right=0)

rng = np.random.default_rng(1)
anos = sorted(clima["ano"].unique())
fator_ano = {ano: rng.lognormal(0, 0.6) for ano in anos}

# uma visita por semana, de abril a setembro, em cada ano
visitas = pd.concat([pd.DataFrame({"data": pd.date_range(f"{a}-04-01", f"{a}-09-30", freq="7D")}) for a in anos])
visitas = visitas.merge(clima[["data", "ano", "dd_acum", "atividade"]], on="data", how="inner")

media = 20 * visitas["atividade"] * visitas["ano"].map(fator_ano) * rng.lognormal(0, 0.4, len(visitas))
achou = rng.random(len(visitas)) > 0.15
visitas["quantidade"] = np.where(achou, rng.poisson(media), 0)

saida = pd.DataFrame({
    "estacao": "HYD01",
    "observado_em": visitas["data"],
    "praga": "Hypera postica",
    "quantidade": visitas["quantidade"],
    "metodo": "varredura (simulada)",
    "origem": "simulado",
    "dd_acum": visitas["dd_acum"].round(0),
    "atividade_regra": visitas["atividade"].round(2),
})
saida.to_csv("observacao_praga_SIMULADO.csv", index=False)

print("visitas:", len(saida), "| zeros:", round((saida["quantidade"] == 0).mean(), 2))
print(saida.groupby(saida["observado_em"].dt.year)["quantidade"].agg(["sum", "max"]))
print("dia em que passa de 300 graus-dia:")
print(clima[clima["dd_acum"] >= 300].groupby("ano")["data"].min().dt.strftime("%m-%d"))