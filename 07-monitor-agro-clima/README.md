# Monitor de Indicadores Agropecuários e Climáticos

Aplicação full-stack Python: FastAPI + Streamlit, IBGE/SIDRA PAM e CPTEC/INPE sazonal.

## Critérios implementados
- Seleção de UF e cultura (soja, milho, arroz, café, feijão e algodão).
- Consulta anual da quantidade produzida no IBGE/SIDRA (tabela 5457, variável 214).
- Série histórica de produção e exportação CSV.
- Consulta de previsão sazonal CPTEC/INPE usando a biblioteca Python `sazonal`, com grade espacial e resumo estatístico.
- Mapa coroplético por UF com produção estadual da cultura selecionada.
- Cruzamento da produção com precipitação acumulada histórica, correlação de Pearson e dispersão com tendência.
- API documentada automaticamente em `/docs`.

## Limitação metodológica explícita
A previsão sazonal do CPTEC/INPE é um produto de previsão/anomalia, não um histórico anual observado de precipitação. Para a correlação histórica, o dashboard aceita CSV com `ano,precipitacao_mm`; não fabrica uma série histórica. O endpoint sazonal busca a grade real do CPTEC. Essa separação evita correlacionar previsão futura com produção observada de anos passados como se fossem observações equivalentes.

## Instalação
Python 3.10+ (recomenda-se ambiente Linux/WSL para bibliotecas científicas).
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
Em outro terminal:
```bash
streamlit run frontend/app.py
```
Frontend `localhost:8501`; API `localhost:8000/docs`.

## Formato do CSV climático
```csv
ano,precipitacao_mm
2019,1240.5
2020,1188.2
2021,1320.0
```
Use precipitação acumulada anual na mesma unidade espacial (UF/região) e período da produção.

## Fontes
- SIDRA tabela 5457: https://sidra.ibge.gov.br/tabela/5457
- API IBGE: https://servicodados.ibge.gov.br/api/docs/agregados
- CPTEC sazonal: https://sazonal.cptec.inpe.br/
- Biblioteca Python e instruções: https://sazonal.readthedocs.io/

## Execução de testes
`pytest -q`
