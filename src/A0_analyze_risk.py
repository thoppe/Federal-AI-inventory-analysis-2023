import json
import pandas as pd

f_json = "data/GPT_automated_analysis.json"
with open(f_json) as FIN:
    js = json.load(FIN)


df = pd.DataFrame(js['record_content'])

df['risk_assessment_safety'] = js['risk_assessment_safety']
df['risk_assessment_rights'] = js['risk_assessment_rights']

for key in ['risk_assessment_rights', 'risk_assessment_safety']:
    S0 = df[key].str.lower().str.startswith("yes")
    S1 = df[key].str.lower().str.startswith("no")
    S2 = ~(S0+S1)
    
    df[f'is_{key}'] = S0|S2

    df.loc[S1, key] = None


df['n_risk'] = df[['is_risk_assessment_rights', 'is_risk_assessment_safety']].sum(axis=1)
df = df.sort_values('n_risk',ascending=False)
del df['n_risk']

df = df.set_index('Use_Case_ID')

f_save = 'results/Safety_Rights_impacting_scan.csv'
df.to_csv(f_save)
print(df)

