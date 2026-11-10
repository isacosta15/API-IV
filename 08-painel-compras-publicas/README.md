# Painel de Compras Públicas Federais

## Funcionalidades implementadas
- Integração real com `GET /modulo-contratos/1_consultarContratos`.
- Integração real com `GET /modulo-fornecedor/1_consultarFornecedor` (cadastro de fornecedores/SICAF).
- Filtros por órgão, intervalo de vigência, CNPJ e CNAE.
- Paginação `pagina` e `tamanhoPagina` (máximo 500).
- Controle de paginação automática limitada e respeito ao rate limit.
- Indicadores de valores, ranking de fornecedores e ranking de órgãos na amostra consultada.
- Serviços analíticos para agregar valores por UF mediante cruzamento com UF do cadastro do fornecedor.
- Exportação CSV e Swagger FastAPI.

## Observações importantes
O endpoint de contratos exige `codigoOrgao`, `dataVigenciaInicialMin` e `dataVigenciaInicialMax`. Por isso, a interface solicita o código do órgão. A API oficial limita o uso a 100 chamadas por minuto e recomenda até 500 itens por página. O painel deixa claro que o ranking corresponde ao conjunto consultado; para consolidar Brasil inteiro é necessário percorrer órgãos e páginas respeitando os limites. O mapa por UF pode ser gerado quando o conjunto de contratos for enriquecido com os campos `niFornecedor` e `uf` da consulta de fornecedores.

## Instalação e execução
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
Em outro terminal: `streamlit run frontend/app.py`
- Dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs

## Endpoints locais
- `GET /api/v1/contratos?codigo_orgao=...&date_min=2024-01-01&date_max=2025-12-31`
- `GET /api/v1/fornecedores?pagina=1&tamanho_pagina=500`

## Fontes oficiais
- Portal: https://www.gov.br/compras/pt-br/cidadao/portal-de-dados-abertos
- Swagger: https://dadosabertos.compras.gov.br/swagger-ui/index.html
- Manual técnico: https://manual-api-compras.readthedocs.io/pt-br/latest/
- Limites, paginação e parâmetros detalhados no manual oficial.

## Testes
`pytest -q`
