import pandas as pd
from backend.services import rank_suppliers,aggregate_contracts_by_state
def test_rank():
 d=pd.DataFrame({"nomeRazaoSocialFornecedor":["A","B","A"],"valorGlobal":[10,30,20]})
 assert rank_suppliers(d).iloc[0]["nomeRazaoSocialFornecedor"]=="A"
def test_state_aggregate():
 c=pd.DataFrame({"niFornecedor":["1","2"],"valorGlobal":[10,20]})
 s=pd.DataFrame({"niFornecedor":["1","2"],"uf":["SP","RJ"]})
 assert len(aggregate_contracts_by_state(c,s))==2
