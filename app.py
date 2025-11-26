"""
Flask web application for expense tracker dashboard.
"""
from flask import Flask, render_template, jsonify, request
from datetime import datetime
from decimal import Decimal, InvalidOperation

from tracker import ExpenseTracker
from analytics import ExpenseAnalytics

app = Flask(__name__)
tracker = ExpenseTracker()


@app.route('/')
def index():
    """Main dashboard page."""
    periods = tracker.list_time_periods()
    return render_template('dashboard.html', periods=periods)


@app.route('/api/periods')
def get_periods():
    """API endpoint to get all periods."""
    periods = tracker.list_time_periods()
    return jsonify(periods)


@app.route('/api/period/<int:period_index>')
def get_period(period_index):
    """API endpoint to get period details."""
    period = tracker.get_time_period(index=period_index)
    if period is None:
        return jsonify({'error': 'Period not found'}), 404
    
    summary = ExpenseAnalytics.get_summary(period)
    return jsonify(summary)


@app.route('/api/period/<int:period_index>/expenses')
def get_period_expenses(period_index):
    """API endpoint to get expenses for a period."""
    period = tracker.get_time_period(index=period_index)
    if period is None:
        return jsonify({'error': 'Period not found'}), 404
    
    expenses = [
        {
            'id': exp.id,
            'date': exp.date.strftime('%Y-%m-%d'),
            'category': exp.category,
            'description': exp.description,
            'amount': float(exp.amount)
        }
        for exp in sorted(period.expenses, key=lambda x: x.date, reverse=True)
    ]
    return jsonify(expenses)


@app.route('/api/period/<int:period_index>/analytics')
def get_period_analytics(period_index):
    """API endpoint to get analytics for a period."""
    period = tracker.get_time_period(index=period_index)
    if period is None:
        return jsonify({'error': 'Period not found'}), 404
    
    analytics = ExpenseAnalytics.get_summary(period)
    return jsonify(analytics)


@app.route('/period/<int:period_index>')
def period_detail(period_index):
    """Period detail page."""
    period = tracker.get_time_period(index=period_index)
    if period is None:
        return "Period not found", 404
    
    return render_template('period_detail.html', period_index=period_index, period_name=period.period_name)


@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    """API endpoint to add an expense."""
    try:
        data = request.json
        period_index = data.get('period_index')
        amount = Decimal(str(data.get('amount')))
        category = data.get('category')
        description = data.get('description')
        date_str = data.get('date')
        
        if not all([period_index is not None, amount, category, description, date_str]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        date = datetime.strptime(date_str, '%Y-%m-%d')
        expense = tracker.add_expense(amount, category, description, date, period_index=period_index)
        
        return jsonify({
            'success': True,
            'expense': {
                'id': expense.id,
                'date': expense.date.strftime('%Y-%m-%d'),
                'category': expense.category,
                'description': expense.description,
                'amount': float(expense.amount)
            }
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/create_period', methods=['POST'])
def create_period():
    """API endpoint to create a new time period."""
    try:
        data = request.json
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
        expense_heads = data.get('expense_heads', [])
        period_name = data.get('period_name')
        
        if not expense_heads:
            return jsonify({'error': 'At least one expense head is required'}), 400
        
        period = tracker.create_time_period(start_date, end_date, expense_heads, period_name)
        
        return jsonify({
            'success': True,
            'period': {
                'index': len(tracker.time_periods) - 1,
                'name': period.period_name,
                'start_date': period.start_date.strftime('%Y-%m-%d'),
                'end_date': period.end_date.strftime('%Y-%m-%d'),
                'expense_heads': period.expense_heads
            }
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare', methods=['GET'])
def compare_periods():
    """API endpoint to compare two periods."""
    try:
        period1_idx = int(request.args.get('period1'))
        period2_idx = int(request.args.get('period2'))
        
        period1 = tracker.get_time_period(index=period1_idx)
        period2 = tracker.get_time_period(index=period2_idx)
        
        if period1 is None or period2 is None:
            return jsonify({'error': 'One or both periods not found'}), 404
        
        comparison = ExpenseAnalytics.compare_periods(period1, period2)
        return jsonify(comparison)
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Expense Tracker Web Dashboard")
    print("="*60)
    print("Dashboard running at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
