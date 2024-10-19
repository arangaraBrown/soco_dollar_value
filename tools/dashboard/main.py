from Qualtrics_API_requests import get_qualtrics_data
from Amazon_requests import get_dynamo_data
from estimation import post_estimate
import pandas as pd
import matplotlib.pyplot as plt

# User Defined Parameters
p_reject = 0.5
WTP_max = 0.8

# Get data from Qualtrics API
qualtrics_data = get_qualtrics_data()

# Get data from DynamoDB
dynamo_data = get_dynamo_data()
dynamo_data = [item for item in dynamo_data if item['profile_id'] in qualtrics_data['profile_id'].values]

# Estimate WTP and p values
output = post_estimate(dynamo_data, 1)
output.drop(columns=['n_designs'], inplace=True)

# merge data
output = pd.merge(qualtrics_data, output, on='profile_id', how='inner')

# Filter data based user defined parameters
output = output[output['p.median'] <= p_reject]
output = output[output['WTP.median'] <= WTP_max]

# Save output to csv
output.to_csv('output.csv', index=False)

# Plot Histogram of WTP estimates
plt.hist(output['WTP.median'], bins=10)
plt.xlabel('WTP')
plt.ylabel('Frequency')
plt.title('Histogram of WTP Estimates')
plt.show()

# Plot Histogram of WTP estimates for each benefit
for group in output.groupby('param'):
    plt.hist(group[1]['WTP.median'], bins=10)
    plt.xlabel('WTP')
    plt.ylabel('Frequency')
    plt.title(f'Histogram of WTP Estimates for {group[0]}')
    plt.show()



