import pandas as pd

url = "https://coagmet.colostate.edu/data/daily/hyd01.csv?header=yes&from=2012-01-01&to=2026-10-30&dateFmt=iso&fields=name,lat,lon,tAvg,tMax,tMaxTime,tMin,tMinTime,rhMax,rhMaxTime,rhMin,rhMinTime,vp,precip,pp_wbased,windRun,gustSpeed,gustTime,gustDir,solarRad,rso,etrASCE,etrPK,etrHourly,etoASCE,st5Max,st5MaxTime,st5Min,st5MinTime,st15Max,st15MaxTime,st15Min,st15MinTime,windSpeed10m,gustSpeed10m,gustTime10m,gustDir10m"

dados = pd.read_csv(url, skiprows=[1], na_values=[-999])

colunas = {"Station": "estacao", "Date": "data", "Avg Temp": "tavg", "Max Temp": "tmax",
           "Min Temp": "tmin", "RH Max": "rhmax", "RH Min": "rhmin", "Vapor Pressure": "vp",
           "Liquid Precip": "chuva", "Wind Run": "vento", "Solar Rad": "radiacao", "ASCE ETo": "eto"}
dados = dados[list(colunas)].rename(columns=colunas)
dados["data"] = pd.to_datetime(dados["data"])

print("linhas:", len(dados))
print("de", dados["data"].min().date(), "ate", dados["data"].max().date())
print("dias esperados:", (dados["data"].max() - dados["data"].min()).days + 1)
print("parte vazia por coluna:")
print(dados.isna().mean().round(3))
dados.to_csv("hyd01_clima.csv", index=False)