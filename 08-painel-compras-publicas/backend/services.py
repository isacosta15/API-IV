import requests, pandas as pd, time
from backend.config import REQUEST_TIMEOUT
BASE="https://dadosabertos.compras.gov.br"
def get_page(path:str,params:dict):
    r=requests.get(BASE+path,params=params,headers={"Accept":"application/json"},timeout=REQUEST_TIMEOUT)
    if r.status_code==429: raise RuntimeError("Limite de 100 chamadas/60s atingido; aguarde e tente novamente.")
    r.raise_for_status(); return r.json()
def result_rows(payload):
    if isinstance(payload,dict): return payload.get("resultado",[])
    return payload if isinstance(payload,list) else []
def fetch_contracts(codigo_orgao:str,date_min:str,date_max:str,page:int=1,page_size:int=500,
                   ni_fornecedor:str|None=None,auto_pages:int=1):
    if not codigo_orgao: raise ValueError("codigoOrgao é obrigatório na API de contratos.")
    if date_min>date_max: raise ValueError("Data inicial maior que final.")
    all_rows=[]; metadata={}
    for p in range(page,page+max(1,min(auto_pages,20))):
        params={"codigoOrgao":codigo_orgao,"dataVigenciaInicialMin":date_min,
                "dataVigenciaInicialMax":date_max,"pagina":p,"tamanhoPagina":min(page_size,500)}
        if ni_fornecedor: params["niFornecedor"]=ni_fornecedor
        payload=get_page("/modulo-contratos/1_consultarContratos",params)
        rows=result_rows(payload); all_rows.extend(rows)
        if isinstance(payload,dict):
            metadata={k:payload.get(k) for k in ("totalRegistros","totalPaginas","paginasRestantes")}
            if p>=int(payload.get("totalPaginas",p)): break
        if not rows: break
        if p < page+auto_pages-1: time.sleep(.7)
    return pd.json_normalize(all_rows),metadata
def fetch_suppliers(page:int=1,page_size:int=500,cnpj:str|None=None,cnae:int|None=None):
    params={"pagina":page,"tamanhoPagina":min(page_size,500)}
    if cnpj: params["cnpj"]=cnpj
    if cnae: params["codigoCnae"]=cnae
    payload=get_page("/modulo-fornecedor/1_consultarFornecedor",params)
    return pd.json_normalize(result_rows(payload)),payload if isinstance(payload,dict) else {}
def rank_suppliers(contracts:pd.DataFrame,top_n:int=10,sector_cnae:int|None=None,suppliers:pd.DataFrame|None=None):
    df=contracts.copy()
    value_col="valorGlobal"
    supplier_col="nomeRazaoSocialFornecedor"
    if value_col not in df or supplier_col not in df: raise ValueError("Resposta de contratos sem valorGlobal ou fornecedor.")
    df[value_col]=pd.to_numeric(df[value_col],errors="coerce")
    if sector_cnae is not None:
        if suppliers is None or "codigoCnae" not in suppliers or "niFornecedor" not in suppliers:
            raise ValueError("Para filtrar por ramo, forneça cadastro de fornecedores com CNAE e identificação.")
        eligible=suppliers.loc[pd.to_numeric(suppliers.codigoCnae,errors="coerce")==sector_cnae,"niFornecedor"].astype(str)
        df=df[df["niFornecedor"].astype(str).isin(set(eligible))]
    return (df.dropna(subset=[value_col]).groupby(supplier_col,as_index=False)[value_col]
            .sum().sort_values(value_col,ascending=False).head(top_n))
def aggregate_contracts_by_state(contracts:pd.DataFrame,suppliers:pd.DataFrame|None=None):
    if suppliers is None or not {"niFornecedor","uf"}.issubset(suppliers.columns):
        raise ValueError("É necessário cruzar contratos com cadastro de fornecedores que contenha niFornecedor e UF.")
    df=contracts.copy()
    df["valorGlobal"]=pd.to_numeric(df["valorGlobal"],errors="coerce")
    sup=suppliers[["niFornecedor","uf"]].drop_duplicates("niFornecedor")
    merged=df.merge(sup,on="niFornecedor",how="left")
    return merged.dropna(subset=["uf","valorGlobal"]).groupby("uf",as_index=False)["valorGlobal"].sum()
def health_payload(): return {"status":"ok","service":"compras-publicas"}
