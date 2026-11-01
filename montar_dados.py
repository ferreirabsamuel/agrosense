import pandas as pd

sitios = ['dembwa_taitaHills', 'maktau', 'mbitaPoints', 'nairobi']
partes = []

for sitio in sitios:
    c = pd.read_csv(f'bdd_kenya_{sitio}_sf.csv')
    c['date'] = pd.to_datetime(c['date'])
    print(sitio, 'datas repetidas:', c['date'].duplicated().sum())
    c = c.drop_duplicates('date', keep='last').sort_values('date')
    c['dias'] = c['date'].diff().dt.days
    c['por_dia'] = c['numberOfIndividuals'] / c['dias']

    k = pd.read_csv(f'bdd_kenya_{sitio}_climate.csv')
    k['dia'] = pd.to_datetime(k['dateUTC'], format='ISO8601').dt.normalize()
    diario = k.groupby('dia')[['temperature', 'rh']].mean().asfreq('D')
    anterior = diario.shift(1)
    for janela in (7, 14):
        medias = anterior.rolling(janela, min_periods=janela // 2).mean()
        c = c.merge(medias.add_suffix(f'_{janela}'), left_on='date', right_index=True, how='left')
    c['sitio'] = sitio
    partes.append(c)

dados = pd.concat(partes)
dados = dados.dropna(subset=['por_dia', 'temperature_7', 'rh_7'])
print(dados.groupby('sitio').agg(linhas=('por_dia', 'size'),
                                 media=('por_dia', 'mean'),
                                 zeros=('por_dia', lambda s: (s == 0).mean())))
dados.to_csv('dados_lagarta.csv', index=False)
print(list(dados.columns))