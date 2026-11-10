import streamlit as st, pandas as pd, requests, plotly.express as px
st.set_page_config(page_title="AgroClima",layout="wide")
st.title("Monitor de Indicadores Agropecuários e Climáticos")
st.caption("IBGE/PAM + CPTEC/INPE | produção, precipitação, correlação e mapa por UF")
api=st.sidebar.text_input("Backend","http://localhost:8000")
uf=st.sidebar.selectbox("Estado",["SP","PR","RS","MG","GO","MT","MS","BA","SC","TO","MA","PI","PA","RO","AC","AM","RR","AP","CE","RN","PB","PE","AL","SE","ES","RJ","DF"])
crop=st.sidebar.selectbox("Cultura",["soja","milho","arroz","café","feijão","algodão"])
start,end=st.sidebar.slider("Período",2000,2025,(2015,2025))
if st.button("Consultar produção",type="primary"):
    try:
        r=requests.get(api+"/api/v1/agro/producao",params={"uf":uf,"cultura":crop,"ano_inicio":start,"ano_fim":end},timeout=90); r.raise_for_status()
        st.session_state.agro=pd.DataFrame(r.json()["dados"])
    except Exception as e: st.error(str(e))
df=st.session_state.get("agro")
if df is not None and not df.empty:
    a,b=st.columns(2); a.metric("Anos retornados",len(df)); b.metric("Produção mais recente",f"{df.producao_ton.iloc[-1]:,.0f} t")
    st.plotly_chart(px.line(df,x="ano",y="producao_ton",markers=True,title=f"Produção de {crop} — {uf}"),use_container_width=True)
    st.dataframe(df,use_container_width=True)
    st.download_button("Exportar produção CSV",df.to_csv(index=False).encode(), "producao.csv")
st.divider()
st.subheader("Comparação com precipitação histórica")
st.write("Para a análise histórica, carregue um CSV com as colunas `ano` e `precipitacao_mm` (precipitação acumulada anual da mesma UF/região). O CPTEC sazonal fornece previsão/anomalia sazonal, não uma série observada anual longa.")
clim=st.file_uploader("CSV de precipitação histórica",type="csv")
if clim and df is not None:
    try:
        cdf=pd.read_csv(clim); merged=df.merge(cdf[["ano","precipitacao_mm"]],on="ano")
        if len(merged)>=3:
            corr=merged.producao_ton.corr(merged.precipitacao_mm)
            st.metric("Correlação de Pearson",f"{corr:.3f}")
            st.plotly_chart(px.scatter(merged,x="precipitacao_mm",y="producao_ton, trendline='ols'",title="Precipitação acumulada × produção"),use_container_width=True)
            st.dataframe(merged)
        else: st.warning("São necessários ao menos três anos coincidentes.")
    except Exception as e: st.error(str(e))
st.divider()
st.subheader("Mapa de produtividade por estado")
map_year=st.number_input("Ano do mapa",2000,2025,2024)
if st.button("Gerar mapa nacional"):
    try:
        r=requests.get(api+"/api/v1/agro/estados",params={"cultura":crop,"ano":int(map_year)},timeout=180); r.raise_for_status()
        st.session_state.states=pd.DataFrame(r.json()["dados"])
    except Exception as e: st.error(str(e))
states=st.session_state.get("states")
if states is not None and not states.empty:
    # mapa de calor por UF com geometria GeoJSON oficial do IBGE
    try:
        geo=requests.get("https://servicodados.ibge.gov.br/api/v3/malhas/estados?formato=application/vnd.geo+json&qualidade=intermediaria",timeout=60).json()
        fig=px.choropleth(states,geojson=geo,locations="uf",featureidkey="properties.sigla",color="producao_ton",
                         color_continuous_scale="YlGn",scope="south america",title=f"Produção por UF — {crop} ({map_year})")
        fig.update_geos(fitbounds="locations",visible=False); st.plotly_chart(fig,use_container_width=True)
    except Exception as e: st.warning(f"Não foi possível desenhar o mapa: {e}")
st.divider()
st.subheader("Previsão sazonal CPTEC/INPE")
date=st.text_input("Data de emissão (AAAAMM)",value="202611")
if st.button("Consultar previsão sazonal"):
    try:
        r=requests.get(api+"/api/v1/clima/previsao",params={"date":date,"variavel":"prec"},timeout=180); r.raise_for_status()
        st.json(r.json())
    except Exception as e: st.error(str(e))
