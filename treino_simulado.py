import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error

dados = pd.read_csv("dados_lagarta_SIMULADO.csv", parse_dates=["date"])
features = ["temperature_7", "rh_7", "temperature_14", "rh_14"]

corte = dados["date"].quantile(0.8)
treino = dados[dados["date"] <= corte]
teste = dados[dados["date"] > corte]

modelo = RandomForestRegressor(random_state=1, min_samples_leaf=20)
modelo.fit(treino[features], treino["por_dia_sim"])
previsto = modelo.predict(teste[features])

print("erro da floresta: {:.3f}".format(mean_absolute_error(teste["por_dia_sim"], previsto)))
print("erro da mediana: {:.3f}".format(mean_absolute_error(teste["por_dia_sim"], [treino["por_dia_sim"].median()] * len(teste))))
print("correlacao com a regra: {:.2f}".format(pd.Series(previsto, index=teste.index).corr(teste["atividade_regra"], method="spearman")))

res = permutation_importance(modelo, teste[features], teste["por_dia_sim"], n_repeats=10, random_state=1)
print(dict(zip(features, res.importances_mean.round(3))))