"""
A/B Testing Campaign Analysis - Streamlit Dashboard
Main application entry point
"""
import streamlit as st
import pandas as pd
import sys
sys.path.insert(0, '../src')

from layout import DashboardLayout
from callbacks import DashboardCallbacks

def main():
    """Main application."""
    
    # Configure page
    DashboardLayout.setup_page_config()
    
    # Create navigation
    page = DashboardLayout.create_sidebar_navigation()
    
    # File uploader in sidebar
    uploaded_file = DashboardLayout.create_file_uploader()
    
    # Page routing
    if page == "Overview":
        show_overview_page(uploaded_file)
    elif page == "Data Analysis":
        show_data_analysis_page(uploaded_file)
    elif page == "Statistical Tests":
        show_statistical_tests_page(uploaded_file)
    elif page == "Segments":
        show_segments_page(uploaded_file)
    elif page == "Report":
        show_report_page(uploaded_file)

def show_overview_page(df: pd.DataFrame):
    """Show overview page."""
    st.title("📊 A/B Testing Campaign Analysis Dashboard")
    
    if df is None:
        DashboardLayout.create_overview_page()
        return
    
    # Validate data
    is_valid, message, df_clean = DashboardCallbacks.validate_and_load_data(df)
    
    if not is_valid:
        st.error(f"❌ {message}")
        return
    
    st.success(message)
    
    # Process data
    df_processed, process_info = DashboardCallbacks.process_data(df_clean)
    
    if 'error' in process_info:
        st.error(f"Processing error: {process_info['error']}")
        return
    
    # Calculate stats
    stats = DashboardCallbacks.calculate_descriptive_stats(df_processed)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Control Users", f"{stats['control']['n']:,}")
    with col2:
        st.metric("Treatment Users", f"{stats['treatment']['n']:,}")
    with col3:
        control_mean = stats['control']['mean']
        treatment_mean = stats['treatment']['mean']
        improvement = ((treatment_mean - control_mean) / control_mean * 100) if control_mean != 0 else 0
        st.metric("Improvement %", f"{improvement:.2f}%")
    with col4:
        st.metric("Total Users", f"{len(df_processed):,}")
    
    st.markdown("---")
    
    # SRM Check
    srm = process_info['srm_result']
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("✓ Data Quality")
        if srm['has_srm']:
            st.warning(f"⚠️ Sample Ratio Mismatch detected (p={srm['p_value']:.4f})")
        else:
            st.success("✓ No Sample Ratio Mismatch detected")
        
        st.write(f"Chi-square statistic: {srm['chi_square_stat']:.4f}")
        st.write(f"P-value: {srm['p_value']:.4f}")
    
    with col_right:
        st.subheader("📊 Distribution Summary")
        st.write(f"**Control Mean:** {stats['control']['mean']:.4f}")
        st.write(f"**Treatment Mean:** {stats['treatment']['mean']:.4f}")
        st.write(f"**Mean Difference:** {treatment_mean - control_mean:.4f}")

def show_data_analysis_page(df: pd.DataFrame):
    """Show data analysis page."""
    st.title("📋 Data Analysis")
    
    if df is None:
        DashboardLayout.create_data_analysis_page()
        return
    
    # Validate data
    is_valid, message, df_clean = DashboardCallbacks.validate_and_load_data(df)
    
    if not is_valid:
        st.error(f"❌ {message}")
        return
    
    st.success(message)
    
    # Process data
    df_processed, _ = DashboardCallbacks.process_data(df_clean)
    
    tab1, tab2, tab3 = st.tabs(["Data Quality", "Distributions", "Summary Stats"])
    
    with tab1:
        st.subheader("Data Quality Checks")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(df_processed))
        with col2:
            st.metric("Duplicates Removed", len(df) - len(df_processed))
        with col3:
            st.metric("Missing Values", df_processed.isnull().sum().sum())
    
    with tab2:
        st.subheader("Distribution Comparison")
        control_data = df_processed[df_processed['variant'] == 'control']['metric'].values
        treatment_data = df_processed[df_processed['variant'] == 'treatment']['metric'].values
        
        fig = DashboardCallbacks.Visualizations.distribution_plot(
            control_data, treatment_data,
            title="Control vs Treatment Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Summary Statistics")
        stats = DashboardCallbacks.calculate_descriptive_stats(df_processed)
        
        for variant in ['control', 'treatment']:
            st.write(f"**{variant.title()} Group:**")
            for key, value in stats[variant].items():
                st.write(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")

def show_statistical_tests_page(df: pd.DataFrame):
    """Show statistical tests page."""
    st.title("📊 Statistical Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Power Analysis Settings")
        metric_type = st.selectbox("Metric Type", ["Continuous", "Binary"])
        alpha = st.slider("Alpha (α)", 0.01, 0.10, 0.05)
        power = st.slider("Power (1-β)", 0.70, 0.99, 0.80)
        
        if metric_type == "Continuous":
            effect_size = st.slider("Effect Size (Cohen's d)", 0.1, 1.0, 0.2)
            if st.button("Calculate Sample Size"):
                result = DashboardCallbacks.calculate_power_analysis(
                    metric_type='continuous',
                    alpha=alpha,
                    power=power,
                    effect_size=effect_size
                )
                st.success(f"Required sample size per group: **{result['sample_size_per_group']:,}**")
        else:
            baseline = st.slider("Baseline Conversion", 0.01, 0.50, 0.10)
            expected = st.slider("Expected Conversion", 0.01, 0.50, 0.12)
            if st.button("Calculate Sample Size"):
                result = DashboardCallbacks.calculate_power_analysis(
                    metric_type='binary',
                    alpha=alpha,
                    power=power,
                    baseline_conversion=baseline,
                    expected_conversion=expected
                )
                st.success(f"Required sample size per group: **{result['sample_size_per_group']:,}**")
    
    with col2:
        st.subheader("Test Results")
        if df is None:
            st.info("Upload data to see test results")
            return
        
        # Validate data
        is_valid, message, df_clean = DashboardCallbacks.validate_and_load_data(df)
        if not is_valid:
            st.error(f"❌ {message}")
            return
        
        # Process data
        df_processed, _ = DashboardCallbacks.process_data(df_clean)
        
        # Perform tests
        test_results = DashboardCallbacks.perform_statistical_tests(df_processed, alpha=alpha)
        
        st.write("**T-Test Results:**")
        st.write(f"  T-Statistic: {test_results['ttest']['t_statistic']:.4f}")
        st.write(f"  P-Value: {test_results['ttest']['p_value']:.6f}")
        st.write(f"  Cohen's d: {test_results['cohens_d']:.4f}")
        st.write(f"  Interpretation: {test_results['interpretation']}")
        
        if test_results['ttest']['significant']:
            st.success("✅ Result is statistically significant")
        else:
            st.warning("⚠️ Result is not statistically significant")

def show_segments_page(df: pd.DataFrame):
    """Show segments page."""
    st.title("🔍 Segment Analysis")
    
    if df is None:
        DashboardLayout.create_segments_page()
        return
    
    # Validate data
    is_valid, message, df_clean = DashboardCallbacks.validate_and_load_data(df)
    if not is_valid:
        st.error(f"❌ {message}")
        return
    
    # Process data
    df_processed, _ = DashboardCallbacks.process_data(df_clean)
    
    st.subheader("Heterogeneous Treatment Effects")
    
    # Get available columns for segmentation
    segment_cols = [col for col in df_processed.columns 
                   if col not in ['metric', 'variant', 'timestamp', 'user_id']]
    
    if segment_cols:
        segment_col = st.selectbox("Segment By", segment_cols)
        
        # Perform segment analysis
        segment_results = DashboardCallbacks.segment_analysis(df_processed, segment_col)
        
        st.dataframe(segment_results, use_container_width=True)
    else:
        st.info("No segmentation columns found. Add demographic or device columns to data.")

def show_report_page(df: pd.DataFrame):
    """Show report page."""
    st.title("📄 Test Report & Recommendations")
    
    if df is None:
        DashboardLayout.create_report_page()
        return
    
    # Validate data
    is_valid, message, df_clean = DashboardCallbacks.validate_and_load_data(df)
    if not is_valid:
        st.error(f"❌ {message}")
        return
    
    # Process data
    df_processed, _ = DashboardCallbacks.process_data(df_clean)
    
    # Perform tests
    test_results = DashboardCallbacks.perform_statistical_tests(df_processed)
    
    # Generate recommendations
    recommendations = DashboardCallbacks.generate_recommendations(test_results, len(df_processed))
    
    st.subheader("Executive Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Statistical Summary")
        st.markdown(f"""
        - **Decision**: {recommendations['decision']}
        - **P-Value**: {recommendations['p_value']:.6f}
        - **Effect Size (Cohen's d)**: {recommendations['effect_size']:.4f}
        - **Mean Difference**: {recommendations['mean_difference']:.4f}
        - **Confidence Level**: 95%
        """)
    
    with col2:
        st.subheader("💡 Rationale")
        st.info(recommendations['rationale'])
    
    st.markdown("---")
    
    # Export options
    col_export = st.columns(3)
    with col_export[0]:
        if st.button("📥 Export Report (Excel)"):
            excel_file = DashboardCallbacks.export_results(
                df_processed, test_results, "ab_test_report.xlsx"
            )
            st.download_button(
                label="Download Excel",
                data=excel_file,
                file_name="ab_test_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col_export[1]:
        if st.button("📊 Export Data (CSV)"):
            csv = df_processed.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="ab_test_data.csv",
                mime="text/csv"
            )
    
    with col_export[2]:
        st.info("Email export coming soon")

# Run the app
if __name__ == "__main__":
    main()
