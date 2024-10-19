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
    columns_to_keep = ['RecordedDate','profile_id','Q2','Q49','Q3','Q12']
    df = df[columns_to_keep]
    en_hi_cols = {'Q3':'Q12'}
    for col in en_hi_cols.keys():
        df[col] = df[col].combine_first(df[en_hi_cols[col]])
        df.drop(columns=en_hi_cols[col], inplace=True)
    df.rename(columns={'Q2':'lang','Q49':'enum','Q3':'WFC'}, inplace=True)
    df = df[df['enum']!='Ari']
    df.loc[(df['WFC'] == 'Saki Naka') & (df['RecordedDate'] < dt.datetime(year = 2024, month = 10, day = 19)), 'WFC'] = 'Company Visit'
    return df
