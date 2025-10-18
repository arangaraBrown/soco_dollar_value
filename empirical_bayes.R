library(data.table)
library(stringr)
library(deconvolveR)
library(statmod)
library(ggplot2)
library(haven)

set.seed(1)

main <- function(){
    dt <- as.data.table(read.csv('~/Desktop/bace/tools/dashboard/output.csv'))
    lb <- 0
    ub <- 1
    setnames(dt, c("WTP_logit.mean", "WTP_logit.std"),
             c("coef", "coef_sd"))
    dt[, zscore := coef / coef_sd]
    dt[, lcoef_sd := log(coef_sd)]
    dt[, wtp := exp(coef) -1]
    dt <- clean_data(dt,lb,ub)
    compute_and_save(dt,lb, ub)
}

compute_and_save <- function(dt, lb, ub, df = 15, tuning = 1) {
  # Define amenities list
  amenities <- c('Maternity policy and related benefits',
                 'Pension Fund',
                 'Health Insurance',
                 'Appointment Letter + Pay Slip',
                 'Safe Work Environment',
                 'Wages Paid via Bank Account')
  
  # 1. Process full dataset 
  process_group(dt, "all", "all", lb, ub, df, tuning)
  
  # 2. Process by individual amenities
  for (amenity in amenities) {
    cat("\nProcessing amenity:", amenity, "\n")
    process_group(dt[param == amenity], paste("all", amenity), amenity, lb, ub, df, tuning)
  }
  
  # 3. Process demographic breakdowns (each using full amenity set)
  
  # By gender
  process_group(dt[gender == "Male"], "Male", "all", lb, ub, df, tuning)
  process_group(dt[gender == "Female"], "Female", "all", lb, ub, df, tuning)
  
  # Male-only subgroups
  male_dt <- dt[gender == "Male"]
  
  # By employment status
  process_group(male_dt[employment_status == "Formal"], "Formal (male)", "all", lb, ub, df, tuning)
  process_group(male_dt[employment_status == "Informal"], "Informal (male)", "all", lb, ub, df, tuning)
  
  # By migration status
  process_group(male_dt[local_migrant == "local"], "Local (male)", "all", lb, ub, df, tuning)
  process_group(male_dt[local_migrant == "migrant"], "Migrant (male)", "all", lb, ub, df, tuning)
  
  # By wage type
  daily_dt <- male_dt[wage_type == "Daily"]
  monthly_dt <- male_dt[wage_type == "Monthly"]
  process_group(daily_dt, "Daily wage (male)", "all", lb, ub, df, tuning)
  process_group(monthly_dt, "Monthly wage (male)", "all", lb, ub, df, tuning)
  
  # By current_wage groups - Males, daily only
  
  # By current_wage groups - Males, daily only
  daily_dt <- male_dt[wage_type == "Daily"]
  
  # Using data.table syntax
  daily_with_rank <- copy(daily_dt)
  daily_with_rank[, current_wage_rank := frank(current_wage, ties.method = "first", na.last = "keep")]
  total_non_na <- sum(!is.na(daily_with_rank$current_wage))
  midpoint_rank <- floor(total_non_na / 2)
  
  # Process lower half - corrected condition to use data.table syntax
  process_group(daily_with_rank[current_wage_rank <= midpoint_rank], "Lower current_wage daily (male)", "all", lb, ub, df, tuning)
  # Process upper half - corrected condition to use > for upper group
  process_group(daily_with_rank[current_wage_rank > midpoint_rank], "Upper current_wage daily (male)", "all", lb, ub, df, tuning)
  
  # By current_wage groups - Males, monthly only
  monthly_dt <- male_dt[wage_type == "Monthly"]
  
  # Using data.table syntax
  monthly_with_rank <- copy(monthly_dt)
  monthly_with_rank[, current_wage_rank := frank(current_wage, ties.method = "first", na.last = "keep")]
  total_non_na <- sum(!is.na(monthly_with_rank$current_wage))
  midpoint_rank <- floor(total_non_na / 2)
  
  # Process lower half - corrected condition to use data.table syntax
  process_group(monthly_with_rank[current_wage_rank <= midpoint_rank], "Lower current_wage monthly (male, monthly)", "all", lb, ub, df, tuning)
  # Process upper half - corrected condition to use > for upper group
  process_group(monthly_with_rank[current_wage_rank > midpoint_rank], "Upper current_wage monthly (male, monthly)", "all", lb, ub, df, tuning)
  
  # By region
  maharashtra_wfcs <- c("Chakan", "Saki Naka", "Bhosari", "Navi Mumbai")
  process_group(male_dt[WFC %in% maharashtra_wfcs], "Maharashtra (male)", "all", lb, ub, df, tuning)
  
  gujarat_wfcs <- c("Vatva", "Savli", "Dahej", "Ahmedabad")
  process_group(male_dt[WFC %in% gujarat_wfcs], "Gujarat (male)", "all", lb, ub, df, tuning)
  
  # By industry groups
  manufacturing_industries <- c("Automotive", "Steel + Cement", "Pharmaceutical", 
                                "Chemical", "Garment")
  process_group(male_dt[industry %in% manufacturing_industries], "Manufacturing (male)", "all", lb, ub, df, tuning)
  process_group(male_dt[industry == "Construction"], "Construction (male)", "all", lb, ub, df, tuning)
  
  other_industries <- c("Power Generation", "Gig Worker", "Other")
  process_group(male_dt[industry %in% other_industries], "Other industries (male)", "all", lb, ub, df, tuning)
  
  # By age groups
  process_group(male_dt[age < 30], "Young (male)", "all", lb, ub, df, tuning)
  process_group(male_dt[age >= 30], "Old (male)", "all", lb, ub, df, tuning)
  
  # By having benefit
  process_group(male_dt[has_benefit == "Yes"], "Has Benefit", "all", lb, ub, df, tuning)
  process_group(male_dt[has_benefit == "No"], "Doesn't Have Benefit", "all", lb, ub, df, tuning)
  
}

# Helper function to process a data group
process_group <- function(group_dt, group_name, amenity_param, lb, ub, df, tuning) {
  cat(sprintf("\n%s sample size: %d\n", group_name, nrow(group_dt)))
  eb <- empirical_bayes(group_dt, lb, ub, df, tuning)
  
  # Extract group identifier from the name
  # Remove any text in parentheses and convert to lowercase
  group_id <- tolower(sub(" \\(.*\\)$", "", group_name))
  # For amenity-specific groups, extract the main group name
  group_id <- sub("all", "all", group_id)
  # Replace spaces with underscores
  group_id <- gsub(" ", "_", group_id)
  
  write_results(eb, group_id, amenity_param)
}

write_results <- function(eb, sample, amenity){
    eb_dist <- data.table(coef = eb$eb_dist$coef, density = eb$eb_dist$coef_dist)
    fwrite(eb_dist, paste0('/Users/ari_dev_rangarajan/Desktop/bace/tools/deconvolution/output/eb_dist_', amenity, '_', sample, '.csv'))
    fwrite(eb$post_dt, paste0('/Users/ari_dev_rangarajan/Desktop/bace/tools/deconvolution/output/posterior_mean_', amenity, '_', sample, '.csv'))

    ggsave(paste0('/Users/ari_dev_rangarajan/Desktop/bace/tools/deconvolution/output_local/eb_dist_', amenity, '_', sample, '.pdf'),
      plot = eb$p_eb_dist, width = 8, height = 4.5, unit = "in")
    ggsave(paste0('/Users/ari_dev_rangarajan/Desktop/bace/tools/deconvolution/output_local/posterior_mean_', amenity, '_', sample, '.pdf'),
      plot = eb$p_posterior_mean, width = 8, height = 4.5, unit = "in")
  }

empirical_bayes <- function(dt, lb, ub, df, tuning){

    # Prepare for numerical integration
    gq <- gauss.quad(100, kind = "legendre")

    # Density function of log(coef_sd)
    g_lns_density <- density(dt[, lcoef_sd], n = 512)

    # Deconvolution of zscore
    tau_zscore <- seq(0, dt[, max(zscore)], length.out = 1000)
    res_zscore <- deconv(
      tau = tau_zscore, X = dt$zscore,
      family = "Normal", pDegree = df, c0 = tuning
    )
    zscore_gdensity <- list()
    zscore_gdensity$x <- tau_zscore
    zscore_gdensity$y <- res_zscore$stats[, "g"] / (tau_zscore[2] - tau_zscore[1])

    eb_dist <- get_empirical_bayes_dist(gq, g_lns_density, zscore_gdensity, dt, 250)
    post_dt <- get_posterior_mean(gq, zscore_gdensity, dt)
    
    nbins <- 25
    binsize <- dt[, max(wtp) - min(wtp)] / nbins
    
    # Calculate prior mean
    prior_mean <- sum(eb_dist[wtp > 0, wtp * wtp_dist / sum(wtp_dist)])
    cat("Prior mean:", prior_mean, "\n")
    
    # Calculate standard deviation
    prior_sd <- sqrt(sum(eb_dist[wtp > 0, (wtp - prior_mean)^2 * wtp_dist / sum(wtp_dist)]))
    cat("Prior standard deviation:", prior_sd, "\n")
    
    # Calculate posterior mean
    post_mean <- sum(post_dt[wtp_eb > 0, wtp_eb]) / nrow(post_dt)
    cat("Posterior mean:", post_mean, "\n")
    
    # Calculate standard deviation
    post_sd <- sqrt(sum(post_dt[wtp_eb > 0, (wtp_eb - post_mean)^2]) / nrow(post_dt))
    cat("Posterior standard deviation:", post_sd, "\n")
    
    
    prior_log_mean <- sum(eb_dist[wtp > 0, log(wtp) * wtp_dist / sum(wtp_dist)])
    prior_log_sd <- sqrt(
      sum(eb_dist[wtp > 0, (log(wtp) - prior_log_mean)^2 * wtp_dist / sum(wtp_dist)])
    )

    p_eb_dist <- ggplot() +
      geom_histogram(data = dt, mapping = aes( x = wtp, y = ..count.. / binsize / sum(..count..) ),
                     color = "brown", bins = nbins, alpha = 0.2) +
      geom_line(data = eb_dist, mapping = aes(x = wtp, y = wtp_dist), color = "blue") +
      stat_function(fun = dlnorm, args = list(meanlog = prior_log_mean, sdlog = prior_log_sd),
                    colour = "red") +
      labs(x = expression(theta), y = "Density")
    
    p_posterior_mean <- ggplot(data = dt) +
      geom_histogram(mapping = aes(x = wtp, y = ..count.. / sum(..count..)),
                     color = "brown", bins = nbins, alpha = 0.2) +
      geom_histogram(mapping = aes(x = wtp_eb, y = ..count.. / sum(..count..)),
                     color = "blue", bins = nbins, alpha = 0.2)
    
    res <- list()
    res$eb_dist <- eb_dist
    res$post_dt <- post_dt[, .(profile_id, coef, coef_eb, coef_sd)]
    res$p_eb_dist <- p_eb_dist
    res$p_posterior_mean <- p_posterior_mean
    return(res)
}

get_empirical_bayes_dist <- function(gq, g_lns_density, zscore_gdensity, dt, numpoints) {
    min_t <- min(g_lns_density$x)
    max_t <- max(g_lns_density$x)

    quadrature <- get_quadrature(gq, min_t, max_t)

    g_lns_nodes <- approx(x = g_lns_density$x, y = g_lns_density$y, xout = quadrature$nodes)$y
    exp_mt <- exp(-quadrature$nodes)

    coefs <- seq(dt[, min(coef)], dt[, max(coef)], length.out = numpoints)
    coefs_dist <- rep(0, length(coefs))
    for (i in seq_along(coefs)) {
      g_mu_nodes <- approx(x = zscore_gdensity$x, y = zscore_gdensity$y, xout = coefs[i] * exp_mt)$y
      g_mu_nodes[is.na(g_mu_nodes)] <- 0
      coefs_dist[i] <- sum(quadrature$weights * exp_mt * g_mu_nodes * g_lns_nodes)
    }
    
    eb_dist <- data.table(coef = coefs, coef_dist = coefs_dist)
    eb_dist[, wtp := exp(coef)-1]
    eb_dist[, wtp_dist := coef_dist / exp(coef)]
      
    return(eb_dist)
}

get_posterior_mean <- function(gq, zscore_gdensity, dt) {
  dt <- get_posterior_mean_zscore(gq, zscore_gdensity, dt, "zscore", "coef_eb", "wtp_eb")
  
  return(dt)
}

get_posterior_mean_zscore <- function(gq, zscore_gdensity, dt, zscore_name, coef_eb_name, wtp_eb_name) {
  min_x <- dt[abs(get(zscore_name)) < 50, min(get(zscore_name))]
  max_x <- dt[abs(get(zscore_name)) < 50, max(get(zscore_name))]
  quadrature <- get_quadrature(gq, min_x, max_x)
  
  g_mu_nodes <- approx(x = zscore_gdensity$x, y = zscore_gdensity$y, xout = quadrature$nodes)$y
  g_mu_nodes[is.na(g_mu_nodes)] <- 0
  for (i in seq_along(dt$coef)) {
    phi <- dnorm(dt[i, get(zscore_name)] - quadrature$nodes)
    denominator_components <- phi * g_mu_nodes * quadrature$weights
    numerator_components <- denominator_components * quadrature$nodes
    dt[i, (coef_eb_name) := coef_sd * sum(numerator_components) / sum(denominator_components)]
  }
  
  dt[, (wtp_eb_name) := exp(get(coef_eb_name)) - 1]
  
  return(dt)
}

get_quadrature <- function(gq, a, b) {
    res <- list()
    res$nodes <- gq$nodes * (b - a) / 2 + (b + a) / 2
    res$weights <- gq$weights * (b - a) / 2

    return(res)
}

clean_data <- function(amenity_dt, lb, ub) {
    dt <- copy(amenity_dt)

    dt <- dt[coef > lb & coef < ub]
    dt <- dt[!is.na(zscore)]

    return(dt)
}

#################
### EXECUTE #####
#################

main()
