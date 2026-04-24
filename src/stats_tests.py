"""
Statistical Tests Module for A/B Testing Campaign Analysis
Implements t-tests, chi-square tests, proportion tests, and effect size calculations
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple

class StatisticalTests:
    """Perform statistical tests for A/B testing."""
    
    @staticmethod
    def independent_ttest(
        control: np.ndarray,
        treatment: np.ndarray,
        alpha: float = 0.05
    ) -> Dict:
        """
        Perform independent samples t-test.
        
        Returns:
        --------
        dict : Test results including t-statistic, p-value, significance
        """
        t_stat, p_value = stats.ttest_ind(control, treatment)
        
        control_mean = np.mean(control)
        treatment_mean = np.mean(treatment)
        pooled_std = np.sqrt((np.var(control) + np.var(treatment)) / 2)
        cohens_d = (treatment_mean - control_mean) / pooled_std if pooled_std > 0 else 0
        
        # Confidence intervals
        se = pooled_std * np.sqrt(2 / len(control))
        ci_lower = (treatment_mean - control_mean) - 1.96 * se
        ci_upper = (treatment_mean - control_mean) + 1.96 * se
        
        return {
            'test_type': 't-test',
            'control_mean': control_mean,
            'treatment_mean': treatment_mean,
            'mean_difference': treatment_mean - control_mean,
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < alpha,
            'cohens_d': cohens_d,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'alpha': alpha
        }
    
    @staticmethod
    def chi_square_test(
        contingency_table: pd.DataFrame,
        alpha: float = 0.05
    ) -> Dict:
        """
        Perform chi-square test of independence.
        
        Parameters:
        -----------
        contingency_table : pd.DataFrame
            2x2 contingency table (rows: variants, cols: outcomes)
        
        Returns:
        --------
        dict : Test results
        """
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        # Cramér's V effect size
        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
        
        return {
            'test_type': 'chi-square',
            'chi_square_statistic': chi2,
            'p_value': p_value,
            'degrees_of_freedom': dof,
            'significant': p_value < alpha,
            'cramers_v': cramers_v,
            'alpha': alpha
        }
    
    @staticmethod
    def proportion_test(
        successes_control: int,
        n_control: int,
        successes_treatment: int,
        n_treatment: int,
        alpha: float = 0.05
    ) -> Dict:
        """
        Perform two-proportion z-test.
        
        Returns:
        --------
        dict : Test results
        """
        p1 = successes_control / n_control
        p2 = successes_treatment / n_treatment
        
        # Pooled proportion for standard error
        p_pool = (successes_control + successes_treatment) / (n_control + n_treatment)
        se = np.sqrt(p_pool * (1 - p_pool) * (1/n_control + 1/n_treatment))
        
        z_stat = (p2 - p1) / se if se > 0 else 0
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        
        # Confidence interval
        ci_lower = (p2 - p1) - 1.96 * se
        ci_upper = (p2 - p1) + 1.96 * se
        
        return {
            'test_type': 'proportion-test',
            'control_proportion': p1,
            'treatment_proportion': p2,
            'proportion_difference': p2 - p1,
            'z_statistic': z_stat,
            'p_value': p_value,
            'significant': p_value < alpha,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'alpha': alpha
        }
    
    @staticmethod
    def cohens_d(
        group1: np.ndarray,
        group2: np.ndarray
    ) -> float:
        """Calculate Cohen's d effect size."""
        n1, n2 = len(group1), len(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0
        
        return (np.mean(group2) - np.mean(group1)) / pooled_std
    
    @staticmethod
    def interpret_effect_size(cohens_d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            return "Negligible"
        elif abs_d < 0.5:
            return "Small"
        elif abs_d < 0.8:
            return "Medium"
        else:
            return "Large"
    
    @staticmethod
    def confidence_interval_continuous(
        mean: float,
        std: float,
        n: int,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate confidence interval for continuous variable."""
        z = stats.norm.ppf((1 + confidence) / 2)
        se = std / np.sqrt(n)
        return (mean - z * se, mean + z * se)
    
    @staticmethod
    def confidence_interval_proportion(
        successes: int,
        n: int,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate confidence interval for proportion (Wilson score)."""
        z = stats.norm.ppf((1 + confidence) / 2)
        p = successes / n
        
        denominator = 1 + z**2 / n
        centre = (p + z**2 / (2*n)) / denominator
        spread = z * np.sqrt(p * (1 - p) / n + z**2 / (4*n**2)) / denominator
        
        return (centre - spread, centre + spread)
