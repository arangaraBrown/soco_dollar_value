from Qualtrics_API_requests import get_qualtrics_data
from Amazon_requests import get_dynamo_data
from estimation import post_estimate
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import lognorm
import random

random.seed(0)
# User Defined Parameters
WTP_max = 1
p_max = 1

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
output_recent = output.tail(10)
output.to_csv('output.csv', index=False)

# # # Filter data based on user defined WTP_max
# initial_count = len(output)
# output = output[output['mean'] <= WTP_max]
# # output = output[output['p.mean'] <= p_max]
# final_count = len(output)
# rejected_count = initial_count - final_count

# initial_count_recent = len(output_recent)
# output_recent = output_recent[output_recent['WTP.median'] <= WTP_max]
# final_count_recent = len(output_recent)
# rejected_count_recent = initial_count_recent - final_count_recent

# print(f"Number of surveys rejected: {rejected_count}")
# print(f"Number of surveys accepted: {final_count}")
# print(f"Percentage of surveys accepted: {100 - rejected_count/initial_count*100}%")
# print(f"Percentage of last 10 surveys accepted: {100 - rejected_count_recent/initial_count_recent*100}%")

# output['rupee_wtp'] = np.multiply(output['WTP.mean'], output['current_wage'])
# monthly_wtp = np.mean(output[output['wage_type'] == 'Monthly']['rupee_wtp'])

# # Save output to csv
# output.to_csv('output.csv', index=False)

# bins = np.arange(0, .85, 0.05)  
# plt.rcParams["font.size"] = 22
# plt.hist(output['WTP.mean'], bins=bins, density=True, alpha=0.5, color='skyblue', edgecolor='black', label='Data Density')

# wtp_mean = np.mean(output['WTP.mean'])
# wtp_std = np.std(output['WTP.mean'])
# sigma = np.sqrt(np.log(1 + (np.square(wtp_std))/(np.square(wtp_mean))))
# mu =  np.log(wtp_mean) - (np.square(wtp_std))/2
# x = np.linspace(0,0.8, 1000)
# pdf_values = lognorm.pdf(x,s=sigma, scale = np.exp(mu))
# plt.plot(x, pdf_values, 'b-', lw=2, label='Lognormal PDF')

# percentile_with_benefit = (len(output[output['has_benefit'] == "Yes"]) +  0.5*(len(output[output['has_benefit'] == "Partly"])))/ len(output.dropna(subset=['has_benefit']))
# implied_price = lognorm.ppf((1-percentile_with_benefit),s=sigma, scale = np.exp(mu))

# plt.text(0.45, max(plt.ylim())*0.85, f'Mean WTP: {wtp_mean*100:.2f}% / ₹{monthly_wtp:.2f} \nFraction with Benefit: {percentile_with_benefit:.2f}% \nMarginal WTP: {implied_price:.2f}%')
# plt.xlabel('Willigness To Pay')
# plt.yticks([])
# plt.xticks(np.arange(0, 0.9, 0.1), [f'{int(x*100)}%' for x in np.arange(0, 0.9, 0.1)])
# plt.show()

# # average_wta = np.average(output[output['has_benefit'] == "Yes"]['WTP.mean'])
# # average_wtp = np.average(output[output['has_benefit'] == "No"]['WTP.mean'])

# # print(f"Average WTA: {average_wta}")
# # print(f"Average WTP: {average_wtp}")

# # # Create a new column for bins of WTP.mean using the same bin edges as before
# output['wtp_bin'] = pd.cut(output['WTP.mean'], bins=bins, right=False)

# # Aggregate the data: count total respondents and those with benefit per bin
# bin_summary = output.groupby('wtp_bin').agg(
#     total=('profile_id', 'count'),
#     benefit_count=('has_benefit', lambda x: (x == "Yes").sum() + 0.5 * (x == "Partly").sum())
# ).reset_index()

# # Calculate the fraction of respondents with the benefit in each bin
# bin_summary['fraction'] = bin_summary['benefit_count'] / bin_summary['total']

# # Calculate the midpoint of each bin for plotting
# bin_summary['midpoint'] = bin_summary['wtp_bin'].apply(lambda interval: interval.left + (interval.right - interval.left) / 2)

# # Create the scatterplot
# plt.scatter(bin_summary['midpoint'], bin_summary['fraction'], color='red',s=200)
# plt.xlabel('Willigness To Pay')
# plt.ylabel('Likelihood of Having Benefit')
# plt.show()


# # # # # # Plot Histogram of WTP estimates for each benefit
# # for group in output.groupby('param'): 
# #     half_1 = group[1]['WTP.mean'][:len(group[1])//2]
# #     half_2 = group[1]['WTP.mean'][len(group[1])//2:]
# #     # print(f"{group[0]} WTP Estimate: {np.average(group[1]['WTP.mean'])}")
# #     # print(f"{group[0]} WTP Estimate 1: {np.average(half_1)}")
# #     # print(f"{group[0]} WTP Estimate 2: {np.average(half_2)}")

# #     plt.hist(group[1]['WTP.mean'], bins=bins, density=True, alpha=0.5, color='skyblue', edgecolor='black', label='Data Density')

# #     wtp_mean = np.mean(group[1]['WTP.mean'])
# #     wtp_std = np.std(group[1]['WTP.mean'])
# #     sigma = np.sqrt(np.log(1 + (np.square(wtp_std))/(np.square(wtp_mean))))
# #     mu =  np.log(wtp_mean) - (np.square(wtp_std))/2
# #     x = np.linspace(0,0.8, 1000)
# #     pdf_values = lognorm.pdf(x,s=sigma, scale = np.exp(mu))
# #     plt.plot(x, pdf_values, 'b-', lw=2, label='Lognormal PDF')

# #     #need to add for partlys for the AL + PS
# #     percentile_with_benefit = len(group[1][group[1]['has_benefit'] == "Yes"]) / len(group[1].dropna(subset=['has_benefit']))
# #     implied_price = lognorm.ppf((1-percentile_with_benefit),s=sigma, scale = np.exp(mu))
# #     #print(f"{group[0]} Implied Price: {implied_price}")
# #     average_wta = np.average(group[1][group[1]['has_benefit'] == "Yes"]['WTP.mean'])
# #     average_wtp = np.average(group[1][group[1]['has_benefit'] == "No"]['WTP.mean'])

# #     plt.xlabel('WTP')
# #     plt.ylabel('Density')
# #     plt.title(f'Histogram of WTP Estimates:{group[0]}')
# #     plt.show()



