import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

dados = pd.read_csv("dados_lagarta.csv", parse_dates=["date"])
features = ["temperature_7", "rh_7", "temperature_14", "rh_14"]
dados = dados.dropna(subset=features)
print(dados[features + ["por_dia"]].describe())

# teste 1: treina nos dias antigos, testa nos recentes
corte = dados["date"].quantile(0.8)
treino = dados[dados["date"] <= corte]
teste = dados[dados["date"] > corte]

rf_model = RandomForestRegressor(random_state=1)
rf_model.fit(treino[features], treino["por_dia"])
rf_preds = rf_model.predict(teste[features])
rf_val_mae = mean_absolute_error(teste["por_dia"], rf_preds)
mae_mediana = mean_absolute_error(teste["por_dia"], [treino["por_dia"].median()] * len(teste))

print("\nTeste por tempo")
print("erro da floresta: {:.3f}".format(rf_val_mae))
print("erro da mediana: {:.3f}".format(mae_mediana))

# teste 2: esconde um local inteiro de cada vez
print("\nTeste por local")
for sitio in dados["sitio"].unique():
    treino = dados[dados["sitio"] != sitio]
    teste = dados[dados["sitio"] == sitio]
    modelo = RandomForestRegressor(random_state=1)
    modelo.fit(treino[features], treino["por_dia"])
    erro = mean_absolute_error(teste["por_dia"], modelo.predict(teste[features]))
    erro_mediana = mean_absolute_error(teste["por_dia"], [treino["por_dia"].median()] * len(teste))
    print(sitio, "floresta: {:.3f}".format(erro), "mediana: {:.3f}".format(erro_mediana))