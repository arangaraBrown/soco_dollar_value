from QualtricsAPI import Credentials
from QualtricsAPI.Survey import Responses
import pandas as pd
import datetime as dt

def get_qualtrics_data():
    Credentials().qualtrics_api_credentials(token='9ISA2H5BZcTcyKLOVbGNWCWiipf4wz9fLzYGMZ6X', data_center='iad1')
    df = Responses().get_survey_responses(survey='SV_aavJvw1DJO7ogB0',verify=None,useLabels=True)
    df = df[df['Finished'] == 'True']
    df['RecordedDate'] = pd.to_datetime(df['RecordedDate'])
    df = df[df['RecordedDate'] >= '2024-08-01']
    df = df[df['Q50'].str.contains('No', na=False)]
    columns_to_keep = ['RecordedDate','profile_id','Q2','Q49','Q3','Q12','Q4', 'Q5', 'Q61',	'Q6', 'Q7', 'Q8', 'Q9', 'Q10','Q13','Q62',
                       'Q14','Q15','Q16','Q17','Q18','Q19','Q74','Q73','Q55','Q57','Q63','Q64','Q93','Q89','Q11','Q20','Q83','Q85','Q86','Q87','Q88','Q90'
                       ,'Q92','Q82','Q101','Q78','Q38','Q52','Q39','Q21','Q53','Q22']
    df = df[columns_to_keep]
    df['num_family_members'] = df[['Q83', 'Q85', 'Q86', 'Q87', 'Q88', 'Q90']].apply(lambda x: ' '.join(x.dropna()), axis=1)
    df['current_wage'] = df[['Q38','Q52','Q39','Q21','Q53','Q22']].apply(lambda x: float(' '.join(x.dropna())), axis=1)
    #df = df[~((df['Q74'] == 'No') | (df['Q73'] == 'No') | (df['Q93'] == 'No') | (df['Q89'] == 'No'))]
    df.drop(columns=['Q74', 'Q73', 'Q93', 'Q89','Q85', 'Q83','Q86', 'Q87', 'Q88', 'Q90','Q38','Q52','Q39','Q21','Q53','Q22'], inplace=True)
    en_hi_cols = {'Q3':'Q12', 'Q4':'Q13','Q5': 'Q14','Q61':'Q62','Q6':'Q15','Q7':'Q16','Q8':'Q17','Q9':'Q18','Q10':'Q19', 'Q63':'Q64', 'Q55': 'Q57','Q11':'Q20',
                  'Q92':'Q101','Q82':'Q78'}
    for col in en_hi_cols.keys():
        df[col] = df[col].combine_first(df[en_hi_cols[col]])
        df.drop(columns=en_hi_cols[col], inplace=True)
    df['Q92_Q82_combined'] = df.apply(lambda row: 'Yes' if row['Q92'] == 'Yes' and row['Q82'] == 'Yes' else ('No' if row['Q92'] == 'No' and row['Q82'] == 'No' else ('Partly' if row['Q92'] == 'No' and row['Q82'] == 'Yes' else ('Partly' if row['Q92'] == 'Yes' and row['Q82'] == 'No' else ''))), axis=1)
    df.rename(columns={'Q2':'lang','Q49':'enum','Q3':'WFC', 'Q4':'age', 'Q5': 'gender', 'Q61': 'employment_status','Q6': 'industry','Q7':'industry_other','Q8':'local_migrant','Q9':'migrate_alone_family','Q10': 'state_of_origin', 'Q11': 'wage_type','Q55':
                       "Notes",'Q63':'has_benefit'}, inplace=True)
    df["has_benefit"] = df['has_benefit'].combine_first(df['Q92_Q82_combined'])
    df.drop(columns=['Q92_Q82_combined','Q92','Q82'], inplace=True)
    df = df[df['enum']!='Ari']
    df.loc[(df['WFC'] == 'Saki Naka') & (df['RecordedDate'] < dt.datetime(year = 2024, month = 10, day = 19)), 'WFC'] = 'Company Visit'
    return df

df = get_qualtrics_data()
