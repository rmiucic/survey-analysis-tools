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

# Page configuration
st.set_page_config(
    page_title="Survey Data Analyzer", 
    page_icon="📊", 
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
</style>
""", unsafe_allow_html=True)


class SurveyAnalyzer:
    def __init__(self, df):
        self.df = df
        self.categorical_questions = []
        self.yes_no_questions = []
        self.text_questions = []
        self.rating_questions = []
        self._categorize_questions()
    
    def _categorize_questions(self):
        """Categorize questions by type"""
        for col in self.df.columns[1:]:  # Skip timestamp
            unique_count = self.df[col].nunique()
            sample_values = self.df[col].dropna().unique()[:5]
            
            # Rating scales (look for patterns like "1 = ... 5 =")
            if any("1 =" in str(val) or "5 =" in str(val) for val in sample_values):
                self.rating_questions.append(col)
            # Yes/No questions
            elif unique_count <= 3 and any(str(val) in ['Da', 'Ne'] for val in sample_values):
                self.yes_no_questions.append(col)
            # Categorical (reasonable number of categories)
            elif unique_count <= 10:
                self.categorical_questions.append(col)
            # Text/open-ended
            else:
                self.text_questions.append(col)
    
    def create_demographics_charts(self):
        """Create demographic overview charts"""
        charts = []
        
        # Location distribution
        if len(self.df.columns) > 1:
            location_col = self.df.columns[1]  # "Gde živiš?"
            location_counts = self.df[location_col].value_counts()
            
            fig_location = px.pie(
                values=location_counts.values,
                names=location_counts.index,
                title="Distribution by Location Type"
            )
            charts.append(("Location Distribution", fig_location))
        
        # Region distribution
        if len(self.df.columns) > 2:
            region_col = self.df.columns[2]  # "U kom kraju zemlje živiš?"
            region_counts = self.df[region_col].value_counts()
            
            fig_region = px.bar(
                x=region_counts.index,
                y=region_counts.values,
                title="Distribution by Region",
                labels={'x': 'Region', 'y': 'Count'}
            )
            fig_region.update_xaxis(tickangle=45)
            charts.append(("Region Distribution", fig_region))
        
        # Age distribution
        if len(self.df.columns) > 3:
            age_col = self.df.columns[3]  # Age when became mother
            age_counts = self.df[age_col].value_counts()
            
            fig_age = px.bar(
                x=age_counts.values,
                y=age_counts.index,
                orientation='h',
                title="Age When Became Mother",
                labels={'x': 'Count', 'y': 'Age Group'}
            )
            charts.append(("Age Distribution", fig_age))
        
        # Education level
        if len(self.df.columns) > 4:
            edu_col = self.df.columns[4]  # Education level
            edu_counts = self.df[edu_col].value_counts()
            
            fig_edu = px.pie(
                values=edu_counts.values,
                names=edu_counts.index,
                title="Education Level Distribution"
            )
            charts.append(("Education Distribution", fig_edu))
        
        return charts
    
    def create_experience_charts(self):
        """Create birth/pregnancy experience charts"""
        charts = []
        
        # Find birth method question
        birth_cols = [col for col in self.df.columns if 'porodila' in col.lower()]
        if birth_cols:
            birth_counts = self.df[birth_cols[0]].value_counts()
            fig_birth = px.pie(
                values=birth_counts.values,
                names=birth_counts.index,
                title="Birth Method Distribution"
            )
            charts.append(("Birth Method", fig_birth))
        
        # Find birth experience rating
        rating_cols = [col for col in self.df.columns if 'iskustvo porođaja' in col.lower()]
        if rating_cols:
            rating_counts = self.df[rating_cols[0]].value_counts()
            fig_rating = px.bar(
                x=rating_counts.index,
                y=rating_counts.values,
                title="Birth Experience Rating (1=Very Bad, 5=Excellent)",
                labels={'x': 'Rating', 'y': 'Count'}
            )
            charts.append(("Birth Experience Rating", fig_rating))
        
        # Planned pregnancy
        planned_cols = [col for col in self.df.columns if 'planirana' in col.lower()]
        if planned_cols:
            planned_counts = self.df[planned_cols[0]].value_counts()
            fig_planned = px.pie(
                values=planned_counts.values,
                names=planned_counts.index,
                title="Was Pregnancy Planned?"
            )
            charts.append(("Pregnancy Planning", fig_planned))
        
        return charts
    
    def create_cross_analysis(self, var1, var2):
        """Create cross-tabulation analysis"""
        if var1 and var2 and var1 != var2:
            cross_tab = pd.crosstab(self.df[var1], self.df[var2], margins=True)
            cross_tab = cross_tab.iloc[:-1, :-1]  # Remove margins
            
            fig = px.imshow(
                cross_tab.values,
                x=cross_tab.columns,
                y=cross_tab.index,
                aspect="auto",
                color_continuous_scale="Blues",
                title=f"Cross-analysis: {var1} vs {var2}"
            )
            fig.update_xaxis(tickangle=45)
            fig.update_yaxis(tickangle=0)
            
            return fig
        return None
    
    def analyze_text_responses(self, text_column):
        """Analyze text responses"""
        text_data = self.df[text_column].dropna()
        
        if len(text_data) == 0:
            return None, None
        
        # Combine all text
        all_text = " ".join(text_data.astype(str))
        
        # Clean text for word cloud
        cleaned_text = re.sub(r'[^\w\s]', ' ', all_text.lower())
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Generate word cloud
        try:
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                max_words=100,
                colormap='viridis'
            ).generate(cleaned_text)
            
            # Convert to image
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(f"Word Cloud: {text_column}", fontsize=16, pad=20)
            
            # Convert to bytes
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer, len(text_data)
        except:
            return None, len(text_data)


def main():
    st.title("📊 Survey Data Analyzer")
    st.markdown("Upload your survey Excel file to generate interactive visualizations")
    
    # Sidebar for file upload
    st.sidebar.header("📁 Upload Data")
    uploaded_file = st.sidebar.file_uploader(
        "Choose an Excel file", 
        type=['xlsx', 'xls'],
        help="Upload your survey data in Excel format"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            with st.spinner("Loading data..."):
                df = pd.read_excel(uploaded_file)
            
            # Initialize analyzer
            analyzer = SurveyAnalyzer(df)
            
            # Display basic info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Participants", len(df))
            with col2:
                st.metric("Total Questions", len(df.columns) - 1)
            with col3:
                st.metric("Categorical Questions", len(analyzer.categorical_questions))
            with col4:
                st.metric("Text Questions", len(analyzer.text_questions))
            
            # Main analysis tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📍 Demographics", 
                "🤱 Birth Experience", 
                "🔍 Cross Analysis", 
                "💭 Text Analysis",
                "📋 Raw Data"
            ])
            
            with tab1:
                st.header("Demographics Overview")
                demo_charts = analyzer.create_demographics_charts()
                
                if demo_charts:
                    cols = st.columns(2)
                    for i, (title, chart) in enumerate(demo_charts):
                        with cols[i % 2]:
                            st.plotly_chart(chart, use_container_width=True)
                else:
                    st.info("No demographic data found")
            
            with tab2:
                st.header("Birth & Pregnancy Experience")
                exp_charts = analyzer.create_experience_charts()
                
                if exp_charts:
                    cols = st.columns(2)
                    for i, (title, chart) in enumerate(exp_charts):
                        with cols[i % 2]:
                            st.plotly_chart(chart, use_container_width=True)
                else:
                    st.info("No experience data found")
            
            with tab3:
                st.header("Cross-Variable Analysis")
                st.markdown("Compare how different variables relate to each other")
                
                col1, col2 = st.columns(2)
                with col1:
                    var1 = st.selectbox(
                        "Select first variable:",
                        options=analyzer.categorical_questions + analyzer.yes_no_questions,
                        key="var1"
                    )
                with col2:
                    var2 = st.selectbox(
                        "Select second variable:",
                        options=analyzer.categorical_questions + analyzer.yes_no_questions,
                        key="var2"
                    )
                
                if st.button("Generate Cross Analysis"):
                    cross_fig = analyzer.create_cross_analysis(var1, var2)
                    if cross_fig:
                        st.plotly_chart(cross_fig, use_container_width=True)
                    else:
                        st.warning("Please select two different variables")
            
            with tab4:
                st.header("Text Response Analysis")
                
                if analyzer.text_questions:
                    selected_text_col = st.selectbox(
                        "Select text question to analyze:",
                        options=analyzer.text_questions
                    )
                    
                    if st.button("Analyze Text Responses"):
                        with st.spinner("Generating word cloud..."):
                            wordcloud_img, response_count = analyzer.analyze_text_responses(selected_text_col)
                            
                            st.subheader(f"Analysis of: {selected_text_col}")
                            st.metric("Number of Responses", response_count)
                            
                            if wordcloud_img:
                                st.image(wordcloud_img, caption="Word Cloud of Responses")
                            else:
                                st.warning("Could not generate word cloud for this text data")
                            
                            # Show sample responses
                            st.subheader("Sample Responses:")
                            sample_responses = df[selected_text_col].dropna().head(5)
                            for i, response in enumerate(sample_responses, 1):
                                st.write(f"**{i}.** {response}")
                else:
                    st.info("No text questions found in the data")
            
            with tab5:
                st.header("Raw Data Preview")
                st.dataframe(df.head(100), use_container_width=True)
                st.info(f"Showing first 100 rows of {len(df)} total")
                
                # Download button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download full data as CSV",
                    data=csv,
                    file_name='survey_data.csv',
                    mime='text/csv'
                )
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.info("Please ensure your file is a valid Excel format (.xlsx or .xls)")
    
    else:
        # Show example/instructions
        st.info("👆 Please upload your survey Excel file to begin analysis")
        
        st.markdown("""
        ### What this app can do:
        - 📊 **Automatic question type detection** (categorical, yes/no, text)
        - 📍 **Demographics visualization** (location, age, education)
        - 🤱 **Experience analysis** (birth method, satisfaction, planning)
        - 🔍 **Cross-variable comparisons** (see how different factors relate)
        - 💭 **Text analysis** (word clouds from open responses)
        - 📋 **Raw data exploration** with download capability
        
        ### Supported file types:
        - Excel files (.xlsx, .xls)
        - First row should contain question headers
        - Each row represents one survey response
        """)


if __name__ == "__main__":
    main()