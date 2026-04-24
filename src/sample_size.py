"""
Sample Size Calculation Module for A/B Testing
Power analysis to determine optimal sample sizes
"""
import numpy as np
from scipy import stats
from typing import Dict, Tuple

class SampleSizeCalculator:
    """Calculate required sample sizes for A/B tests."""
    
    @staticmethod
    def calculate_two_sample_ttest(
        alpha: float = 0.05,
        beta: float = 0.20,
        effect_size: float = 0.2,
        ratio: float = 1.0
    ) -> int:
        """
        Calculate sample size for two-sample t-test.
        
        Parameters:
        -----------
        alpha : float
            Significance level (Type I error)
        beta : float
            Type II error rate (1 - power)
        effect_size : float
            Cohen's d (standardized effect size)
        ratio : float
            Ratio of control/treatment sample sizes
        
        Returns:
        --------
        int : Required sample size per group
        """
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(1 - beta)
        
        n = ((z_alpha + z_beta) ** 2 * (1 + 1/ratio)) / (effect_size ** 2)
        return int(np.ceil(n))
    
    @staticmethod
    def calculate_proportion_test(
        p1: float,
        p2: float,
        alpha: float = 0.05,
        beta: float = 0.20,
        ratio: float = 1.0
    ) -> int:
        """
        Calculate sample size for proportion test (chi-square).
        
        Parameters:
        -----------
        p1 : float
            Baseline conversion rate (0-1)
        p2 : float
            Expected conversion rate in treatment group
        alpha : float
            Significance level
        beta : float
            Type II error rate
        ratio : float
            Ratio of control/treatment sample sizes
        
        Returns:
        --------
        int : Required sample size per group
        """
        p_bar = (p1 + p2) / 2
        
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(1 - beta)
        
        p_diff = p2 - p1
        
        n = ((z_alpha + z_beta) ** 2 * (p_bar * (1 - p_bar) * (1 + 1/ratio))) / (p_diff ** 2)
        return int(np.ceil(n))
    
    @staticmethod
    def calculate_effect_size_cohens_d(
        baseline_mean: float,
        treatment_mean: float,
        pooled_std: float
    ) -> float:
        """Calculate Cohen's d effect size."""
        if pooled_std == 0:
            return 0
        return (treatment_mean - baseline_mean) / pooled_std
    
    @staticmethod
    def calculate_effect_size_proportion(
        p1: float,
        p2: float
    ) -> float:
        """
        Calculate effect size for proportions (odds ratio).
        
        Returns:
        --------
        float : Log-odds ratio
        """
        if p1 == 0 or p1 == 1 or p2 == 0 or p2 == 1:
            return 0
        
        odds1 = p1 / (1 - p1)
        odds2 = p2 / (1 - p2)
        
        return np.log(odds2 / odds1)
    
    @staticmethod
    def power_analysis_summary(
        metric_type: str = 'continuous',
        alpha: float = 0.05,
        power: float = 0.80,
        **kwargs
    ) -> Dict:
        """
        Provide comprehensive power analysis summary.
        
        Parameters:
        -----------
        metric_type : str
            'continuous' or 'binary'
        alpha : float
            Significance level
        power : float
            Statistical power
        **kwargs : dict
            Additional parameters based on metric type
        
        Returns:
        --------
        dict : Power analysis results
        """
        beta = 1 - power
        
        if metric_type == 'continuous':
            effect_size = kwargs.get('effect_size', 0.2)
            n = SampleSizeCalculator.calculate_two_sample_ttest(
                alpha=alpha, beta=beta, effect_size=effect_size
            )
            return {
                'metric_type': metric_type,
                'alpha': alpha,
                'power': power,
                'effect_size': effect_size,
                'sample_size_per_group': n,
                'total_sample_size': n * 2,
                'test_type': 't-test'
            }
        
        elif metric_type == 'binary':
            p1 = kwargs.get('baseline_conversion', 0.1)
            p2 = kwargs.get('expected_conversion', 0.12)
            n = SampleSizeCalculator.calculate_proportion_test(
                p1=p1, p2=p2, alpha=alpha, beta=beta
            )
            return {
                'metric_type': metric_type,
                'alpha': alpha,
                'power': power,
                'baseline_conversion': p1,
                'expected_conversion': p2,
                'sample_size_per_group': n,
                'total_sample_size': n * 2,
                'test_type': 'chi-square'
            }
