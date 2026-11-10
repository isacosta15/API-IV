from __future__ import annotations
import requests, pandas as pd, numpy as np
from backend.config import REQUEST_TIMEOUT

SIDRA="https://servicodados.ibge.gov.br/api/v3/agregados"
UF_CODES={"RO":11,"AC":12,"AM":13,"RR":14,"PA":15,"AP":16,"TO":17,"MA":21,"PI":22,"CE":23,"RN":24,"PB":25,"PE":26,"AL":27,"SE":28,"BA":29,"MG":31,"ES":32,"RJ":33,"SP":35,"PR":41,"SC":42,"RS":43,"MS":50,"MT":51,"GO":52,"DF":53}
CROPS={"soja":40124,"milho":40122,"arroz":400_leaf if False else 40001,"café":40108,"feijão":40110,"algodão":40102}
# SIDRA PAM 5457: variável 214 = quantidade produzida; classificação 782 = produto.
def fetch_production(uf:str, crop:str, start:int, end:int)->pd.DataFrame:
    uf=uf.upper()
    if uf not in UF_CODES: raise ValueError("UF inválida.")
    crop_key=crop.lower()
    if crop_key not in CROPS: raise ValueError("Cultura não cadastrada.")
    years=",".join(map(str,range(start,end+1)))
    url=f"{SIDRA}/5457/periodos/{years}/variaveis/214"
    params={"localidades":f"N3[{UF_CODES[uf]}]","classificacao":f"782[{CROPS[crop_key]}]","view":"flat"}
    r=requests.get(url,params=params,timeout=REQUEST_TIMEOUT); r.raise_for_status()
    rows=[]
    for block in r.json():
        for result in block.get("resultados",[]):
            for series in result.get("series",[]):
                for year,value in series.get("serie",{}).items():
                    try: rows.append({"ano":int(year),"producao_ton":float(str(value).replace(",",".")),"uf":uf,"cultura":crop_key})
                    except (ValueError,TypeError): continue
    df=pd.DataFrame(rows)
    if df.empty: raise ValueError("SIDRA não retornou dados. Confira o código da cultura no catálogo SIDRA.")
    return df.sort_values("ano")

def fetch_all_states(crop:str, year:int)->pd.DataFrame:
    rows=[]
    for uf,code in UF_CODES.items():
        url=f"{SIDRA}/5457/periodos/{year}/variaveis/214"
        params={"localidades":f"N3[{code}]","classificacao":f"782[{CROPS[crop.lower()]}]","view":"flat"}
        r=requests.get(url,params=params,timeout=REQUEST_TIMEOUT); r.raise_for_status()
        for block in r.json():
            for res in block.get("resultados",[]):
                for ser in res.get("series",[]):
                    for y,val in ser.get("serie",{}).items():
                        try: rows.append({"uf":uf,"ano":int(y),"producao_ton":float(str(val).replace(",",".")),"cultura":crop})
                        except (ValueError,TypeError): pass
    return pd.DataFrame(rows)

def fetch_cptec_seasonal(date:str, variable:str="prec", minlat:float=-34, maxlat:float=6,
                         minlon:float=285, maxlon:float=330):
    """Obtém grade sazonal CPTEC/INPE com biblioteca oficial sazonal."""
    try:
        import sazonal.CPTEC_SAZ as SAZ
    except ImportError as exc:
        raise RuntimeError("Instale a dependência sazonal conforme requirements.txt.") from exc
    model=SAZ.model()
    model.dict["area"]["reduce"]=True
    model.dict["area"]["minlat"]=minlat; model.dict["area"]["maxlat"]=maxlat
    model.dict["area"]["minlon"]=minlon; model.dict["area"]["maxlon"]=maxlon
    dataset=model.load(date=date,var=[variable],product="seas",field="anomalies")
    return dataset

def seasonal_grid_summary(dataset)->dict:
    """Retorna estatísticas da grade; identifica variável espacial no NetCDF retornado."""
    import xarray as xr
    if not hasattr(dataset,"data_vars"): raise ValueError("Resposta CPTEC não é um Dataset xarray.")
    variable=next(iter(dataset.data_vars))
    da=dataset[variable]
    values=np.asarray(da.values,dtype=float)
    valid=values[np.isfinite(values)]
    if not valid.size: raise ValueError("Grade climática sem valores válidos.")
    return {"variavel":variable,"media_anomalia":float(valid.mean()),"minimo":float(valid.min()),
            "maximo":float(valid.max()),"shape":list(values.shape)}

def merge_production_climate(production:pd.DataFrame, climate:pd.DataFrame)->pd.DataFrame:
    if not {"ano","precipitacao_mm"}.issubset(climate.columns):
        raise ValueError("CSV climático precisa conter ano e precipitacao_mm.")
    merged=production.merge(climate[["ano","precipitacao_mm"]],on="ano",how="inner")
    if merged.empty: raise ValueError("Não existem anos coincidentes. Dados de previsão sazonal não substituem precipitação histórica observada.")
    return merged

def correlation_summary(df:pd.DataFrame)->dict:
    if len(df)<3: raise ValueError("São necessários ao menos três anos coincidentes.")
    corr=df["producao_ton"].corr(df["precipitacao_mm"])
    return {"correlacao_pearson":float(corr),"observacoes":int(len(df))}

def health_payload(): return {"status":"ok","service":"agro-clima"}
