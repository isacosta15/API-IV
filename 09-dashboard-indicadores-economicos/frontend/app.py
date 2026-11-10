import streamlit as st,pandas as pd,requests,plotly.express as px
from scipy.stats import linregress
st.set_page_config(page_title="Indicadores Econômicos",layout="wide")
st.title("Dashboard de Indicadores Econômicos Brasileiros")
st.caption("Banco Central/SGS + Ipeadata | comparação base 100, frequências e correlação")
api=st.sidebar.text_input("Backend","http://localhost:8000")
d1=st.sidebar.date_input("Data inicial",pd.Timestamp("2015-01-01")); d2=st.sidebar.date_input("Data final",pd.Timestamp("2025-12-31"))
freq=st.sidebar.selectbox("Frequência comum",["MS","QS","YS"],format_func={"MS":"Mensal","QS":"Trimestral","YS":"Anual"}.get)
st.subheader("Indicadores do Banco Central")
labels=list({"Selic diária (432)":432,"IPCA mensal (433)":433,"Câmbio USD compra (1)":1,"IGP-M mensal (189)":189,"Desemprego PNAD (24369)":24369})
selected=st.multiselect("Selecione até cinco indicadores",labels,default=labels[:2],max_selections=5)
if st.button("Carregar séries BCB",type="primary"):
 frames=[]
 for label in selected:
  code={"Selic diária (432)":432,"IPCA mensal (433)":433,"Câmbio USD compra (1)":1,"IGP-M mensal (189)":189,"Desemprego PNAD (24369)":24369}[label]
  try:
   r=requests.get(f"{api}/api/v1/bcb/{code}",params={"data_inicio":d1.strftime("%d/%m/%Y"),"data_fim":d2.strftime("%d/%m/%Y")},timeout=90); r.raise_for_status()
   df=pd.DataFrame(r.json()["dados"])
   if not df.empty: df["data"]=pd.to_datetime(df.data); frames.append((label,df))
  except Exception as e: st.error(f"{label}: {e}")
 st.session_state.bcb_frames=frames
frames=st.session_state.get("bcb_frames",[])
if frames:
 parts=[]
 for label,df in frames:
  x=df.set_index("data").valor.resample(freq).mean().dropna().reset_index()
  if not x.empty: x["base_100"]=x.valor/x.valor.iloc[0]*100; x["indicador"]=label; parts.append(x)
 if parts:
  chart=pd.concat(parts)
  st.plotly_chart(px.line(chart,x="data",y="base_100",color="indicador",title="Comparação normalizada — base 100"),use_container_width=True)
  st.dataframe(chart,use_container_width=True)
  st.download_button("Exportar comparação CSV",chart.to_csv(index=False).encode(),"comparacao_bcb.csv")
st.divider()
st.subheader("Séries do Ipeadata")
search=st.text_input("Buscar série por nome/tema",placeholder="Ex.: PIB, população, renda")
if st.button("Buscar catálogo Ipeadata"):
 try:
  r=requests.get(api+"/api/v1/ipeadata/catalogo",params={"busca":search,"limite":100},timeout=90); r.raise_for_status()
  st.session_state.ipea_catalog=pd.DataFrame(r.json()["dados"])
 except Exception as e: st.error(str(e))
catalog=st.session_state.get("ipea_catalog")
if catalog is not None and not catalog.empty:
 st.dataframe(catalog,use_container_width=True)
 code=st.selectbox("Código da série (SERCODIGO)",catalog.SERCODIGO.astype(str).tolist())
 if st.button("Carregar série Ipeadata"):
  try:
   r=requests.get(f"{api}/api/v1/ipeadata/{code}",timeout=90); r.raise_for_status()
   x=pd.DataFrame(r.json()["dados"]); x["data"]=pd.to_datetime(x.data)
   st.session_state.ipea_loaded=x
  except Exception as e: st.error(str(e))
ipea=st.session_state.get("ipea_loaded")
if ipea is not None and not ipea.empty:
 st.plotly_chart(px.line(ipea,x="data",y="valor",title="Série histórica Ipeadata"),use_container_width=True)
 st.dataframe(ipea,use_container_width=True)
 st.download_button("Exportar Ipeadata CSV",ipea.to_csv(index=False).encode(),"ipeadata.csv")
st.divider()
st.subheader("Correlação entre dois indicadores")
st.write("Carregue duas séries e selecione a frequência comum para alinhar datas.")
if len(frames)>=2:
 names=[x[0] for x in frames]
 left=st.selectbox("Indicador X",names,index=0); right=st.selectbox("Indicador Y",names,index=1)
 if st.button("Calcular correlação"):
  try:
   a=dict(frames)[left].set_index("data").valor.resample(freq).mean().dropna().rename("x")
   b=dict(frames)[right].set_index("data").valor.resample(freq).mean().dropna().rename("y")
   m=pd.concat([a,b],axis=1).dropna()
   if len(m)<3: st.warning("Poucas observações coincidentes.")
   else:
    fit=linregress(m.x,m.y); st.metric("Correlação de Pearson",f"{m.x.corr(m.y):.4f}")
    st.caption(f"R² = {fit.rvalue**2:.4f} | p-valor = {fit.pvalue:.4g} | n = {len(m)}")
    m=m.reset_index(); m["tendencia"]=fit.intercept+fit.slope*m.x
    fig=px.scatter(m,x="x",y="y",trendline="ols",title=f"{left} × {right}")
    st.plotly_chart(fig,use_container_width=True)
  except Exception as e: st.error(str(e))
else: st.info("Carregue pelo menos duas séries BCB para habilitar a correlação.")
st.info("Correlação não implica causalidade. A agregação de frequência utiliza média aritmética; escolha a frequência considerando a natureza econômica de cada série.")
