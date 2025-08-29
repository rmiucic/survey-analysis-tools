import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from collections import Counter
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
from scipy.stats import chi2_contingency, fisher_exact
import seaborn as sns

# Page configuration
st.set_page_config(
    page_title="Maternity Survey Analyzer", 
    page_icon="🤱", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px;
        font-weight: 600;
    }
    .highlight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


class MaternityAnalyzer:
    def __init__(self, df):
        self.df = df
        self.key_questions = self._identify_key_questions()
    
    def _identify_key_questions(self):
        """Identify key question columns for analysis"""
        questions = {}
        
        # Education
        education_cols = [col for col in self.df.columns if 'obrazovan' in col.lower()]
        questions['education'] = education_cols[0] if education_cols else None
        
        # Birth satisfaction
        satisfaction_cols = [col for col in self.df.columns if 'iskustvo porođaja' in col.lower() and 'oceni' in col.lower()]
        questions['birth_satisfaction'] = satisfaction_cols[0] if satisfaction_cols else None
        
        # Mental health indicators
        questions['anxiety_during_birth'] = None
        questions['postpartum_depression'] = None
        questions['mental_health_support'] = None
        
        for col in self.df.columns:
            if 'anksioznosti, straha' in col.lower() and 'porođaj' in col.lower():
                questions['anxiety_during_birth'] = col
            elif 'postporođajne depresije' in col.lower() and 'simptome' in col.lower():
                questions['postpartum_depression'] = col
            elif 'emocijama i teškoćama' in col.lower() and 'sa kim' in col.lower():
                questions['mental_health_support'] = col
        
        # Desire for more children
        future_children_cols = [col for col in self.df.columns if 'još dece' in col.lower() and 'odluk' in col.lower()]
        questions['future_children_desire'] = future_children_cols[0] if future_children_cols else None
        
        # Support system
        partner_support_cols = [col for col in self.df.columns if 'partner razume' in col.lower()]
        questions['partner_support'] = partner_support_cols[0] if partner_support_cols else None
        
        return questions
    
    def analyze_education_vs_satisfaction(self):
        """Analyze relationship between education and birth satisfaction"""
        if not self.key_questions['education'] or not self.key_questions['birth_satisfaction']:
            return None
        
        edu_col = self.key_questions['education']
        sat_col = self.key_questions['birth_satisfaction']
        
        # Create crosstab
        cross_tab = pd.crosstab(self.df[edu_col], self.df[sat_col], margins=True)
        cross_tab_pct = pd.crosstab(self.df[edu_col], self.df[sat_col], normalize='index') * 100
        
        # Create visualization
        fig = px.imshow(
            cross_tab_pct.values[:-1, :-1],  # Remove margins
            x=cross_tab_pct.columns[:-1],
            y=cross_tab_pct.index[:-1],
            color_continuous_scale="RdYlBu_r",
            title="Education Level vs Birth Satisfaction (% within education group)",
            labels=dict(color="Percentage")
        )
        fig.update_layout(height=500)
        
        # Calculate statistics
        chi2, p_value, dof, expected = chi2_contingency(cross_tab.iloc[:-1, :-1])
        
        return {
            'figure': fig,
            'crosstab': cross_tab,
            'chi2': chi2,
            'p_value': p_value,
            'interpretation': self._interpret_p_value(p_value)
        }
    
    def analyze_mental_health_vs_future_children(self):
        """Analyze relationship between mental health and desire for more children"""
        if not self.key_questions['postpartum_depression'] or not self.key_questions['future_children_desire']:
            return None
        
        mh_col = self.key_questions['postpartum_depression']
        fc_col = self.key_questions['future_children_desire']
        
        # Clean and prepare data
        df_clean = self.df[[mh_col, fc_col]].dropna()
        
        if len(df_clean) < 10:
            return None
        
        # Create stacked bar chart
        cross_tab = pd.crosstab(df_clean[mh_col], df_clean[fc_col])
        cross_tab_pct = pd.crosstab(df_clean[mh_col], df_clean[fc_col], normalize='index') * 100
        
        fig = go.Figure()
        
        for col in cross_tab_pct.columns:
            fig.add_trace(go.Bar(
                name=col,
                x=cross_tab_pct.index,
                y=cross_tab_pct[col],
                text=[f'{val:.1f}%' for val in cross_tab_pct[col]],
                textposition='inside'
            ))
        
        fig.update_layout(
            title="Postpartum Depression vs Desire for More Children",
            xaxis_title="Postpartum Depression Symptoms",
            yaxis_title="Percentage",
            barmode='stack',
            height=500
        )
        
        # Calculate statistics
        if cross_tab.shape[0] > 1 and cross_tab.shape[1] > 1:
            chi2, p_value, dof, expected = chi2_contingency(cross_tab)
        else:
            chi2, p_value = None, None
        
        return {
            'figure': fig,
            'crosstab': cross_tab,
            'chi2': chi2,
            'p_value': p_value,
            'interpretation': self._interpret_p_value(p_value) if p_value else "Insufficient data for statistical analysis"
        }
    
    def analyze_support_vs_mental_health(self):
        """Analyze relationship between support systems and mental health"""
        if not self.key_questions['partner_support'] or not self.key_questions['anxiety_during_birth']:
            return None
        
        support_col = self.key_questions['partner_support']
        anxiety_col = self.key_questions['anxiety_during_birth']
        
        # Clean data
        df_clean = self.df[[support_col, anxiety_col]].dropna()
        
        if len(df_clean) < 10:
            return None
        
        # Create visualization
        cross_tab = pd.crosstab(df_clean[support_col], df_clean[anxiety_col])
        cross_tab_pct = pd.crosstab(df_clean[support_col], df_clean[anxiety_col], normalize='index') * 100
        
        fig = go.Figure()
        
        for col in cross_tab_pct.columns:
            fig.add_trace(go.Bar(
                name=col,
                x=cross_tab_pct.index,
                y=cross_tab_pct[col],
                text=[f'{val:.1f}%' for val in cross_tab_pct[col]],
                textposition='inside'
            ))
        
        fig.update_layout(
            title="Partner Support vs Anxiety During Birth",
            xaxis_title="Partner Support Level",
            yaxis_title="Percentage",
            barmode='group',
            height=500
        )
        
        # Statistics
        chi2, p_value, dof, expected = chi2_contingency(cross_tab)
        
        return {
            'figure': fig,
            'crosstab': cross_tab,
            'chi2': chi2,
            'p_value': p_value,
            'interpretation': self._interpret_p_value(p_value)
        }
    
    def _interpret_p_value(self, p_value):
        """Interpret statistical significance"""
        if p_value is None:
            return "Cannot calculate statistical significance"
        elif p_value < 0.001:
            return "Very strong statistical relationship (p < 0.001)"
        elif p_value < 0.01:
            return "Strong statistical relationship (p < 0.01)"
        elif p_value < 0.05:
            return "Statistically significant relationship (p < 0.05)"
        elif p_value < 0.1:
            return "Marginally significant trend (p < 0.1)"
        else:
            return "No significant statistical relationship found"
    
    def create_comprehensive_mental_health_analysis(self):
        """Create comprehensive mental health dashboard"""
        charts = []
        
        # Mental health questions analysis
        mh_questions = [
            self.key_questions['anxiety_during_birth'],
            self.key_questions['postpartum_depression'],
            self.key_questions['mental_health_support']
        ]
        
        for i, question in enumerate(mh_questions):
            if question and question in self.df.columns:
                values = self.df[question].value_counts()
                
                fig = px.pie(
                    values=values.values,
                    names=values.index,
                    title=f"Mental Health Indicator {i+1}: {question[:50]}..."
                )
                charts.append(fig)
        
        return charts
    
    def create_demographics_analysis(self):
        """Enhanced demographics with correlations"""
        charts = []
        
        # Basic demographics
        demo_cols = self.df.columns[1:5]  # First few columns are usually demographics
        
        for col in demo_cols:
            if self.df[col].nunique() < 20:  # Only categorical data
                values = self.df[col].value_counts()
                
                fig = px.bar(
                    x=values.index,
                    y=values.values,
                    title=f"Distribution: {col}",
                    labels={'x': col, 'y': 'Count'}
                )
                fig.update_layout(xaxis_tickangle=45)
                charts.append(fig)
        
        return charts


def main():
    st.title("🤱 Maternity Survey Deep Analysis")
    st.markdown("**Exploring relationships between education, mental health, support systems, and birth experiences**")
    
    # Sidebar
    st.sidebar.header("📁 Upload Survey Data")
    uploaded_file = st.sidebar.file_uploader(
        "Choose survey data file", 
        type=['xlsx', 'xls', 'csv'],
        help="Upload your maternity survey data (Excel or CSV format)"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            with st.spinner("Loading data..."):
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                else:
                    df = pd.read_excel(uploaded_file)
            
            analyzer = MaternityAnalyzer(df)
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 Participants", len(df))
            with col2:
                st.metric("❓ Questions", len(df.columns) - 1)
            with col3:
                valid_responses = df.notna().sum().sum()
                total_possible = len(df) * (len(df.columns) - 1)
                completion_rate = (valid_responses / total_possible) * 100
                st.metric("✅ Completion Rate", f"{completion_rate:.1f}%")
            with col4:
                text_responses = sum(1 for col in df.columns if df[col].nunique() > 50)
                st.metric("📝 Open Questions", text_responses)
            
            # Main analysis tabs
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "🎓 Education & Satisfaction", 
                "🧠 Mental Health & Decisions",
                "🤝 Support Systems",
                "📊 Key Relationships",
                "📍 Demographics", 
                "💭 Insights"
            ])
            
            with tab1:
                st.header("🎓 Education Level vs Birth Satisfaction")
                
                analysis = analyzer.analyze_education_vs_satisfaction()
                if analysis:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.plotly_chart(analysis['figure'], use_container_width=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="highlight-box">
                        <h4>📈 Statistical Results</h4>
                        <p><strong>Chi-square:</strong> {analysis['chi2']:.3f}</p>
                        <p><strong>P-value:</strong> {analysis['p_value']:.4f}</p>
                        <p><strong>Interpretation:</strong> {analysis['interpretation']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Show detailed breakdown
                    st.subheader("📋 Detailed Breakdown")
                    st.dataframe(analysis['crosstab'], use_container_width=True)
                else:
                    st.warning("Cannot perform this analysis - missing required questions")
            
            with tab2:
                st.header("🧠 Mental Health vs Future Family Planning")
                
                analysis = analyzer.analyze_mental_health_vs_future_children()
                if analysis:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.plotly_chart(analysis['figure'], use_container_width=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="highlight-box">
                        <h4>🔍 Analysis Results</h4>
                        <p><strong>Relationship:</strong> {analysis['interpretation']}</p>
                        {f'<p><strong>P-value:</strong> {analysis["p_value"]:.4f}</p>' if analysis['p_value'] else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.subheader("🧮 Cross-tabulation")
                    st.dataframe(analysis['crosstab'], use_container_width=True)
                    
                    # Key insights
                    st.subheader("💡 Key Insights")
                    if analysis['crosstab'] is not None:
                        total_with_depression = analysis['crosstab'].sum(axis=1)
                        for idx in total_with_depression.index:
                            pct_wanting_more = (analysis['crosstab'].loc[idx, :] / total_with_depression[idx] * 100).round(1)
                            st.write(f"**{idx}:** Distribution across future children desire")
                else:
                    st.warning("Cannot perform this analysis - missing required questions")
            
            with tab3:
                st.header("🤝 Support Systems & Mental Health")
                
                analysis = analyzer.analyze_support_vs_mental_health()
                if analysis:
                    st.plotly_chart(analysis['figure'], use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        **Statistical Significance:** {analysis['interpretation']}
                        
                        **P-value:** {analysis['p_value']:.4f}
                        """)
                    
                    with col2:
                        st.subheader("Cross-tabulation")
                        st.dataframe(analysis['crosstab'])
                else:
                    st.warning("Cannot perform this analysis - missing required questions")
            
            with tab4:
                st.header("📊 Key Relationship Matrix")
                
                # Create correlation-style analysis for multiple relationships
                st.subheader("🔗 Multiple Variable Relationships")
                
                # Available variables for analysis
                available_vars = [q for q in analyzer.key_questions.values() if q and q in df.columns]
                
                if len(available_vars) >= 2:
                    col1, col2 = st.columns(2)
                    with col1:
                        var1 = st.selectbox("Select first variable:", available_vars, key="rel1")
                    with col2:
                        var2 = st.selectbox("Select second variable:", available_vars, key="rel2")
                    
                    if st.button("🔍 Analyze Relationship"):
                        if var1 != var2:
                            # Create cross-tabulation
                            cross_tab = pd.crosstab(df[var1], df[var2])
                            cross_tab_pct = pd.crosstab(df[var1], df[var2], normalize='index') * 100
                            
                            # Visualization
                            fig = px.imshow(
                                cross_tab_pct.values,
                                x=cross_tab_pct.columns,
                                y=cross_tab_pct.index,
                                color_continuous_scale="Viridis",
                                title=f"Relationship: {var1[:30]}... vs {var2[:30]}..."
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Statistics
                            chi2, p_value, dof, expected = chi2_contingency(cross_tab)
                            st.write(f"**Statistical significance:** {analyzer._interpret_p_value(p_value)}")
                            
                            st.dataframe(cross_tab, use_container_width=True)
                else:
                    st.info("Not enough variables available for relationship analysis")
            
            with tab5:
                st.header("📍 Demographics Overview")
                
                demo_charts = analyzer.create_demographics_analysis()
                
                if demo_charts:
                    cols = st.columns(2)
                    for i, chart in enumerate(demo_charts):
                        with cols[i % 2]:
                            st.plotly_chart(chart, use_container_width=True)
                else:
                    st.info("No demographic charts available")
            
            with tab6:
                st.header("💭 Key Insights & Recommendations")
                
                st.markdown("""
                <div class="highlight-box">
                <h3>🎯 Research Questions Explored</h3>
                <ul>
                    <li><strong>Education & Satisfaction:</strong> How does educational background relate to birth experience satisfaction?</li>
                    <li><strong>Mental Health & Family Planning:</strong> Do postpartum mental health experiences influence decisions about future children?</li>
                    <li><strong>Support Systems:</strong> How does partner support correlate with anxiety and emotional wellbeing?</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Key findings summary
                st.subheader("📋 Summary Statistics")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Response Rate by Question", f"{(df.notna().mean().mean()*100):.1f}%")
                    
                    # Most common responses
                    if analyzer.key_questions['birth_satisfaction']:
                        most_common_satisfaction = df[analyzer.key_questions['birth_satisfaction']].mode().iloc[0]
                        st.write(f"**Most common birth satisfaction rating:** {most_common_satisfaction}")
                
                with col2:
                    if analyzer.key_questions['postpartum_depression']:
                        depression_rate = (df[analyzer.key_questions['postpartum_depression']].str.contains('Da', na=False).sum() / len(df) * 100)
                        st.metric("Reported Postpartum Depression", f"{depression_rate:.1f}%")
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.info("Please ensure your file is a valid Excel (.xlsx, .xls) or CSV (.csv) format")
    
    else:
        st.info("👆 Please upload your maternity survey Excel file to begin analysis")
        
        st.markdown("""
        ### 🎯 Specialized Analysis Features:
        - 🎓 **Education vs Satisfaction:** Statistical analysis of how educational background relates to birth experience
        - 🧠 **Mental Health Impact:** Examine relationships between postpartum depression and family planning decisions
        - 🤝 **Support System Analysis:** Correlate partner support with mental health outcomes
        - 📊 **Statistical Significance:** Chi-square tests and p-values for all relationships
        - 💡 **Actionable Insights:** Data-driven recommendations for maternal support programs
        
        ### 📁 Supported File Formats:
        - **Excel files** (.xlsx, .xls)
        - **CSV files** (.csv)
        - First row should contain question headers
        - Each row represents one survey response
        """)


if __name__ == "__main__":
    main()