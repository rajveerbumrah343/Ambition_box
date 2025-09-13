from flask import Flask, render_template, request, jsonify,abort
import pandas as pd
import os
from utils.analysis import *

app = Flask(__name__)

# Load the dataset
def load_data():
    data_path = os.path.join('data', 'all_cities_data.csv')
    df = pd.read_csv(data_path)
    return df

@app.route('/')
def index():
    df = load_data()
    
    # Get unique values for filters
    industries = sorted(df['industry'].dropna().unique())
    locations = sorted(df['location'].dropna().unique())
    sizes = sorted(df['size'].dropna().unique())
    types = sorted(df['type'].dropna().unique())
    
    # Get top rated companies
    top_companies = df.nlargest(10, 'company_rating')
    
    # Create some charts for the homepage
    
    rating_dist_chart = create_rating_distribution_chart(df)
    
    return render_template('index.html', 
                         industries=industries,
                         locations=locations,
                         sizes=sizes,
                         types=types,
                         top_companies=top_companies.to_dict('records'),
                         
                         rating_dist_chart=rating_dist_chart)

@app.route('/company/<company_name>')
def company_detail(company_name):
    df = load_data()
    try:
        company = df[df['company_name'] == company_name].iloc[0].to_dict()
        
        # Get related companies (same industry)
        related_companies = df[
            (df['industry'] == company['industry']) & 
            (df['company_name'] != company_name)
        ].nlargest(4, 'company_rating').to_dict('records')
        
    except (IndexError, KeyError):
        abort(404, description="Company not found")
    
    return render_template('company.html', 
                         company=company,
                         related_companies=related_companies)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    industry = request.args.get('industry', '')
    location = request.args.get('location', '')
    size = request.args.get('size', '')
    company_type = request.args.get('type', '')
    min_rating = request.args.get('min_rating', 0, type=float)
    
    df = load_data()
    
    # Apply filters
    filtered_df = df.copy()
    if query:
        filtered_df = filtered_df[filtered_df['company_name'].str.contains(query, case=False, na=False)]
    if industry:
        filtered_df = filtered_df[filtered_df['industry'] == industry]
    if location:
        filtered_df = filtered_df[filtered_df['location'] == location]
    if size:
        filtered_df = filtered_df[filtered_df['size'] == size]
    if company_type:
        filtered_df = filtered_df[filtered_df['type'] == company_type]
    if min_rating:
        filtered_df = filtered_df[filtered_df['company_rating'] >= min_rating]
    
    # Get unique values for filters
    industries = sorted(df['industry'].dropna().unique())
    locations = sorted(df['location'].dropna().unique())
    sizes = sorted(df['size'].dropna().unique())
    types = sorted(df['type'].dropna().unique())
    
    # Add CSV download functionality
    csv_required = request.args.get('csv', '')
    if csv_required.lower() == 'true':
        # Return CSV instead of HTML
        csv_data = filtered_df.to_csv(index=False)
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=filtered_companies.csv'
        }
    
    return render_template('search.html', 
                         companies=filtered_df.to_dict('records'),
                         industries=industries,
                         locations=locations,
                         sizes=sizes,
                         types=types,
                         query=query,
                         industry=industry,
                         location=location,
                         size=size,
                         type=company_type,
                         min_rating=min_rating)

# app.py (update the analytics route)
@app.route('/analytics')
def analytics():
    df = load_data()
    
    # Get filter parameters from the request
    industry_filter = request.args.get('industry', '')
    location_filter = request.args.get('location', '')
    size_filter = request.args.get('size', '')
    min_rating_filter = request.args.get('min_rating', 0, type=float)
    
    # Apply filters if provided
    filtered_df = df.copy()
    if industry_filter:
        filtered_df = filtered_df[filtered_df['industry'] == industry_filter]
    if location_filter:
        filtered_df = filtered_df[filtered_df['location'] == location_filter]
    if size_filter:
        filtered_df = filtered_df[filtered_df['size'] == size_filter]
    if min_rating_filter:
        filtered_df = filtered_df[filtered_df['company_rating'] >= min_rating_filter]
    
    # Get unique values for filters
    industries = sorted(df['industry'].dropna().unique())
    locations = sorted(df['location'].dropna().unique())
    sizes = sorted(df['size'].dropna().unique())
    
    # Create all charts using FILTERED data
    company_age_chart = create_company_age_distribution(filtered_df)
    rating_dist_chart = create_rating_distribution_chart(filtered_df)

    rating_by_size_chart = create_rating_by_size_chart(filtered_df)
    rating_by_name_chart = create_rating_by_name_chart(filtered_df)
    dashboard_chart = create_rating_distribution_overview(filtered_df)
    
    # Get the count of filtered companies
    filtered_companies_count = len(filtered_df)
    
    return render_template('analytics.html',
                         company_age_chart=company_age_chart,
                         rating_dist_chart=rating_dist_chart,
                         
                         rating_by_size_chart=rating_by_size_chart,
                         rating_by_name_chart=rating_by_name_chart,
                         dashboard_chart=dashboard_chart,
                         industries=industries,
                         locations=locations,
                         sizes=sizes,
                         current_industry=industry_filter,
                         current_location=location_filter,
                         current_size=size_filter,
                         current_min_rating=min_rating_filter,
                         filtered_companies_count=filtered_companies_count)

@app.route('/api/companies')
def api_companies():
    df = load_data()
    return jsonify(df.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True)