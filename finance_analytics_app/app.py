from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import pandas as pd
import numpy as np
import os
from werkzeug.utils import secure_filename
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class FinanceAnalyzer:
    def __init__(self, data):
        self.data = self.clean_data(data)
        self.income_data = None
        self.expense_data = None
        self.monthly_summary = None
        self.category_expenses = None
        self.income_sources = None
        
    def clean_data(self, data):
        """Clean and preprocess the financial data"""
        # Convert date column to datetime
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        
        # Ensure Amount is numeric
        data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce')
        
        # Create absolute amount column
        data['Absolute_Amount'] = data['Amount'].abs()
        
        # Extract date components
        data['Month'] = data['Date'].dt.month
        data['Month_Year'] = data['Date'].dt.to_period('M')
        data['Day_of_Week'] = data['Date'].dt.day_name()
        data['Quarter'] = data['Date'].dt.quarter
        
        # Sort by date
        data = data.sort_values('Date')
        
        # Drop rows with missing essential data
        data = data.dropna(subset=['Date', 'Amount', 'Type'])
        
        return data
    
    def analyze_finances(self):
        """Perform comprehensive financial analysis"""
        # Separate income and expenses
        self.income_data = self.data[self.data['Type'] == 'Income'].copy()
        self.expense_data = self.data[self.data['Type'] == 'Expense'].copy()
        
        # Calculate basic metrics
        total_income = self.income_data['Amount'].sum()
        total_expenses = abs(self.expense_data['Amount'].sum())
        net_savings = total_income - total_expenses
        
        # Category analysis
        self.analyze_categories()
        
        # Time-based analysis
        self.analyze_monthly_trends()
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_savings': net_savings,
            'income_transactions': len(self.income_data),
            'expense_transactions': len(self.expense_data),
            'largest_income': self.income_data['Amount'].max() if not self.income_data.empty else 0,
            'largest_expense': abs(self.expense_data['Amount'].min()) if not self.expense_data.empty else 0
        }
    
    def analyze_categories(self):
        """Analyze spending and income by categories"""
        # Expense categories
        if not self.expense_data.empty:
            self.category_expenses = self.expense_data.groupby('Category')['Absolute_Amount'].agg(['sum', 'mean', 'count']).reset_index()
            self.category_expenses.columns = ['Category', 'Total_Amount', 'Average_Amount', 'Transaction_Count']
            self.category_expenses = self.category_expenses.sort_values('Total_Amount', ascending=False)
            
            total_expenses = self.category_expenses['Total_Amount'].sum()
            self.category_expenses['Percentage'] = (self.category_expenses['Total_Amount'] / total_expenses * 100).round(2)
        
        # Income sources
        if not self.income_data.empty:
            self.income_sources = self.income_data.groupby('Category')['Amount'].agg(['sum', 'mean', 'count']).reset_index()
            self.income_sources.columns = ['Source', 'Total_Amount', 'Average_Amount', 'Transaction_Count']
            self.income_sources = self.income_sources.sort_values('Total_Amount', ascending=False)
            
            total_income = self.income_sources['Total_Amount'].sum()
            self.income_sources['Percentage'] = (self.income_sources['Total_Amount'] / total_income * 100).round(2)
    
    def analyze_monthly_trends(self):
        """Analyze monthly financial trends"""
        # Monthly income
        monthly_income = self.income_data.groupby('Month_Year')['Amount'].sum().reset_index()
        monthly_income.columns = ['Month_Year', 'Monthly_Income']
        
        # Monthly expenses
        monthly_expenses = self.expense_data.groupby('Month_Year')['Absolute_Amount'].sum().reset_index()
        monthly_expenses.columns = ['Month_Year', 'Monthly_Expenses']
        
        # Merge and calculate net savings
        self.monthly_summary = pd.merge(monthly_income, monthly_expenses, on='Month_Year', how='outer').fillna(0)
        self.monthly_summary['Net_Savings'] = self.monthly_summary['Monthly_Income'] - self.monthly_summary['Monthly_Expenses']
        self.monthly_summary['Cumulative_Savings'] = self.monthly_summary['Net_Savings'].cumsum()
        self.monthly_summary['Month_Year_Str'] = self.monthly_summary['Month_Year'].astype(str)

# Global variable to store analyzer instance
analyzer = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global analyzer
    
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Read the uploaded file
            if filename.endswith('.csv'):
                data = pd.read_csv(filepath)
            else:
                data = pd.read_excel(filepath)
            
            # Initialize analyzer
            analyzer = FinanceAnalyzer(data)
            
            flash('File uploaded successfully!')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload CSV or Excel files only.')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    global analyzer
    
    if analyzer is None:
        flash('Please upload a file first')
        return redirect(url_for('index'))
    
    # Perform analysis
    summary = analyzer.analyze_finances()
    
    return render_template('dashboard.html', summary=summary)

@app.route('/api/charts/<chart_type>')
def get_charts(chart_type):
    global analyzer
    
    if analyzer is None:
        return jsonify({'error': 'No data available'})
    
    try:
        if chart_type == 'expense_categories':
            return jsonify(create_expense_pie_chart())
        elif chart_type == 'income_sources':
            return jsonify(create_income_pie_chart())
        elif chart_type == 'monthly_trends':
            return jsonify(create_monthly_trends_chart())
        elif chart_type == 'category_bars':
            return jsonify(create_category_bar_chart())
        elif chart_type == 'cumulative_savings':
            return jsonify(create_cumulative_savings_chart())
        else:
            return jsonify({'error': 'Invalid chart type'})
    
    except Exception as e:
        return jsonify({'error': str(e)})

def create_expense_pie_chart():
    """Create expense categories pie chart"""
    if analyzer.category_expenses is None or analyzer.category_expenses.empty:
        return {'data': [], 'layout': {}}
    
    fig = px.pie(
        analyzer.category_expenses, 
        values='Total_Amount', 
        names='Category',
        title='Expense Distribution by Category',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400, margin=dict(t=50, b=50, l=50, r=50))
    
    return json.loads(fig.to_json())

def create_income_pie_chart():
    """Create income sources pie chart"""
    if analyzer.income_sources is None or analyzer.income_sources.empty:
        return {'data': [], 'layout': {}}
    
    fig = px.pie(
        analyzer.income_sources, 
        values='Total_Amount', 
        names='Source',
        title='Income Distribution by Source',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400, margin=dict(t=50, b=50, l=50, r=50))
    
    return json.loads(fig.to_json())

def create_monthly_trends_chart():
    """Create monthly income vs expenses trend chart"""
    if analyzer.monthly_summary is None or analyzer.monthly_summary.empty:
        return {'data': [], 'layout': {}}
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=analyzer.monthly_summary['Month_Year_Str'],
        y=analyzer.monthly_summary['Monthly_Income'],
        mode='lines+markers',
        name='Income',
        line=dict(color='#2E8B57', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=analyzer.monthly_summary['Month_Year_Str'],
        y=analyzer.monthly_summary['Monthly_Expenses'],
        mode='lines+markers',
        name='Expenses',
        line=dict(color='#DC143C', width=3)
    ))
    
    fig.update_layout(
        title='Monthly Income vs Expenses Trend',
        xaxis_title='Month',
        yaxis_title='Amount',
        height=400,
        margin=dict(t=50, b=50, l=50, r=50),
        hovermode='x unified'
    )
    
    return json.loads(fig.to_json())

def create_category_bar_chart():
    """Create category-wise spending bar chart"""
    if analyzer.category_expenses is None or analyzer.category_expenses.empty:
        return {'data': [], 'layout': {}}
    
    fig = px.bar(
        analyzer.category_expenses.head(10), 
        x='Category', 
        y='Total_Amount',
        title='Top 10 Expense Categories',
        color='Total_Amount',
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        height=400,
        margin=dict(t=50, b=50, l=50, r=50),
        xaxis={'categoryorder': 'total descending'}
    )
    
    return json.loads(fig.to_json())

def create_cumulative_savings_chart():
    """Create cumulative savings chart"""
    if analyzer.monthly_summary is None or analyzer.monthly_summary.empty:
        return {'data': [], 'layout': {}}
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=analyzer.monthly_summary['Month_Year_Str'],
        y=analyzer.monthly_summary['Cumulative_Savings'],
        mode='lines+markers',
        fill='tonexty',
        name='Cumulative Savings',
        line=dict(color='#4169E1', width=3)
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    fig.update_layout(
        title='Cumulative Savings Over Time',
        xaxis_title='Month',
        yaxis_title='Cumulative Amount',
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return json.loads(fig.to_json())

@app.route('/api/summary')
def get_summary():
    global analyzer
    
    if analyzer is None:
        return jsonify({'error': 'No data available'})
    
    summary = analyzer.analyze_finances()
    
    # Add additional insights
    insights = []
    
    # Spending insights
    if analyzer.category_expenses is not None and not analyzer.category_expenses.empty:
        top_expense = analyzer.category_expenses.iloc[0]
        insights.append(f"Your highest expense category is {top_expense['Category']} at ${top_expense['Total_Amount']:,.2f}")
    
    # Income insights
    if analyzer.income_sources is not None and not analyzer.income_sources.empty:
        top_income = analyzer.income_sources.iloc[0]
        insights.append(f"Your primary income source is {top_income['Source']} contributing ${top_income['Total_Amount']:,.2f}")
    
    # Savings rate
    if summary['total_income'] > 0:
        savings_rate = (summary['net_savings'] / summary['total_income']) * 100
        insights.append(f"Your savings rate is {savings_rate:.1f}%")
    
    summary['insights'] = insights
    
    return jsonify(summary)

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)