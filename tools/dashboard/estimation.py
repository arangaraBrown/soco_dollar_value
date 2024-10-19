# Import database connection and pmc function
from app.database.db import table, decimal_to_float
from app.bace.pmc_inference import pmc
from app.bace.user_config import answers
from app.bace.user_config import theta_params, size_thetas, likelihood_pdf
import pandas as pd

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

import scipy.stats
import numpy as np

def post_estimate(db_items,upper):
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

            def compute_posterior_estimates(i):
                
                theta_params = dict(
                    WTP = scipy.stats.uniform(0, i),
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

                estimates = posterior_thetas.agg(['mean', 'median', 'std']).to_dict()
                return estimates

            # You can add additional variables associated with an item using item.get('var') to the exported csv.
            individual_output = {
                "profile_id": item.get("profile_id"),
                "n_designs": ND,
                "param": item.get("param"),
                **compute_posterior_estimates(upper),
            }

            output.append(individual_output)


    # Convert output to dataframe and write to .csv
    output_df = pd.json_normalize(output)
    return output_df