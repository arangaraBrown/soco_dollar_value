# Example configuration file
import scipy.stats
import numpy as np

author       = 'Ari Dev Rangarajan' # Your name here
size_thetas  = 2500                      # Size of sample drawn from prior distribution over preference parameters.
max_opt_time = 5                         # Stop Bayesian Optimization process after max_opt_time seconds and return best design.

# example constraint: Remove designs where pen A is Blue and pen B is Black (i.e., ensuring color_a <= color_b)
# to be added to `conf_dict` below
# Other Mango constraint examples: https://github.com/ARM-software/mango/blob/main/examples/Constrained%20Optimization.ipynb
# def constraint(params):
#     color_a = np.array([s['color_a'] for s in params])
#     color_b = np.array([s['color_b'] for s in params])

#     return (color_a <= color_b)

# Configuration Dictionary for Bayesian Optimization
# See https://github.com/ARM-software/mango#6-optional-configurations for details
# early_stopping is additionally set in design_optimization.py
# constraint can be added as in the example above
conf_dict = dict(
    domain_size    = 1500,
    initial_random = 1,
    num_iteration  = 40,
    # constraint     = constraint
)

answers = [0, 1]           # All possible answers that can be observed. Does not have to be binary.

# Preference parameters (theta_params)
# Dictionary where each preference parameter has a prior distribution specified by a scipy.stats distribution
# All entries must have a .rvs() and .log_pdf() method
# See https://docs.scipy.org/doc/scipy/reference/stats.html
theta_params = dict(
    WTP = scipy.stats.uniform(0,0.33),
    p = scipy.stats.uniform()
)

# Design parameters (design_params)
# Dictionary where each parameter specifies what designs can be chosen for a characteristic
# See https://github.com/ARM-software/mango#DomainSpace for details on specifying designs

design_params = dict(
    design_a   = ['Yes', 'No'],
    design_b    = ['Yes', 'No'],
)

# Specify likelihood function
# Returns Prob(answer | theta, design) for each answer in answers
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
