import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

praga_data = pd.read_csv("gorgulho_simulado.csv")
praga_data["tem_larva"] = praga_data["quantidade"] > 0
print("visitas com larva:", round(praga_data["tem_larva"].mean(), 2))

features = ["dd_acum", "temp_7", "rh_7", "chuva_7", "eto_7", "dia_ano"]
X = praga_data[features]
y = praga_data["tem_larva"]

# treina nos anos antigos e testa nos recentes
treino = praga_data["ano"] <= 2022
train_X, val_X = X[treino], X[~treino]
train_y, val_y = y[treino], y[~treino]

rf_model = RandomForestClassifier(random_state=1, min_samples_leaf=5)
rf_model.fit(train_X, train_y)
rf_auc = roc_auc_score(val_y, rf_model.predict_proba(val_X)[:, 1])

# palpite simples: taxa de visitas com larva na mesma semana do ano
taxa_semana = train_y.groupby(train_X["dia_ano"] // 7).mean()
palpite_semana = (val_X["dia_ano"] // 7).map(taxa_semana).fillna(train_y.mean())
auc_semana = roc_auc_score(val_y, palpite_semana)

print("\nNota (AUC) da floresta: {:.3f}".format(rf_auc))
print("Nota (AUC) da média da semana: {:.3f}".format(auc_semana))
print("Passa no teste:", rf_auc > auc_semana)

final_model = RandomForestClassifier(random_state=1, min_samples_leaf=5)
final_model.fit(X, y)

graus_dia = float(input("\nInsira os graus-dia acumulados no ano (base 48 F): "))
temperatura = float(input("Insira a temperatura média dos últimos 7 dias (F): "))
umidade = float(input("Insira a umidade relativa média dos últimos 7 dias (de 0 a 1): "))
chuva = float(input("Insira a chuva dos últimos 7 dias (polegadas): "))
eto = float(input("Insira a ETo dos últimos 7 dias (polegadas): "))
dia = float(input("Insira o dia do ano (1 a 365): "))

new_data = pd.DataFrame([[graus_dia, temperatura, umidade, chuva, eto, dia]], columns=features)
chance = final_model.predict_proba(new_data)[0, 1]
faixa = "alto" if chance >= 0.5 else "médio" if chance >= 0.2 else "baixo"

print("\nChance de ter larva (SIMULADO): {:.0%} | risco: {}".format(chance, faixa))