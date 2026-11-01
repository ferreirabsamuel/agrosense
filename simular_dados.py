import numpy as np
import pandas as pd

dados = pd.read_csv("dados_lagarta.csv", parse_dates=["date"])
dados = dados.dropna(subset=["temperature_7", "rh_7", "temperature_14", "rh_14"])
rng = np.random.default_rng(1)

# gatilho de temperatura (valores arredondados de estudos): 0 abaixo de 13 e acima de 34, maximo de 28 a 30
atividade = np.interp(dados["temperature_14"], [13, 28, 30, 34], [0, 1, 1, 0], left=0, right=0)
esperado = 4.0 * atividade   # 4 insetos por dia no maximo (escolha nossa)

ruido = rng.lognormal(0, 0.5, len(dados))
surto = np.where(rng.random(len(dados)) < 0.05, 5, 1)   # surtos que nao dependem do clima

dados["atividade_regra"] = esperado
dados["por_dia_sim"] = rng.poisson(esperado * ruido * surto)
dados["origem"] = "simulado"

dados.to_csv("dados_lagarta_SIMULADO.csv", index=False)
print(dados.groupby("sitio")["por_dia_sim"].agg(["mean", "max"]))
print("zeros:", round((dados["por_dia_sim"] == 0).mean(), 2))