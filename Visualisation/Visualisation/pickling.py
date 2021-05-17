import pandas as pd
df2 = pd.read_excel('LUCAS_TOPSOIL_v1.xls')
df2.to_pickle('Lucas.pkl')