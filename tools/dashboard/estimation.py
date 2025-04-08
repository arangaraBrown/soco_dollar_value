# Import database connection and pmc function
from app.database.db import table, decimal_to_float
from app.bace.pmc_inference import pmc
from app.bace.user_config import answers
from app.bace.user_config import theta_params, size_thetas
import pandas as pd
import scipy.stats as st
import numpy as np


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

        def la_likelihood_pdf(answer, thetas,
                   # All keys in design_params here
                   wage_a, wage_b,
                   design_a, design_b,
                   ):
            
            # loss aversion utility model
            def utility(current_wage, design_wage, design_amenity):
                if (design_wage >= current_wage):
                    u = np.log(design_wage) + thetas['WTP_la'] * (design_amenity == "Yes")
                else:
                    u  = np.log(current_wage) - np.log(current_wage - design_wage)*thetas['alpha_la'] + thetas['WTP_la'] * (design_amenity == "Yes")
                return u
            
            current_wage = float(item['wage'])
            base_U_a = utility(current_wage,wage_a,design_a)
            base_U_b = utility(current_wage,wage_b,design_b)
            
            base_utility_diff = base_U_b - base_U_a

            # Logit likelihood of choosing B over A with scale parameter thetas['mu']
            # likelihood = 1 / (1 + np.exp(-1 * thetas['mu'] * base_utility_diff))

            # eps = 1e-10
            # likelihood[likelihood < eps] = eps
            # likelihood[likelihood > (1 - eps)] = 1 - eps

            # Binomial Likelihood from paper
            likelihood = (1-thetas['p_la'])*(base_utility_diff>0) + thetas['p_la']/2

            # Produce a likelihood associated with each possible answer choice
            # (account for the fact that answer inputs through the API may be in string format)
            if str(answer) == '1':
                # choose B
                return likelihood
            else:
                # choose A
                return 1 - likelihood
            
        def likelihood_pdf(answer, thetas,
                   # All keys in design_params here
                   wage_a, wage_b,
                   design_a, design_b,
                   ):
            
            base_U_a = np.log(wage_a) + thetas['WTP'] * (design_a == "Yes")
            base_U_b = np.log(wage_b) + thetas['WTP'] * (design_b == "Yes")
            
            base_utility_diff = base_U_b - base_U_a

            # Logit likelihood of choosing B over A with scale parameter thetas['mu']
            # likelihood = 1 / (1 + np.exp(-1 * thetas['mu'] * base_utility_diff))

            # eps = 1e-10
            # likelihood[likelihood < eps] = eps
            # likelihood[likelihood > (1 - eps)] = 1 - eps

            # Binomial Likelihood from paper
            likelihood = (1-thetas['p'])*(base_utility_diff>0) + thetas['p']/2

            # Produce a likelihood associated with each possible answer choice
            # (account for the fact that answer inputs through the API may be in string format)
            if str(answer) == '1':
                # choose B
                return likelihood
            else:
                # choose A
                return 1 - likelihood


        # Estimate preferences if the individual answered at least one question.
        if ND > 0:

            # try:

                #################################################################################
                ### Edit this block to update the method for calculating posterior estimates. ###
                #################################################################################

    # Assuming pmc, answer_history, design_history, likelihood_pdf, size_thetas are already defined

            def compute_posterior_estimates(i,la):
                if la:
                    theta_params = dict(
                        WTP_la = scipy.stats.uniform(0, i),
                        alpha_la = scipy.stats.uniform(0,2),
                        p_la = scipy.stats.uniform()
                    )

                    # Compute posterior estimates using Population Monte Carlo
                    posterior_thetas = pmc(
                        theta_params,
                        answer_history,
                        design_history,
                        la_likelihood_pdf,
                        size_thetas
                    )
                else:
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
                if la:
                    estimates = posterior_thetas[['WTP_la','p_la','alpha_la']].agg(['mean','std']).to_dict()
                else:
                    estimates = posterior_thetas[['WTP','p',]].agg(['mean','std']).to_dict()
                return estimates

            # You can add additional variables associated with an item using item.get('var') to the exported csv.
            individual_output = {
                "profile_id": item.get("profile_id"),
                "n_designs": ND,
                "param": item.get("param"),
                **compute_posterior_estimates(upper,False),
                **compute_posterior_estimates(upper,True),
            }

            output.append(individual_output)


    # Convert output to dataframe and write to .csv
    output_df = pd.json_normalize(output)
    return output_df