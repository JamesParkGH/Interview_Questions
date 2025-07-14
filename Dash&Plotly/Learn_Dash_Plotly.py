# Comprehensive Dash Dashboard with SQL Data and Interactive Visualizations
import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import numpy as np
import dash_ag_grid as dag
from datetime import datetime, timedelta

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Sales Analytics Dashboard"

# Create sample SQL database
def create_sample_database():
    """Create a sample SQLite database with sales data"""
    conn = sqlite3.connect('sales_data.db')
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    
    # Sample product data
    products = ['Laptop', 'Phone', 'Tablet', 'Headphones', 'Monitor', 'Keyboard', 'Mouse']
    categories = ['Electronics', 'Electronics', 'Electronics', 'Audio', 'Electronics', 'Accessories', 'Accessories']
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    # Generate sales data
    data = []
    for i in range(2000):
        product = np.random.choice(products)
        category = categories[products.index(product)]
        region = np.random.choice(regions)
        date = np.random.choice(dates)
        quantity = np.random.randint(1, 50)
        unit_price = np.random.uniform(50, 2000)
        total_sales = quantity * unit_price
        
        data.append({
            'date': pd.to_datetime(date).strftime('%Y-%m-%d'),
            'product': product,
            'category': category,
            'region': region,
            'quantity': quantity,
            'unit_price': round(unit_price, 2),
            'total_sales': round(total_sales, 2)
        })
    
    df = pd.DataFrame(data)
    df.to_sql('sales', conn, if_exists='replace', index=False)
    conn.close()
    return df

# Load data from SQL database
def load_data_from_sql():
    """Load data from SQLite database"""
    try:
        conn = sqlite3.connect('sales_data.db')
        query = """
        SELECT * FROM sales 
        ORDER BY date DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        # Create database if it doesn't exist
        return create_sample_database()

# Load initial data
df = load_data_from_sql()
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.to_period('M').astype(str)
df['year'] = df['date'].dt.year

# Dashboard layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("📊 Sales Analytics Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'})
    ]),
    
    # Control Panel
    html.Div([
        html.Div([
            html.H3("🎛️ Filters", style={'color': '#34495e'}),
            
            # Product dropdown
            html.Label("Select Product:", style={'fontWeight': 'bold', 'marginTop': '10px'}),
            dcc.Dropdown(
                id='product-dropdown',
                options=[{'label': 'All Products', 'value': 'all'}] + 
                        [{'label': product, 'value': product} for product in sorted(df['product'].unique())],
                value='all',
                style={'marginBottom': '15px'}
            ),
            
            # Category dropdown
            html.Label("Select Category:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': 'All Categories', 'value': 'all'}] + 
                        [{'label': category, 'value': category} for category in sorted(df['category'].unique())],
                value='all',
                style={'marginBottom': '15px'}
            ),
            
            # Region dropdown
            html.Label("Select Region:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='region-dropdown',
                options=[{'label': 'All Regions', 'value': 'all'}] + 
                        [{'label': region, 'value': region} for region in sorted(df['region'].unique())],
                value='all',
                style={'marginBottom': '15px'}
            ),
            
            # Date range picker
            html.Label("Select Date Range:", style={'fontWeight': 'bold'}),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=df['date'].min(),
                end_date=df['date'].max(),
                display_format='YYYY-MM-DD',
                style={'marginBottom': '15px'}
            ),
            
        ], className='control-panel', style={
            'width': '25%', 'float': 'left', 'padding': '20px',
            'backgroundColor': '#ecf0f1', 'borderRadius': '10px',
            'margin': '10px'
        }),
        
        # Main dashboard area
        html.Div([
            # KPI Cards
            html.Div(id='kpi-cards', style={'marginBottom': '20px'}),
            
            # Charts row 1
            html.Div([
                html.Div([
                    dcc.Graph(id='sales-trend-chart')
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(id='product-performance-chart')
                ], style={'width': '50%', 'display': 'inline-block'}),
            ]),
            
            # Charts row 2
            html.Div([
                html.Div([
                    dcc.Graph(id='regional-distribution-chart')
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(id='category-breakdown-chart')
                ], style={'width': '50%', 'display': 'inline-block'}),
            ]),
            
            # Data Table Section
            html.Div([
                html.H3("📋 Detailed Sales Data", style={'color': '#34495e', 'marginTop': '30px', 'marginBottom': '15px'}),
                html.Div([
                    dag.AgGrid(
                        id="sales-data-table",
                        columnDefs=[
                            {"field": "date", "headerName": "Date", "sortable": True, "filter": True, "width": 120},
                            {"field": "product", "headerName": "Product", "sortable": True, "filter": True, "width": 130},
                            {"field": "category", "headerName": "Category", "sortable": True, "filter": True, "width": 120},
                            {"field": "region", "headerName": "Region", "sortable": True, "filter": True, "width": 100},
                            {"field": "quantity", "headerName": "Quantity", "sortable": True, "filter": True, "type": "numericColumn", "width": 110},
                            {"field": "unit_price", "headerName": "Unit Price ($)", "sortable": True, "filter": True, "type": "numericColumn", "width": 130,
                             "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"}},
                            {"field": "total_sales", "headerName": "Total Sales ($)", "sortable": True, "filter": True, "type": "numericColumn", "width": 140,
                             "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"}}
                        ],
                        defaultColDef={
                            "resizable": True, 
                            "sortable": True, 
                            "filter": True,
                            "floatingFilter": True
                        },
                        rowData=[],
                        dashGridOptions={
                            "pagination": True,
                            "paginationPageSize": 20,
                            "domLayout": "autoHeight",
                            "rowSelection": "multiple"
                        },
                        style={"height": "500px", "width": "100%"}
                    )
                ], style={'backgroundColor': 'white', 'borderRadius': '10px', 'padding': '15px', 
                         'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
            ], style={'marginTop': '20px'}),
            
        ], style={'width': '70%', 'float': 'right', 'padding': '10px'})
    ], style={'overflow': 'hidden'}),
    
], style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'})

# Callback for updating all charts based on dropdown selections
@callback(
    [Output('kpi-cards', 'children'),
     Output('sales-trend-chart', 'figure'),
     Output('product-performance-chart', 'figure'),
     Output('regional-distribution-chart', 'figure'),
     Output('category-breakdown-chart', 'figure'),
     Output('sales-data-table', 'rowData')],
    [Input('product-dropdown', 'value'),
     Input('category-dropdown', 'value'),
     Input('region-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_dashboard(selected_product, selected_category, selected_region, start_date, end_date):
    # Filter data based on selections
    filtered_df = df.copy()
    
    if selected_product != 'all':
        filtered_df = filtered_df[filtered_df['product'] == selected_product]
    if selected_category != 'all':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_region != 'all':
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]
    
    # Calculate KPIs
    total_sales = filtered_df['total_sales'].sum()
    total_quantity = filtered_df['quantity'].sum()
    avg_order_value = total_sales / len(filtered_df) if len(filtered_df) > 0 else 0
    unique_products = filtered_df['product'].nunique()
    
    # KPI Cards
    kpi_cards = html.Div([
        html.Div([
            html.H4(f"${total_sales:,.2f}", style={'color': '#27ae60', 'margin': '0'}),
            html.P("Total Sales", style={'margin': '0', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 
                 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H4(f"{total_quantity:,}", style={'color': '#3498db', 'margin': '0'}),
            html.P("Units Sold", style={'margin': '0', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 
                 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H4(f"${avg_order_value:.2f}", style={'color': '#e74c3c', 'margin': '0'}),
            html.P("Avg Order Value", style={'margin': '0', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 
                 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H4(f"{unique_products}", style={'color': '#9b59b6', 'margin': '0'}),
            html.P("Unique Products", style={'margin': '0', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 
                 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
    ])
    
    # 1. Sales Trend Chart
    monthly_sales = filtered_df.groupby('month')['total_sales'].sum().reset_index()
    sales_trend_fig = px.line(monthly_sales, x='month', y='total_sales', 
                             title='📈 Sales Trend Over Time',
                             labels={'total_sales': 'Total Sales ($)', 'month': 'Month'})
    sales_trend_fig.update_layout(template='plotly_white')
    
    # 2. Product Performance Chart
    product_sales = filtered_df.groupby('product')['total_sales'].sum().reset_index().sort_values('total_sales', ascending=True)
    product_performance_fig = px.bar(product_sales, x='total_sales', y='product', 
                                   title='🏆 Product Performance',
                                   labels={'total_sales': 'Total Sales ($)', 'product': 'Product'},
                                   orientation='h')
    product_performance_fig.update_layout(template='plotly_white')
    
    # 3. Regional Distribution Chart
    regional_sales = filtered_df.groupby('region')['total_sales'].sum().reset_index()
    regional_fig = px.pie(regional_sales, values='total_sales', names='region', 
                         title='🌍 Sales by Region')
    regional_fig.update_layout(template='plotly_white')
    
    # 4. Category Breakdown Chart
    category_sales = filtered_df.groupby('category')['total_sales'].sum().reset_index()
    category_fig = px.bar(category_sales, x='category', y='total_sales', 
                         title='📊 Sales by Category',
                         labels={'total_sales': 'Total Sales ($)', 'category': 'Category'})
    category_fig.update_layout(template='plotly_white')
    
    # 5. Prepare data for AG Grid table
    table_data = filtered_df.copy()
    table_data['date'] = table_data['date'].dt.strftime('%Y-%m-%d')  # Format date for display
    table_data = table_data.sort_values('date', ascending=False)  # Most recent first
    
    return kpi_cards, sales_trend_fig, product_performance_fig, regional_fig, category_fig, table_data.to_dict('records')

if __name__ == '__main__':
    app.run(debug=True)
