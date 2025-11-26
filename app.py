from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, date
import sqlite3
import json
import os
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
CORS(app)

DATABASE = 'expenses.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Time periods table
    c.execute('''CREATE TABLE IF NOT EXISTS time_periods
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  start_date TEXT NOT NULL,
                  end_date TEXT NOT NULL,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    
    # Expense heads table (editable per time period)
    c.execute('''CREATE TABLE IF NOT EXISTS expense_heads
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  time_period_id INTEGER NOT NULL,
                  head_name TEXT NOT NULL,
                  FOREIGN KEY (time_period_id) REFERENCES time_periods(id) ON DELETE CASCADE)''')
    
    # Expenses table
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  time_period_id INTEGER NOT NULL,
                  expense_head_id INTEGER NOT NULL,
                  amount REAL NOT NULL,
                  description TEXT,
                  expense_date TEXT NOT NULL,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (time_period_id) REFERENCES time_periods(id) ON DELETE CASCADE,
                  FOREIGN KEY (expense_head_id) REFERENCES expense_heads(id) ON DELETE CASCADE)''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Time Period Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/time-periods', methods=['GET'])
def get_time_periods():
    """Get all time periods"""
    conn = get_db_connection()
    periods = conn.execute('SELECT * FROM time_periods ORDER BY start_date DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in periods])

@app.route('/api/time-periods', methods=['POST'])
def create_time_period():
    """Create a new time period"""
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO time_periods (name, start_date, end_date)
                      VALUES (?, ?, ?)''',
                   (data['name'], data['start_date'], data['end_date']))
    period_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'id': period_id, 'message': 'Time period created successfully'}), 201

@app.route('/api/time-periods/<int:period_id>', methods=['DELETE'])
def delete_time_period(period_id):
    """Delete a time period (cascades to expenses and heads)"""
    conn = get_db_connection()
    conn.execute('DELETE FROM time_periods WHERE id = ?', (period_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Time period deleted successfully'})

# Expense Head Routes
@app.route('/api/time-periods/<int:period_id>/expense-heads', methods=['GET'])
def get_expense_heads(period_id):
    """Get expense heads for a specific time period"""
    conn = get_db_connection()
    heads = conn.execute('''SELECT * FROM expense_heads 
                            WHERE time_period_id = ? 
                            ORDER BY head_name''', (period_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in heads])

@app.route('/api/time-periods/<int:period_id>/expense-heads', methods=['POST'])
def create_expense_head(period_id):
    """Create a new expense head for a time period"""
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO expense_heads (time_period_id, head_name)
                      VALUES (?, ?)''',
                   (period_id, data['head_name']))
    head_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'id': head_id, 'message': 'Expense head created successfully'}), 201

@app.route('/api/expense-heads/<int:head_id>', methods=['PUT'])
def update_expense_head(head_id):
    """Update an expense head"""
    data = request.json
    conn = get_db_connection()
    conn.execute('UPDATE expense_heads SET head_name = ? WHERE id = ?',
                 (data['head_name'], head_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Expense head updated successfully'})

@app.route('/api/expense-heads/<int:head_id>', methods=['DELETE'])
def delete_expense_head(head_id):
    """Delete an expense head"""
    conn = get_db_connection()
    conn.execute('DELETE FROM expense_heads WHERE id = ?', (head_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Expense head deleted successfully'})

# Expense Routes
@app.route('/api/time-periods/<int:period_id>/expenses', methods=['GET'])
def get_expenses(period_id):
    """Get all expenses for a time period"""
    conn = get_db_connection()
    expenses = conn.execute('''SELECT e.*, eh.head_name 
                                FROM expenses e
                                JOIN expense_heads eh ON e.expense_head_id = eh.id
                                WHERE e.time_period_id = ?
                                ORDER BY e.expense_date DESC, e.created_at DESC''',
                            (period_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in expenses])

@app.route('/api/time-periods/<int:period_id>/expenses', methods=['POST'])
def create_expense(period_id):
    """Create a new expense"""
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO expenses (time_period_id, expense_head_id, amount, description, expense_date)
                      VALUES (?, ?, ?, ?, ?)''',
                   (period_id, data['expense_head_id'], data['amount'], 
                    data.get('description', ''), data['expense_date']))
    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'id': expense_id, 'message': 'Expense created successfully'}), 201

@app.route('/api/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Update an expense"""
    data = request.json
    conn = get_db_connection()
    conn.execute('''UPDATE expenses 
                    SET expense_head_id = ?, amount = ?, description = ?, expense_date = ?
                    WHERE id = ?''',
                 (data['expense_head_id'], data['amount'], 
                  data.get('description', ''), data['expense_date'], expense_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Expense updated successfully'})

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense"""
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Expense deleted successfully'})

# Analytics Routes
@app.route('/api/time-periods/<int:period_id>/analytics', methods=['GET'])
def get_analytics(period_id):
    """Get analytics for a time period"""
    conn = get_db_connection()
    
    # Total expenses
    total = conn.execute('''SELECT SUM(amount) as total 
                            FROM expenses 
                            WHERE time_period_id = ?''',
                         (period_id,)).fetchone()
    total_amount = total['total'] or 0
    
    # Expenses by head
    by_head = conn.execute('''SELECT eh.head_name, SUM(e.amount) as total
                               FROM expenses e
                               JOIN expense_heads eh ON e.expense_head_id = eh.id
                               WHERE e.time_period_id = ?
                               GROUP BY eh.id, eh.head_name
                               ORDER BY total DESC''',
                           (period_id,)).fetchall()
    
    # Daily expenses
    daily = conn.execute('''SELECT expense_date, SUM(amount) as total
                            FROM expenses
                            WHERE time_period_id = ?
                            GROUP BY expense_date
                            ORDER BY expense_date''',
                         (period_id,)).fetchall()
    
    # Average daily expense
    period_info = conn.execute('''SELECT start_date, end_date 
                                   FROM time_periods 
                                   WHERE id = ?''',
                                (period_id,)).fetchone()
    
    if period_info:
        start = datetime.strptime(period_info['start_date'], '%Y-%m-%d')
        end = datetime.strptime(period_info['end_date'], '%Y-%m-%d')
        days = (end - start).days + 1
        avg_daily = total_amount / days if days > 0 else 0
    else:
        avg_daily = 0
    
    conn.close()
    
    return jsonify({
        'total': total_amount,
        'average_daily': round(avg_daily, 2),
        'by_head': [dict(row) for row in by_head],
        'daily': [dict(row) for row in daily]
    })

# Google Sheets Export Route
@app.route('/api/time-periods/<int:period_id>/export', methods=['POST'])
def export_to_google_sheets(period_id):
    """Export expenses to Google Sheets"""
    try:
        from export_to_sheets import export_expenses_to_sheets
        result = export_expenses_to_sheets(period_id)
        return jsonify(result)
    except ImportError:
        return jsonify({
            'success': False,
            'message': 'Google Sheets export not configured. Please set up credentials.'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Export failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
