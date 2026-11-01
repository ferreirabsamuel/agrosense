import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

praga_data = pd.read_csv("gorgulho_simulado.csv")
print(praga_data.describe())

features = ["dd_acum", "temp_7", "rh_7", "chuva_7", "eto_7", "dia_ano"]
X = praga_data[features]
y = praga_data["quantidade"]

# treina nos anos antigos e testa nos recentes (no lugar do train_test_split aleatorio)
treino = praga_data["ano"] <= 2022
train_X, val_X = X[treino], X[~treino]
train_y, val_y = y[treino], y[~treino]

rf_model = RandomForestRegressor(random_state=1, min_samples_leaf=5)
rf_model.fit(train_X, train_y)

rf_preds = rf_model.predict(val_X)
rf_val_mae = mean_absolute_error(val_y, rf_preds)

# palpites simples para comparar
mae_mediana = mean_absolute_error(val_y, [train_y.median()] * len(val_y))
media_semana = train_y.groupby(train_X["dia_ano"] // 7).mean()
palpite_semana = (val_X["dia_ano"] // 7).map(media_semana).fillna(train_y.mean())
mae_semana = mean_absolute_error(val_y, palpite_semana)

print("\nO erro médio absoluto da floresta é de {:.3f}".format(rf_val_mae))
print("O erro médio absoluto da mediana é de {:.3f}".format(mae_mediana))
print("O erro médio absoluto da média da semana é de {:.3f}".format(mae_semana))
print("Passa no teste:", rf_val_mae < mae_mediana and rf_val_mae < mae_semana)

final_model = RandomForestRegressor(random_state=1, min_samples_leaf=5)
final_model.fit(X, y)

graus_dia = float(input("\nInsira os graus-dia acumulados no ano (base 48 F): "))
temperatura = float(input("Insira a temperatura média dos últimos 7 dias (F): "))
umidade = float(input("Insira a umidade relativa média dos últimos 7 dias (de 0 a 1): "))
chuva = float(input("Insira a chuva dos últimos 7 dias (polegadas): "))
eto = float(input("Insira a ETo dos últimos 7 dias (polegadas): "))
dia = float(input("Insira o dia do ano (1 a 365): "))

new_data = pd.DataFrame([[graus_dia, temperatura, umidade, chuva, eto, dia]], columns=features)
larvas_previstas = final_model.predict(new_data)[0]

print("\nLarvas previstas por amostra (SIMULADO): {:.1f}".format(larvas_previstas))