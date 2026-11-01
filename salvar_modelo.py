import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

dados = pd.read_csv("dados_lagarta_SIMULADO.csv")
features = ["temperature_7", "rh_7", "temperature_14", "rh_14"]

modelo = RandomForestRegressor(random_state=1, min_samples_leaf=20)
modelo.fit(dados[features], dados["por_dia_sim"])

pacote = {
    "modelo": modelo,
    "features": features,
    "praga": "Spodoptera frugiperda",
    "origem": "simulado",
    "linhas_treino": len(dados),
}
joblib.dump(pacote, "modelo_lagarta_SIMULADO.joblib")

# teste rapido: 7 e 14 dias com temperatura e umidade medias (valores de exemplo)
exemplo = pd.DataFrame([[22.0, 60.0, 21.0, 62.0]], columns=features)
print("atividade esperada (simulada):", round(modelo.predict(exemplo)[0], 2), "insetos por dia")