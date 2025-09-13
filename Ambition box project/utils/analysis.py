# utils/analysis.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import statsmodels.api as sm
from statsmodels.formula.api import ols
import numpy as np

def create_company_age_distribution(df):
    """Create a histogram of company age distribution"""
    if df.empty:
        return "<div class='alert alert-info'>No data available for the selected filters</div>"
    
    # Check if years_old column exists
    if 'years_old' in df.columns and not df['years_old'].isnull().all():
        # Remove unrealistic ages (negative or too high)
        df_filtered = df[(df['years_old'] > 0) & (df['years_old'] < 200)]
        
        fig = px.histogram(df_filtered, x='years_old', nbins=20, 
                           title='Distribution of Company Age',
                           labels={'years_old': 'Company Age (years)'})
        return fig.to_html()
    else:
        return "<div class='alert alert-info'>Company age data not available</div>"

def create_rating_distribution_chart(df):
    """Create a histogram of rating distribution"""
    if df.empty:
        return "<div class='alert alert-info'>No data available for the selected filters</div>"
    
    fig = px.histogram(df, x='company_rating', nbins=20, 
                       title='Distribution of Company Ratings',
                       labels={'company_rating': 'Company Rating'})
    return fig.to_html()



def create_rating_by_size_chart(df):
    """Create a boxplot of ratings by company size"""
    if df.empty:
        return "<div class='alert alert-info'>No data available for the selected filters</div>"
    
    fig = px.box(df, x='size', y='company_rating', 
                 title='Rating Distribution by Company Size',
                 labels={'company_rating': 'Company Rating', 'size': 'Company Size'})
    return fig.to_html()

def create_rating_by_name_chart(df):
    """Create a bar chart of ratings by company name (top 10)"""
    if df.empty:
        return "<div class='alert alert-info'>No data available for the selected filters</div>"
    
    # Get top 10 companies by rating
    top_companies = df.nlargest(10, 'company_rating')
    
    fig = px.bar(top_companies, x='company_name', y='company_rating', 
                 title='Top 10 Companies by Rating',
                 labels={'company_rating': 'Company Rating', 'company_name': 'Company Name'})
    fig.update_layout(xaxis_tickangle=-45)
    return fig.to_html()

def create_rating_distribution_overview(df):
    """Create a comprehensive view of rating distribution"""
    if df.empty:
        return "<div class='alert alert-info'>No data available for the selected filters</div>"
    
    # Create subplots with 2 rows and 2 columns, but only use 3 of them
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Rating Distribution', 'Rating by Company Size',
                       'Top 10 Companies by Rating', ''),
        specs=[[{"type": "histogram"}, {"type": "box"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # Rating Distribution - Top Left
    fig.add_trace(
        go.Histogram(x=df['company_rating'], nbinsx=20, name="Rating Distribution"),
        row=1, col=1
    )
    
    # Rating by Company Size - Top Right
    for size in df['size'].unique():
        size_data = df[df['size'] == size]['company_rating']
        fig.add_trace(
            go.Box(y=size_data, name=size),
            row=1, col=2
        )
    
    # Top 10 Companies by Rating - Bottom Left
    top_companies = df.nlargest(10, 'company_rating')
    fig.add_trace(
        go.Bar(x=top_companies['company_name'], y=top_companies['company_rating'],
               name="Top Companies"),
        row=2, col=1
    )
    
    # Leave bottom-right empty - remove any traces that might be added
    
    # Update layout
    fig.update_layout(
        height=800, 
        title_text="Company Rating Analytics Dashboard", 
        showlegend=True,
        title_font_size=24
    )
    
    # Update axes titles
    fig.update_xaxes(title_text="Company Rating", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=1)
    
    fig.update_xaxes(title_text="Company Size", row=1, col=2)
    fig.update_yaxes(title_text="Company Rating", row=1, col=2)
    
    fig.update_xaxes(title_text="Company Name", row=2, col=1)
    fig.update_yaxes(title_text="Company Rating", row=2, col=1)
    
    # Remove axes from the empty bottom-right quadrant
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False, row=2, col=2)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, row=2, col=2)
    
    # Remove the empty subplot title
    fig.update_annotations(selector=dict(text=''), text='')
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=-45, row=2, col=1)
    
    return fig.to_html()

def perform_rating_anova(df):
    """Perform ANOVA to check if rating differs by industry"""
    if df.empty or len(df['industry'].unique()) < 2:
        return None
    
    try:
        model = ols('company_rating ~ C(industry)', data=df).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        return anova_table
    except:
        return None