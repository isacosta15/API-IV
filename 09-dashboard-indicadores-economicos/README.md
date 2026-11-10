# Dashboard de Indicadores Econômicos Brasileiros

## Funcionalidades
- Integração com Banco Central/SGS para séries temporais.
- Integração OData do Ipeadata: catálogo/metadados e valores por SERCODIGO.
- Seleção de até cinco indicadores BCB e normalização em base 100.
- Harmonização de frequências diária/mensal/trimestral/anual.
- Comparação de indicadores de fontes distintas (BCB e Ipeadata por meio dos serviços backend e exportação).
- Correlação de Pearson, regressão linear, R², p-valor, dispersão e linha de tendência.
- API FastAPI e dashboard Streamlit.

## Executar
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
Em outro terminal: `streamlit run frontend/app.py`
- Frontend: http://localhost:8501
- Swagger: http://localhost:8000/docs

## Endpoints
- `GET /api/v1/bcb/{codigo}?data_inicio=01/01/2015&data_fim=31/12/2025`
- `GET /api/v1/ipeadata/catalogo?busca=PIB&limite=100`
- `GET /api/v1/ipeadata/{SERCODIGO}`

## Séries BCB pré-configuradas
- SGS 432 — Selic diária
- SGS 433 — IPCA mensal
- SGS 1 — câmbio USD compra
- SGS 189 — IGP-M
- SGS 24369 — PNAD/indicador de desemprego (verifique a descrição e frequência no catálogo SGS antes de uso)

Os códigos e periodicidades devem ser validados no catálogo SGS; a aplicação aceita qualquer código numérico.

## Fontes
- API SGS: https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json
- Catálogo SGS: https://www3.bcb.gov.br/sgspub/
- API Ipeadata: https://www.ipeadata.gov.br/api/odata4/
- Documentação OData: https://ipeadata.gov.br/api/

## Metodologia
A normalização usa primeiro valor válido como base 100. A frequência comum é harmonizada por média (`MS`, `QS`, `YS`); escolha a frequência com critério. Correlação é calculada somente em datas coincidentes, com ao menos três observações, e não indica causalidade.

## Testes
`pytest -q`
