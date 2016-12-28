from collections import namedtuple

import numpy as np
from scipy import stats
import statsmodels.api as sm

from latexify import latexify, fig_size, savefig
import matplotlib.pyplot as plt


Beta = namedtuple("Beta", "a b")


def binomial_bayes_factor(theta, prior, posterior, plot=False):
    p_posterior = stats.beta.pdf(theta, *posterior)
    p_prior = stats.beta.pdf(theta, *prior)
    
    if plot:
        plt.plot(theta, p_prior, "o", c="grey")
        plt.plot(theta, p_posterior, "ko")
        plt.vlines(theta, p_prior, p_posterior, linestyles="--", lw=1)
        
    return p_posterior / p_prior


def binomial_factor_posterior(n_successes, n_studies, prior: Beta,
                              theta_0=None, theta_1=None,
                              alpha=0.95, y_max=None):    
    likelihood = Beta(n_successes + 1, n_studies - n_successes + 1)
    posterior = Beta(prior.a + likelihood.a - 1, prior.b + likelihood.b - 1)
    theta = np.linspace(0, 1, 100)

    prior_curve = stats.beta.pdf(theta, prior.a, prior.b)
    likelihood_curve = stats.beta.pdf(theta, likelihood.a, likelihood.b)
    posterior_curve = stats.beta.pdf(theta, posterior.a, posterior.b)

    plt.plot(theta, prior_curve, "grey", lw=3, label="prior")
    plt.plot(theta, posterior_curve, "k", lw=3, label="posterior")
    plt.plot(theta, likelihood_curve, "C0--", lw=3, label="likelihood")
    plt.legend()

    plt.xlabel(r"$\theta$")
    plt.ylabel("Density")
    
    mean = posterior.a / (posterior.a + posterior.b)
    
    if theta_0 is None:
        theta_0 = mean
    
    bf_0 = binomial_bayes_factor(theta_0, prior, posterior, plot=True)
    bf_1 = 1 if theta_1 is None else binomial_bayes_factor(theta_1,  prior, posterior, plot=True)
     
    if y_max is None:
        y_max = max(max(posterior_curve), max(likelihood_curve)) * 1.05
    y_min = -y_max * 0.05
    plt.ylim(y_min, y_max)
    
    plt.vlines(mean, y_min, y_max, lw=1)
    
    lower, upper = stats.beta.interval(alpha, posterior.a, posterior.b)
    plt.vlines(lower, y_min, y_max, lw=1, linestyles="--", color="grey")
    plt.vlines(upper, y_min, y_max, lw=1, linestyles="--", color="grey")
    plt.fill_between(theta[theta < lower], posterior_curve[theta < lower], color="lightgrey")
    plt.fill_between(theta[theta > upper], posterior_curve[theta > upper], color="lightgrey")
    
    if theta_0 is None:
        theta_0 = mean
    title_string_t = "Mean posterior: {mean:.5}, 95% CI: ({lower:.2}, {upper:.2})\nBF({theta_0:.2}): {bf_0:.2f}"
    if theta_1 is not None:
        title_string_t += ("; BF({theta_1:.2}): {bf_1:.2f}\n"
                           "L({theta_0:.2}:{theta_1:.2}): {lh01:.2f}; L({theta_1:.2}:{theta_0:.2}): {lh10:.2f}")
    title_string = title_string_t.format(mean=mean, lower=lower, upper=upper, theta_0=theta_0, bf_0=bf_0,
                                         theta_1=theta_1, bf_1=bf_1, lh01=bf_0/bf_1, lh10=bf_1/bf_0)
    plt.title(title_string)


if __name__ == "__main__":
    latexify()
    plt.figure(figsize=fig_size())
    binomial_factor_posterior(20, 30, Beta(0.5, 0.5), theta_1=0.5)
    savefig("binomial_factor_posterior")
