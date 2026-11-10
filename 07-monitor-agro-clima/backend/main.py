from fastapi import FastAPI,HTTPException,Query,UploadFile,File
import pandas as pd, io
from backend.services import fetch_production,fetch_all_states,fetch_cptec_seasonal,seasonal_grid_summary,merge_production_climate,correlation_summary,health_payload
app=FastAPI(title="Monitor Agropecuário e Climático",version="2.0.0")
@app.get("/health")
def health(): return health_payload()
@app.get("/api/v1/agro/producao")
def production(uf:str="SP",cultura:str="soja",ano_inicio:int=2015,ano_fim:int=2025):
    try:
        if ano_inicio>ano_fim or ano_fim-ano_inicio>30: raise ValueError("Intervalo inválido (máximo 30 anos).")
        df=fetch_production(uf,cultura,ano_inicio,ano_fim)
        return {"fonte":"IBGE/SIDRA PAM 5457","dados":df.to_dict("records")}
    except Exception as e: raise HTTPException(502,str(e))
@app.get("/api/v1/agro/estados")
def states(cultura:str="soja",ano:int=2025):
    try: return {"fonte":"IBGE/SIDRA PAM 5457","dados":fetch_all_states(cultura,ano).to_dict("records")}
    except Exception as e: raise HTTPException(502,str(e))
@app.get("/api/v1/clima/previsao")
def climate(date:str=Query(...,pattern=r"^\d{6}$"),variavel:str="prec"):
    try:
        ds=fetch_cptec_seasonal(date,variavel)
        summary=seasonal_grid_summary(ds)
        return {"fonte":"CPTEC/INPE BAM-1.2","data_emissao":date,"resumo":summary,
                "nota":"Campo retornado é anomalia sazonal; consulte metadados/unidade do produto antes de interpretar."}
    except Exception as e: raise HTTPException(502,str(e))
@app.post("/api/v1/analise/cruzar")
async def cross_data(uf:str="SP",cultura:str="soja",ano_inicio:int=2015,ano_fim:int=2025,
                     arquivo_climatico:UploadFile=File(...)):
    try:
        climate=pd.read_csv(io.BytesIO(await arquivo_climatico.read()))
        prod=fetch_production(uf,cultura,ano_inicio,ano_fim)
        merged=merge_production_climate(prod,climate)
        return {"dados":merged.to_dict("records"),"estatisticas":correlation_summary(merged)}
    except Exception as e: raise HTTPException(400,str(e))
