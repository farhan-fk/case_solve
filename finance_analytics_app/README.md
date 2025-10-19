# Personal Finance Analytics Web Application

A professional web application for personal finance monitoring and analytics built with Flask and modern web technologies.

## Features

- **File Upload Support**: Upload CSV or Excel files with transaction data
- **Interactive Dashboards**: Beautiful, responsive charts using Plotly.js
- **Comprehensive Analytics**: 
  - Income vs Expense tracking
  - Category-wise breakdowns
  - Monthly trends analysis
  - Cumulative savings visualization
  - Automated insights generation
- **Professional UI/UX**: Modern design with Bootstrap 5 and custom styling
- **Export Capabilities**: Download charts and data in multiple formats
- **Mobile Responsive**: Works seamlessly on all devices

## Quick Start

### Installation

1. Clone or download the application:
```bash
git clone <your-repo-url>
cd finance_analytics_app
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

### Data Format Requirements

Your CSV/Excel file should contain the following columns:
- **Date**: Transaction date (YYYY-MM-DD format)
- **Amount**: Transaction amount (positive numbers)
- **Category**: Expense/Income category (e.g., Food, Salary, Entertainment)
- **Type**: Either "Income" or "Expense"
- **Description**: Optional transaction description

#### Example CSV Structure:
```csv
Date,Amount,Category,Type,Description
2024-01-01,3000.00,Salary,Income,Monthly salary
2024-01-02,50.00,Food,Expense,Lunch at restaurant
2024-01-03,1200.00,Rent,Expense,Monthly rent payment
```

## Application Structure

```
finance_analytics_app/
│
├── app.py                 # Flask application main file
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── templates/            # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Home page with file upload
│   └── dashboard.html   # Analytics dashboard
│
├── static/              # Static assets
│   ├── css/
│   │   └── style.css    # Custom styling
│   └── js/
│       ├── main.js      # Utility functions
│       └── dashboard.js # Dashboard interactions
│
└── uploads/             # Uploaded files (created automatically)
```

## API Endpoints

- `GET /` - Home page with file upload
- `POST /upload` - Upload and process transaction file
- `GET /dashboard` - View analytics dashboard
- `GET /api/summary` - Get financial summary data
- `GET /api/charts/<chart_type>` - Get specific chart data

## Technology Stack

### Backend
- **Flask**: Python web framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive chart generation
- **NumPy**: Numerical computations

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **Plotly.js**: Interactive data visualization
- **Font Awesome**: Icon library
- **Custom CSS**: Enhanced styling and animations

## Customization

### Adding New Chart Types

1. Extend the `FinanceAnalyzer` class in `app.py`:
```python
def create_new_chart(self):
    # Your chart logic here
    return {
        'data': chart_data,
        'layout': chart_layout
    }
```

2. Add a new route:
```python
@app.route('/api/charts/new_chart')
def get_new_chart():
    return jsonify(analyzer.create_new_chart())
```

3. Update the dashboard template to display the new chart.

### Styling Customization

Modify `static/css/style.css` to customize:
- Color schemes
- Typography
- Layout spacing
- Animation effects

### Adding New Features

The modular structure makes it easy to add:
- User authentication
- Data persistence (database integration)
- Advanced analytics (forecasting, budgeting)
- Export to PDF reports
- Email notifications

## Troubleshooting

### Common Issues

1. **File Upload Errors**:
   - Ensure your file has the required columns
   - Check date format (YYYY-MM-DD)
   - Verify Amount column contains only numbers

2. **Charts Not Loading**:
   - Check browser console for JavaScript errors
   - Ensure all static files are properly served
   - Verify API endpoints are responding

3. **Performance Issues**:
   - Large files (>10MB) may take longer to process
   - Consider data sampling for very large datasets

### Error Messages

The application provides detailed error messages for:
- Invalid file formats
- Missing required columns
- Data processing errors
- Chart generation failures

## Development

### Local Development Setup

1. Create a virtual environment:
```bash
python -m venv finance_app_env
source finance_app_env/bin/activate  # On Windows: finance_app_env\Scripts\activate
```

2. Install dependencies in development mode:
```bash
pip install -r requirements.txt
```

3. Enable Flask debug mode:
```bash
export FLASK_DEBUG=1  # On Windows: set FLASK_DEBUG=1
python app.py
```

### Testing with Sample Data

Use the provided sample data structure or create your own test CSV file following the format guidelines above.

## Deployment

### Production Deployment

For production deployment, consider:

1. **Using Gunicorn**:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

2. **Environment Variables**:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
```

3. **Web Server**: Use nginx or Apache as reverse proxy
4. **Database**: Consider PostgreSQL or MySQL for data persistence
5. **File Storage**: Use cloud storage (AWS S3, Google Cloud) for uploaded files

### Security Considerations

- Implement file upload size limits
- Validate file types and content
- Use HTTPS in production
- Add rate limiting for API endpoints
- Implement proper session management

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions:
1. Create an issue in the repository
2. Check the troubleshooting section
3. Review the application logs for detailed error information

---

**Happy Analyzing! 📊💰**