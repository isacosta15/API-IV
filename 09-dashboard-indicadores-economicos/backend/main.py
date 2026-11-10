from fastapi import FastAPI,HTTPException,Query
from backend.services import fetch_bcb,fetch_ipea,fetch_ipea_metadata,health_payload
app=FastAPI(title="Dashboard de Indicadores Econômicos",version="2.0.0")
@app.get("/health")
def health(): return health_payload()
@app.get("/api/v1/bcb/{codigo}")
def bcb(codigo:int,data_inicio:str="01/01/2015",data_fim:str="31/12/2025"):
 try:
  df=fetch_bcb(codigo,data_inicio,data_fim); df["data"]=df.data.dt.strftime("%Y-%m-%d")
  return {"fonte":"BCB/SGS","codigo":codigo,"dados":df.to_dict("records")}
 except Exception as e: raise HTTPException(502,str(e))
@app.get("/api/v1/ipeadata/{codigo}")
def ipea(codigo:str):
 try:
  df=fetch_ipea(codigo); df["data"]=df.data.dt.strftime("%Y-%m-%d")
  return {"fonte":"IPEADATA","codigo":codigo,"dados":df.to_dict("records")}
 except Exception as e: raise HTTPException(502,str(e))
@app.get("/api/v1/ipeadata/catalogo")
def ipea_catalogo(busca:str|None=None,limite:int=100):
 try: return {"dados":fetch_ipea_metadata(busca,limite).to_dict("records")}
 except Exception as e: raise HTTPException(502,str(e))
