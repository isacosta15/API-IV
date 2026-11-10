import streamlit as st,pandas as pd,requests,plotly.express as px
st.set_page_config(page_title="Compras Públicas",layout="wide")
st.title("Painel de Compras Públicas Federais")
st.caption("Contratos, fornecedores, valores, distribuição por UF e ranking")
api=st.sidebar.text_input("Backend","http://localhost:8000")
st.sidebar.markdown("[Swagger oficial](https://dadosabertos.compras.gov.br/swagger-ui/index.html) · [Manual](https://manual-api-compras.readthedocs.io/pt-br/latest/)")
with st.sidebar.form("filtros"):
    org=st.text_input("Código do órgão (obrigatório)",help="O endpoint de contratos exige codigoOrgao.")
    d1=st.date_input("Início da vigência",value=pd.Timestamp("2024-01-01"))
    d2=st.date_input("Fim da vigência",value=pd.Timestamp("2025-12-31"))
    page=st.number_input("Página inicial",1,100000,1)
    pages=st.slider("Páginas a percorrer",1,20,5)
    size=st.slider("Registros por página",10,500,500,10)
    submit=st.form_submit_button("Consultar contratos",type="primary")
if submit:
    try:
        r=requests.get(api+"/api/v1/contratos",params={"codigo_orgao":org,"date_min":d1.isoformat(),"date_max":d2.isoformat(),"pagina":int(page),"tamanho_pagina":int(size),"auto_paginas":int(pages)},timeout=180)
        r.raise_for_status(); st.session_state.contracts=pd.DataFrame(r.json()["dados"])
        st.session_state.contract_meta=r.json()["metadados"]
    except Exception as e: st.error(str(e))
df=st.session_state.get("contracts")
if df is not None and not df.empty:
    df["valorGlobal"]=pd.to_numeric(df.get("valorGlobal"),errors="coerce")
    total=df.valorGlobal.sum()
    a,b,c=st.columns(3); a.metric("Contratos retornados",len(df)); b.metric("Valor global somado",f"R$ {total:,.2f}"); c.metric("Páginas totais (API)",st.session_state.contract_meta.get("totalPaginas","—"))
    st.plotly_chart(px.bar(df.groupby("nomeOrgao",as_index=False).valorGlobal.sum().nlargest(10,"valorGlobal"),x="nomeOrgao",y="valorGlobal",title="Top 10 órgãos por valor global"),use_container_width=True)
    st.dataframe(df,use_container_width=True)
    st.download_button("Exportar contratos CSV",df.to_csv(index=False).encode(),"contratos.csv")
    st.divider(); st.subheader("Ranking dos 10 fornecedores")
    ranking=df.groupby("nomeRazaoSocialFornecedor",as_index=False).valorGlobal.sum().nlargest(10,"valorGlobal")
    st.plotly_chart(px.bar(ranking,x="valorGlobal",y="nomeRazaoSocialFornecedor",orientation="h",title="Fornecedores por valor contratado"),use_container_width=True)
    st.caption("O ranking reflete apenas os contratos consultados nas páginas e órgão selecionados.")
else:
    st.info("Informe o código do órgão e o período. A API oficial exige esses parâmetros para consultar contratos.")
st.divider()
st.subheader("Consulta de fornecedores / SICAF")
with st.form("supplier"):
    cnpj=st.text_input("CNPJ (opcional)")
    cnae=st.number_input("CNAE (opcional; 0 = todos)",min_value=0,value=0)
    sp=st.number_input("Página de fornecedores",1,100000,1)
    ss=st.form_submit_button("Consultar fornecedores")
if ss:
    try:
        params={"pagina":int(sp),"tamanho_pagina":500}
        if cnpj: params["cnpj"]=cnpj
        if cnae: params["codigo_cnae"]=int(cnae)
        r=requests.get(api+"/api/v1/fornecedores",params=params,timeout=90); r.raise_for_status()
        sdf=pd.DataFrame(r.json()["dados"]); st.session_state.suppliers=sdf
    except Exception as e: st.error(str(e))
sdf=st.session_state.get("suppliers")
if sdf is not None:
    st.metric("Fornecedores retornados",len(sdf)); st.dataframe(sdf,use_container_width=True)
    st.download_button("Exportar fornecedores CSV",sdf.to_csv(index=False).encode(),"fornecedores.csv")
st.warning("A API de contratos filtra por código do órgão e vigência. Para ranking nacional completo, percorra órgãos e todas as páginas dentro do limite oficial de chamadas; uma amostra parcial não representa o total federal.")
