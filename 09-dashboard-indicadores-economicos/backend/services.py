import requests,pandas as pd,numpy as np
from scipy.stats import linregress
from backend.config import REQUEST_TIMEOUT
BCB="https://api.bcb.gov.br/dados/serie/bcdata.sgs"
IPEA="https://www.ipeadata.gov.br/api/odata4"
BCB_CATALOG={"Selic diária (432)":432,"IPCA mensal (433)":433,"Câmbio USD compra (1)":1,
             "IGP-M mensal (189)":189,"Desemprego PNAD (24369)":24369}
def fetch_bcb(code:int,start:str,end:str):
 url=f"{BCB}.{code}/dados"
 r=requests.get(url,params={"formato":"json","dataInicial":start,"dataFinal":end},timeout=REQUEST_TIMEOUT); r.raise_for_status()
 df=pd.DataFrame(r.json())
 if df.empty: return pd.DataFrame(columns=["data","valor","fonte","codigo"])
 df["data"]=pd.to_datetime(df["data"],dayfirst=True,errors="coerce")
 df["valor"]=pd.to_numeric(df["valor"].astype(str).str.replace(",",".",regex=False),errors="coerce")
 df["fonte"]="BCB/SGS"; df["codigo"]=str(code)
 return df.dropna(subset=["data","valor"])[["data","valor","fonte","codigo"]]
def fetch_ipea_metadata(search:str|None=None,top:int=100):
 r=requests.get(IPEA+"/Metadados",params={"$format":"json","$top":top},timeout=REQUEST_TIMEOUT); r.raise_for_status()
 df=pd.DataFrame(r.json().get("value",[]))
 if search and not df.empty:
  col="SERNOME" if "SERNOME" in df else df.columns[0]
  df=df[df[col].astype(str).str.contains(search,case=False,na=False)]
 return df
def fetch_ipea(code:str):
 url=f"{IPEA}/ValoresSerie(SERCODIGO='{code}')"
 r=requests.get(url,params={"$format":"json"},timeout=REQUEST_TIMEOUT); r.raise_for_status()
 df=pd.DataFrame(r.json().get("value",[]))
 if df.empty: return pd.DataFrame(columns=["data","valor","fonte","codigo"])
 date_col=next((x for x in ["VALDATA","data"] if x in df),None)
 value_col=next((x for x in ["VALVALOR","valor"] if x in df),None)
 if not date_col or not value_col: raise ValueError(f"Campos não reconhecidos: {list(df.columns)}")
 return pd.DataFrame({"data":pd.to_datetime(df[date_col],errors="coerce"),
                      "valor":pd.to_numeric(df[value_col],errors="coerce"),"fonte":"IPEADATA","codigo":code}).dropna()
def to_frequency(df:pd.DataFrame,freq:str):
 if freq not in {"D","MS","QS","YS"}: raise ValueError("Frequência deve ser D, MS, QS ou YS.")
 x=df.set_index("data")["valor"].sort_index()
 return x.resample(freq).mean().dropna().rename("valor").reset_index()
def normalize_series(df:pd.DataFrame):
 out=df.sort_values("data").copy()
 if out.empty or out.valor.iloc[0]==0: raise ValueError("Série vazia ou valor-base igual a zero.")
 out["base_100"]=out.valor/out.valor.iloc[0]*100
 return out
def compare_series(series:list[pd.DataFrame],labels:list[str],freq:str="MS"):
 if len(series)>5: raise ValueError("Selecione no máximo cinco indicadores.")
 parts=[]
 for frame,label in zip(series,labels):
  d=to_frequency(frame,freq); d=normalize_series(d); d["indicador"]=label; parts.append(d)
 return pd.concat(parts,ignore_index=True) if parts else pd.DataFrame()
def correlation_analysis(left:pd.DataFrame,right:pd.DataFrame,freq:str="MS"):
 a=to_frequency(left,freq).rename(columns={"valor":"x"})
 b=to_frequency(right,freq).rename(columns={"valor":"y"})
 m=a.merge(b,on="data").dropna()
 if len(m)<3: raise ValueError("São necessárias pelo menos três observações coincidentes.")
 fit=linregress(m.x,m.y)
 return {"correlacao":float(m.x.corr(m.y)),"slope":float(fit.slope),"intercept":float(fit.intercept),
         "r_squared":float(fit.rvalue**2),"p_value":float(fit.pvalue),"n":len(m),"dados":m}
def health_payload(): return {"status":"ok","service":"indicadores-economicos"}
