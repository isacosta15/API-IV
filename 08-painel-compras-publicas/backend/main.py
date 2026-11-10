from fastapi import FastAPI,HTTPException,Query
from backend.services import fetch_contracts,fetch_suppliers,health_payload
app=FastAPI(title="Painel de Compras Públicas Federais",version="2.0.0")
@app.get("/health")
def health(): return health_payload()
@app.get("/api/v1/contratos")
def contracts(codigo_orgao:str,date_min:str,date_max:str,pagina:int=1,tamanho_pagina:int=500,
              ni_fornecedor:str|None=None,auto_paginas:int=1):
    try:
        df,meta=fetch_contracts(codigo_orgao,date_min,date_max,pagina,tamanho_pagina,ni_fornecedor,auto_paginas)
        return {"metadados":meta,"quantidade":len(df),"dados":df.to_dict("records")}
    except Exception as e: raise HTTPException(502,str(e))
@app.get("/api/v1/fornecedores")
def suppliers(pagina:int=1,tamanho_pagina:int=500,cnpj:str|None=None,codigo_cnae:int|None=None):
    try:
        df,meta=fetch_suppliers(pagina,tamanho_pagina,cnpj,codigo_cnae)
        return {"quantidade":len(df),"dados":df.to_dict("records")}
    except Exception as e: raise HTTPException(502,str(e))
