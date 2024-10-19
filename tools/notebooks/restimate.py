# Import pandas
import pandas as pd

import os, sys, importlib
from pathlib import Path

def import_parents(level=1):
    global __package__
    file = Path(os.path.abspath('')).resolve()
    parent, top = file.parent, file.parents[level - 1]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError: # already removed
        pass

    __package__ = '.'.join(parent.parts[len(top.parts):])
    importlib.import_module(__package__) # won't be needed after that

import_parents(level=2)

# Import database connection and pmc function
from app.database.db import table, decimal_to_float
from app.bace.pmc_inference import pmc
from app.bace.user_config import answers
from app.bace.user_config import theta_params, size_thetas, likelihood_pdf


# Output file path.
output_file = "9_9_24.csv"


def clean_designs_and_answers(item, answers):

    str_answers = [str(answer) for answer in answers]

    design_hist = item['design_history'].copy()
    answer_hist = item['answer_history'].copy()
    answer_hist.extend([None] * (len(design_hist) - len(answer_hist)))

    # Store Output
    design_history = []
    answer_history = []


    for design, answer in zip(design_hist, answer_hist):

        if (design is not None) and (answer is not None) and (str(answer) in str_answers):

            design_history.append(design)
            answer_history.append(answer)

    return design_history, answer_history

import boto3
import openpyxl
import csv

id_column = 'profile_id' # Unique ID column for each profile
table_name = 'bace-db' # Update this if the name of the database TableName in template.yaml is changed
# Update `table_region` below to the region created with `sam deploy --guided`, saved in the SAM configuration file (samconfig.toml by default)
#   if different from the default region in ~/.aws/config (or C:\Users\USERNAME\.aws\config)
table_region = boto3.Session().region_name # example if different from default: table_region = 'us-east-2'
# os.environ['AWS_PROFILE'] = "YOUR_AWS_PROFILE_NAME" # Set this if your current AWS login profile is not the default one -- see profiles in ~/.aws/config (or C:\Users\USERNAME\.aws\config)

############################

# Start database connection
ddb = boto3.resource('dynamodb', region_name = table_region)
table = ddb.Table(table_name)

# Scan all data from DynamoDB table
response = table.scan()
db_items = response['Items']

# with open('new_profiles.csv', 'r', encoding='utf-8-sig') as file:
#     reader = csv.reader(file, delimiter='\n')
#     profiles_to_test = [row[0] for row in reader]

# Go beyond the 1mb limit: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Scan.html
while 'LastEvaluatedKey' in response:
    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    db_items.extend(response['Items'])

# db_items = [item for item in db_items if item['profile_id'] in profiles_to_test]

import scipy.stats
import numpy as np
output = []

for item in db_items:

    # Conver DynamoDB Decimal type to floats
    item = decimal_to_float(item)

    # Get cleaned design and answer histories.
    design_history, answer_history = clean_designs_and_answers(item, answers)
    ND = len(design_history)

    # Estimate preferences if the individual answered at least one question.
    if ND > 0:

        # try:

            #################################################################################
            ### Edit this block to update the method for calculating posterior estimates. ###
            #################################################################################

# Assuming pmc, answer_history, design_history, likelihood_pdf, size_thetas are already defined

        def compute_posterior_estimates():
            # upper = float(i) / 10

            theta_params = dict(
                WTP = scipy.stats.uniform(),
                p = scipy.stats.uniform()
            )

            # Compute posterior estimates using Population Monte Carlo
            posterior_thetas = pmc(
                theta_params,
                answer_history,
                design_history,
                likelihood_pdf,
                size_thetas
            )

            # # Calculate the mean and median posterior estimate for each parameter.
            # import matplotlib.pyplot as plt

            # # Plot posterior_thetas as a histogram
            # plt.hist(posterior_thetas, bins=10)
            # plt.xlabel('Parameter Value')
            # plt.ylabel('Frequency')
            # plt.title('Posterior Estimates')
            # plt.show()

            estimates = posterior_thetas.agg(['mean', 'median', 'std']).to_dict()
            # estimates = {key: value for key, value in estimates.items()}
            if 'p.median' in estimates and estimates['p.median'] < 0.5 :
                return estimates
            return None

                # Store output.
        # You can add additional variables associated with an item using item.get('var') to the exported csv.
        individual_output = {
            "profile_id": item.get("profile_id"),
            "n_designs": ND,
            "param": item.get("param"),
            **compute_posterior_estimates,
        }

        output.append(individual_output)


# Convert output to dataframe and write to .csv
output_df = pd.json_normalize(output)
output_df.to_csv(output_file, index=False)