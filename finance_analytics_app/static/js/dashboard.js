// Dashboard JavaScript for Finance Analytics App

let dashboardData = null;
let charts = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadAllCharts();
    loadInsights();
});

function initializeDashboard() {
    // Add animation classes to cards
    const summaryCards = document.querySelectorAll('#summaryCards .card');
    summaryCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('slide-in-left');
        }, index * 150);
    });
    
    // Initialize chart containers
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        showLoading(container.id);
    });
}

async function loadAllCharts() {
    try {
        // Load all charts in parallel
        const chartPromises = [
            loadChart('expensePieChart', 'expense_categories'),
            loadChart('incomePieChart', 'income_sources'),
            loadChart('monthlyTrendsChart', 'monthly_trends'),
            loadChart('categoryBarChart', 'category_bars'),
            loadChart('cumulativeSavingsChart', 'cumulative_savings')
        ];
        
        await Promise.all(chartPromises);
        
        // Add resize listeners
        window.addEventListener('resize', debounce(resizeAllCharts, 250));
        
    } catch (error) {
        console.error('Error loading charts:', error);
        showGlobalError('Failed to load charts. Please refresh the page.');
    }
}

async function loadChart(containerId, chartType) {
    try {
        showLoading(containerId);
        
        const response = await fetch(`/api/charts/${chartType}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const chartData = await response.json();
        
        if (chartData.error) {
            throw new Error(chartData.error);
        }
        
        // Store chart reference
        charts[containerId] = chartData;
        
        // Configure chart layout
        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false,
            toImageButtonOptions: {
                format: 'png',
                filename: `finance_${chartType}`,
                height: 500,
                width: 800,
                scale: 1
            }
        };
        
        // Enhanced layout settings
        if (chartData.layout) {
            chartData.layout.font = { family: 'Inter, sans-serif', size: 12 };
            chartData.layout.paper_bgcolor = 'rgba(0,0,0,0)';
            chartData.layout.plot_bgcolor = 'rgba(0,0,0,0)';
            chartData.layout.margin = { t: 50, b: 50, l: 50, r: 50 };
        }
        
        // Plot the chart
        await Plotly.newPlot(containerId, chartData.data, chartData.layout, config);
        
        // Add hover effects
        addChartHoverEffects(containerId);
        
    } catch (error) {
        console.error(`Error loading chart ${chartType}:`, error);
        showError(containerId, `Failed to load ${chartType.replace('_', ' ')} chart`);
    }
}

function addChartHoverEffects(containerId) {
    const chartElement = document.getElementById(containerId);
    if (!chartElement) return;
    
    chartElement.on('plotly_hover', function(data) {
        // Add subtle animation on hover
        chartElement.style.transform = 'scale(1.02)';
        chartElement.style.transition = 'transform 0.2s ease';
    });
    
    chartElement.on('plotly_unhover', function(data) {
        chartElement.style.transform = 'scale(1)';
    });
}

async function loadInsights() {
    try {
        const container = document.getElementById('insightsContainer');
        showLoading('insightsContainer');
        
        const response = await fetch('/api/summary');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        dashboardData = data;
        displayInsights(data.insights || []);
        
    } catch (error) {
        console.error('Error loading insights:', error);
        showError('insightsContainer', 'Failed to load insights');
    }
}

function displayInsights(insights) {
    const container = document.getElementById('insightsContainer');
    if (!container) return;
    
    if (!insights || insights.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-info-circle fa-2x mb-3"></i>
                <p>No insights available yet. Try uploading more transaction data.</p>
            </div>
        `;
        return;
    }
    
    const insightsList = insights.map((insight, index) => `
        <div class="insight-item fade-in" style="animation-delay: ${index * 0.1}s">
            <div class="d-flex align-items-start">
                <div class="insight-icon me-3">
                    <i class="fas fa-lightbulb text-warning"></i>
                </div>
                <div class="insight-content">
                    <p class="mb-0">${insight}</p>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = `
        <div class="insights-list">
            ${insightsList}
        </div>
    `;
}

function resizeAllCharts() {
    Object.keys(charts).forEach(containerId => {
        const element = document.getElementById(containerId);
        if (element && element.data) {
            Plotly.Plots.resize(element);
        }
    });
}

function refreshDashboard() {
    // Add loading state to all charts
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        showLoading(container.id);
    });
    
    // Show loading for insights
    showLoading('insightsContainer');
    
    // Reload all data
    loadAllCharts();
    loadInsights();
    
    // Show success message
    showSuccess('Dashboard refreshed successfully!');
}

// Export dashboard data
function exportDashboardData(format = 'json') {
    if (!dashboardData) {
        alert('No data available to export');
        return;
    }
    
    const exportData = {
        summary: dashboardData,
        timestamp: new Date().toISOString(),
        charts: Object.keys(charts)
    };
    
    const filename = `finance_dashboard_${new Date().toISOString().split('T')[0]}`;
    exportData(exportData, filename, format);
}

// Print dashboard
function printDashboard() {
    const printContent = document.querySelector('.dashboard-content').innerHTML;
    const printWindow = window.open('', '_blank');
    
    printWindow.document.write(`
        <html>
            <head>
                <title>Finance Analytics Dashboard</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        margin: 20px; 
                        color: #333;
                    }
                    .card { 
                        border: 1px solid #ddd; 
                        margin-bottom: 20px; 
                        border-radius: 8px;
                    }
                    .card-header { 
                        background: #f8f9fa; 
                        padding: 15px; 
                        border-bottom: 1px solid #ddd;
                        font-weight: bold;
                    }
                    .card-body { 
                        padding: 15px; 
                    }
                    .chart-container { 
                        width: 100%; 
                        height: 400px; 
                        margin: 20px 0;
                    }
                    .row { 
                        display: flex; 
                        flex-wrap: wrap; 
                    }
                    .col-lg-3, .col-md-6 { 
                        flex: 1; 
                        min-width: 200px; 
                        margin: 10px;
                    }
                    @media print {
                        body { margin: 0; }
                        .card { break-inside: avoid; }
                    }
                </style>
            </head>
            <body>
                <h1>Finance Analytics Dashboard Report</h1>
                <p>Generated on: ${new Date().toLocaleDateString()}</p>
                ${printContent}
            </body>
        </html>
    `);
    
    printWindow.document.close();
    setTimeout(() => {
        printWindow.print();
    }, 250);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + R for refresh
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        refreshDashboard();
    }
    
    // Ctrl/Cmd + P for print
    if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault();
        printDashboard();
    }
    
    // Ctrl/Cmd + S for export
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        exportDashboardData('json');
    }
});

function showGlobalError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after 8 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 8000);
}

// Chart interaction handlers
function onChartClick(chartId, data) {
    // Handle chart click events for drill-down functionality
    console.log(`Chart ${chartId} clicked:`, data);
    
    // You can add drill-down functionality here
    // For example, showing detailed breakdown on click
}

// Real-time updates (if needed)
function enableRealTimeUpdates(intervalMinutes = 5) {
    setInterval(() => {
        console.log('Checking for updates...');
        // Add logic to check for new data and update if necessary
        // refreshDashboard();
    }, intervalMinutes * 60 * 1000);
}

// Initialize tooltips for summary cards
function initializeSummaryTooltips() {
    const summaryCards = document.querySelectorAll('#summaryCards .card');
    summaryCards.forEach(card => {
        card.setAttribute('data-bs-toggle', 'tooltip');
        card.setAttribute('data-bs-placement', 'top');
        // Add relevant tooltip text based on card type
    });
}