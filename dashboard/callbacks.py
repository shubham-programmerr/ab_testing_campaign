"""
Callbacks Module for Streamlit Dashboard
Handles data processing and analysis callbacks
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple
import sys
sys.path.insert(0, '../src')

from data_loader import DataLoader
from preprocessing import DataPreprocessor
from stats_tests import StatisticalTests
from sample_size import SampleSizeCalculator
from visualizations import Visualizations

class DashboardCallbacks:
    """Handle dashboard callbacks and data processing."""
    
    @staticmethod
    def validate_and_load_data(df: pd.DataFrame) -> Tuple[bool, str, pd.DataFrame]:
        """
        Validate uploaded data and return cleaned dataframe.
        
        Returns:
        --------
        tuple : (is_valid, message, cleaned_data)
        """
        try:
            # Check required columns
            required_cols = {'user_id', 'variant', 'metric', 'timestamp'}
            missing = required_cols - set(df.columns)
            if missing:
                return False, f"Missing columns: {missing}", None
            
            # Check valid variants
            valid_variants = {'control', 'treatment'}
            df_variants = set(df['variant'].unique())
            invalid = df_variants - valid_variants
            if invalid:
                return False, f"Invalid variants: {invalid}", None
            
            # Check data size
            if len(df) < 30:
                return False, "Insufficient data (minimum 30 records)", None
            
            return True, "✓ Data validated successfully", df
        
        except Exception as e:
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def process_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """
        Process and clean data.
        
        Returns:
        --------
        tuple : (cleaned_data, processing_log)
        """
        preprocessor = DataPreprocessor()
        
        try:
            # Basic cleaning
            df_clean = preprocessor.prepare_for_analysis(df)
            
            # SRM check
            srm_result = preprocessor.check_sample_ratio_mismatch(df_clean)
            
            return df_clean, {
                'processing_log': preprocessor.get_processing_log(),
                'srm_result': srm_result
            }
        
        except Exception as e:
            return None, {'error': str(e)}
    
    @staticmethod
    def calculate_descriptive_stats(df: pd.DataFrame) -> Dict:
        """Calculate descriptive statistics by variant."""
        stats_dict = {}
        
        for variant in ['control', 'treatment']:
            subset = df[df['variant'] == variant]['metric']
            stats_dict[variant] = {
                'n': len(subset),
                'mean': subset.mean(),
                'std': subset.std(),
                'min': subset.min(),
                'max': subset.max(),
                'median': subset.median(),
                'q25': subset.quantile(0.25),
                'q75': subset.quantile(0.75)
            }
        
        return stats_dict
    
    @staticmethod
    def perform_statistical_tests(df: pd.DataFrame, alpha: float = 0.05) -> Dict:
        """
        Perform statistical tests and return results.
        
        Returns:
        --------
        dict : Test results
        """
        control = df[df['variant'] == 'control']['metric'].values
        treatment = df[df['variant'] == 'treatment']['metric'].values
        
        # T-test
        ttest_result = StatisticalTests.independent_ttest(control, treatment, alpha=alpha)
        
        return {
            'ttest': ttest_result,
            'cohens_d': ttest_result['cohens_d'],
            'interpretation': StatisticalTests.interpret_effect_size(ttest_result['cohens_d'])
        }
    
    @staticmethod
    def calculate_power_analysis(
        metric_type: str = 'continuous',
        alpha: float = 0.05,
        power: float = 0.80,
        **kwargs
    ) -> Dict:
        """Calculate power analysis."""
        return SampleSizeCalculator.power_analysis_summary(
            metric_type=metric_type,
            alpha=alpha,
            power=power,
            **kwargs
        )
    
    @staticmethod
    def generate_recommendations(test_results: Dict, data_size: int) -> Dict:
        """
        Generate business recommendations based on test results.
        
        Returns:
        --------
        dict : Recommendations and rationale
        """
        p_value = test_results['ttest']['p_value']
        cohens_d = test_results['cohens_d']
        mean_diff = test_results['ttest']['mean_difference']
        
        # Decision logic
        if p_value < 0.05 and cohens_d > 0:
            decision = "✅ Deploy Treatment"
            rationale = "Statistically significant positive effect detected"
            color = "green"
        elif p_value < 0.05 and cohens_d < 0:
            decision = "❌ Stop & Revert"
            rationale = "Statistically significant negative effect detected"
            color = "red"
        elif 0.05 <= p_value < 0.10:
            decision = "⏳ Continue Monitoring"
            rationale = "Borderline significance - gather more data"
            color = "yellow"
        else:
            decision = "📊 Inconclusive"
            rationale = "No statistically significant difference detected"
            color = "gray"
        
        return {
            'decision': decision,
            'rationale': rationale,
            'color': color,
            'p_value': p_value,
            'effect_size': cohens_d,
            'mean_difference': mean_diff
        }
    
    @staticmethod
    def segment_analysis(
        df: pd.DataFrame,
        segment_col: str,
        alpha: float = 0.05
    ) -> pd.DataFrame:
        """
        Perform segment-level analysis.
        
        Returns:
        --------
        pd.DataFrame : Segment analysis results
        """
        segments = df[segment_col].unique()
        results = []
        
        for segment in segments:
            segment_df = df[df[segment_col] == segment]
            
            if len(segment_df) > 30:
                test_result = DashboardCallbacks.perform_statistical_tests(segment_df, alpha)
                
                results.append({
                    'segment': segment,
                    'n': len(segment_df),
                    'p_value': test_result['ttest']['p_value'],
                    'cohens_d': test_result['cohens_d'],
                    'significant': test_result['ttest']['significant'],
                    'mean_diff': test_result['ttest']['mean_difference']
                })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def export_results(df: pd.DataFrame, test_results: Dict, filename: str) -> bytes:
        """
        Export results to Excel.
        
        Returns:
        --------
        bytes : Excel file content
        """
        from io import BytesIO
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': ['Total Records', 'Control Count', 'Treatment Count', 'P-Value', "Cohen's d"],
                'Value': [
                    len(df),
                    len(df[df['variant'] == 'control']),
                    len(df[df['variant'] == 'treatment']),
                    test_results['ttest']['p_value'],
                    test_results['cohens_d']
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Raw data sheet
            df.to_excel(writer, sheet_name='Data', index=False)
        
        output.seek(0)
        return output.getvalue()
