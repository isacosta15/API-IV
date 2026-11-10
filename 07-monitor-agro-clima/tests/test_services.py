import pandas as pd
from backend.services import merge_production_climate, correlation_summary
def test_merge_and_corr():
    p=pd.DataFrame({"ano":[2020,2021,2022],"producao_ton":[10,20,30]})
    c=pd.DataFrame({"ano":[2020,2021,2022],"precipitacao_mm":[100,110,120]})
    m=merge_production_climate(p,c)
    assert correlation_summary(m)["correlacao_pearson"] > .99
