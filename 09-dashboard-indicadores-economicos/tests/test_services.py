import pandas as pd
from backend.services import normalize_series,correlation_analysis
def test_normalize_and_corr():
 d1=pd.DataFrame({"data":pd.date_range("2020-01-01",periods=6,freq="MS"),"valor":[1,2,3,4,5,6]})
 d2=pd.DataFrame({"data":pd.date_range("2020-01-01",periods=6,freq="MS"),"valor":[2,4,6,8,10,12]})
 assert normalize_series(d1).base_100.iloc[0]==100
 assert correlation_analysis(d1,d2)["correlacao"]>.99
