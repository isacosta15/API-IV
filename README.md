# Projetos Python — Integrações com Dados Complexos (Nível 3)

Três aplicações independentes com backend FastAPI e frontend Streamlit.

| Projeto | Fontes | Principais entregas |
|---|---|---|
| 07 Agroclima | IBGE/SIDRA + CPTEC/INPE | produção por UF/cultura, previsão sazonal, mapa estadual, correlação com precipitação histórica |
| 08 Compras públicas | Compras.gov.br | contratos, fornecedores, filtros, paginação, rankings e serviços de agregação por UF |
| 09 Economia | BCB/SGS + Ipeadata | séries, base 100, frequências, correlação e regressão |

Cada pasta contém seu próprio `requirements.txt`, `.env.example`, backend, frontend, testes e README.

## Rodar qualquer projeto
Entre na pasta desejada e siga seu README. Em geral, rode `uvicorn backend.main:app --reload` e em outro terminal `streamlit run frontend/app.py`.

## Publicação
Pode publicar este diretório como monorepo ou cada subpasta em repositório próprio. Nunca publique `.env`.
