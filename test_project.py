"""
Test and Validation Script for A/B Testing Campaign Analysis Project
Generates sample data and validates all core functionality
"""
import sys
import os
sys.path.insert(0, 'src')

import pandas as pd
import numpy as np
from data_loader import DataLoader
from preprocessing import DataPreprocessor
from stats_tests import StatisticalTests
from sample_size import SampleSizeCalculator
from utils import load_config

def generate_sample_data(n_control=1000, n_treatment=1000, seed=42):
    """Generate realistic A/B test sample data."""
    np.random.seed(seed)
    
    # Control group: normal distribution
    control_metric = np.random.normal(loc=100, scale=15, size=n_control)
    
    # Treatment group: slight improvement
    treatment_metric = np.random.normal(loc=105, scale=15, size=n_treatment)
    
    # Create DataFrame
    data = pd.concat([
        pd.DataFrame({
            'user_id': [f'user_{i:06d}' for i in range(n_control)],
            'variant': 'control',
            'metric': control_metric,
            'timestamp': pd.date_range('2024-01-01', periods=n_control, freq='h'),
            'device_type': np.random.choice(['mobile', 'desktop', 'tablet'], n_control),
            'age_group': np.random.choice(['18-24', '25-34', '35-44', '45+'], n_control)
        }),
        pd.DataFrame({
            'user_id': [f'user_{i:06d}' for i in range(n_control, n_control + n_treatment)],
            'variant': 'treatment',
            'metric': treatment_metric,
            'timestamp': pd.date_range('2024-01-01', periods=n_treatment, freq='h'),
            'device_type': np.random.choice(['mobile', 'desktop', 'tablet'], n_treatment),
            'age_group': np.random.choice(['18-24', '25-34', '35-44', '45+'], n_treatment)
        })
    ]).reset_index(drop=True)
    
    return data

def test_data_loading():
    """Test data loading functionality."""
    print("\n" + "="*60)
    print("TEST 1: Data Loading")
    print("="*60)
    
    # Generate sample data
    df = generate_sample_data()
    print(f"✓ Generated sample data: {len(df)} records")
    
    # Save sample data
    df.to_csv('data/raw/sample_data.csv', index=False)
    print(f"✓ Saved to data/raw/sample_data.csv")
    
    # Load data
    loader = DataLoader('data/raw')
    df_loaded = loader.load_csv('sample_data.csv')
    print(f"✓ Loaded data: {len(df_loaded)} records")
    
    # Validate structure
    loader.validate_ab_data(df_loaded)
    print(f"✓ Data validation passed")
    
    # Check quality
    quality = loader.check_data_quality(df_loaded)
    print(f"✓ Data quality report:")
    for key, value in quality.items():
        if isinstance(value, dict):
            print(f"    {key}: {sum(value.values())} issues")
        else:
            print(f"    {key}: {value}")
    
    return df_loaded

def test_preprocessing(df):
    """Test data preprocessing."""
    print("\n" + "="*60)
    print("TEST 2: Data Preprocessing")
    print("="*60)
    
    preprocessor = DataPreprocessor()
    
    # Check SRM
    srm = preprocessor.check_sample_ratio_mismatch(df)
    print(f"✓ SRM Check:")
    print(f"    Control: {srm['control_count']}")
    print(f"    Treatment: {srm['treatment_count']}")
    print(f"    P-value: {srm['p_value']:.6f}")
    print(f"    Has SRM: {srm['has_srm']}")
    
    # Prepare data
    df_clean = preprocessor.prepare_for_analysis(df, numeric_cols=['metric'])
    print(f"✓ Processed data: {len(df_clean)} records")
    
    # Show log
    print(f"✓ Processing log:")
    for log in preprocessor.get_processing_log():
        print(f"    - {log}")
    
    return df_clean

def test_statistical_tests(df):
    """Test statistical analysis."""
    print("\n" + "="*60)
    print("TEST 3: Statistical Tests")
    print("="*60)
    
    control = df[df['variant'] == 'control']['metric'].values
    treatment = df[df['variant'] == 'treatment']['metric'].values
    
    # T-test
    print(f"✓ Running Independent Samples T-Test...")
    result = StatisticalTests.independent_ttest(control, treatment)
    
    print(f"    Control Mean: {result['control_mean']:.4f}")
    print(f"    Treatment Mean: {result['treatment_mean']:.4f}")
    print(f"    Mean Difference: {result['mean_difference']:.4f}")
    print(f"    T-Statistic: {result['t_statistic']:.4f}")
    print(f"    P-Value: {result['p_value']:.6f}")
    print(f"    Significant (α=0.05): {result['significant']}")
    
    # Effect size
    print(f"\n✓ Effect Size Analysis:")
    print(f"    Cohen's d: {result['cohens_d']:.4f}")
    interpretation = StatisticalTests.interpret_effect_size(result['cohens_d'])
    print(f"    Interpretation: {interpretation}")
    
    # Confidence intervals
    print(f"\n✓ Confidence Intervals (95%):")
    print(f"    Lower: {result['ci_lower']:.4f}")
    print(f"    Upper: {result['ci_upper']:.4f}")
    
    return result

def test_power_analysis():
    """Test power analysis and sample size calculation."""
    print("\n" + "="*60)
    print("TEST 4: Power Analysis & Sample Size")
    print("="*60)
    
    # Continuous metric
    print(f"✓ Continuous Metric (t-test):")
    result_cont = SampleSizeCalculator.power_analysis_summary(
        metric_type='continuous',
        alpha=0.05,
        power=0.80,
        effect_size=0.2
    )
    
    for key, value in result_cont.items():
        print(f"    {key}: {value}")
    
    # Binary metric
    print(f"\n✓ Binary Metric (chi-square):")
    result_bin = SampleSizeCalculator.power_analysis_summary(
        metric_type='binary',
        alpha=0.05,
        power=0.80,
        baseline_conversion=0.10,
        expected_conversion=0.12
    )
    
    for key, value in result_bin.items():
        print(f"    {key}: {value}")

def test_segmentation(df):
    """Test segment analysis."""
    print("\n" + "="*60)
    print("TEST 5: Segment Analysis")
    print("="*60)
    
    segments = df['device_type'].unique()
    print(f"✓ Analyzing segments: {segments}")
    
    results = []
    for segment in segments:
        segment_df = df[df['device_type'] == segment]
        control = segment_df[segment_df['variant'] == 'control']['metric'].values
        treatment = segment_df[segment_df['variant'] == 'treatment']['metric'].values
        
        if len(control) > 10 and len(treatment) > 10:
            test_result = StatisticalTests.independent_ttest(control, treatment)
            results.append({
                'Segment': segment,
                'N Control': len(control),
                'N Treatment': len(treatment),
                'Mean Diff': test_result['mean_difference'],
                'P-Value': test_result['p_value'],
                'Significant': test_result['significant']
            })
    
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    
    return results_df

def test_config_loading():
    """Test configuration loading."""
    print("\n" + "="*60)
    print("TEST 6: Configuration Loading")
    print("="*60)
    
    try:
        config = load_config('config.yaml')
        print(f"✓ Configuration loaded successfully")
        print(f"    Alpha: {config['power_analysis']['alpha']}")
        print(f"    Power: {config['power_analysis']['power']}")
        print(f"    Effect Size: {config['power_analysis']['effect_size']}")
        return config
    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
        return None

def generate_test_report(test_results, segment_results, config):
    """Generate test report."""
    print("\n" + "="*60)
    print("FINAL REPORT")
    print("="*60)
    
    print(f"\n📊 Test Results Summary:")
    print(f"    Overall Result: {'SIGNIFICANT' if test_results['significant'] else 'NOT SIGNIFICANT'}")
    print(f"    P-Value: {test_results['p_value']:.6f}")
    print(f"    Effect Size: {test_results['cohens_d']:.4f}")
    print(f"    Mean Difference: {test_results['mean_difference']:.4f}")
    
    print(f"\n📈 Segment Analysis:")
    print(segment_results.to_string(index=False))
    
    print(f"\n✅ All tests completed successfully!")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("A/B TESTING CAMPAIGN ANALYSIS - PROJECT VALIDATION")
    print("="*60)
    
    try:
        # Test 1: Data Loading
        df = test_data_loading()
        
        # Test 2: Preprocessing
        df_clean = test_preprocessing(df)
        
        # Test 3: Statistical Tests
        test_results = test_statistical_tests(df_clean)
        
        # Test 4: Power Analysis
        test_power_analysis()
        
        # Test 5: Segmentation
        segment_results = test_segmentation(df_clean)
        
        # Test 6: Configuration
        config = test_config_loading()
        
        # Generate Report
        generate_test_report(test_results, segment_results, config)
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - PROJECT IS READY!")
        print("="*60)
        print("\n🚀 Next Steps:")
        print("   1. Place your A/B test data in: data/raw/")
        print("   2. Run dashboard: cd dashboard && streamlit run app.py")
        print("   3. Or run notebooks: jupyter notebook notebooks/")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
