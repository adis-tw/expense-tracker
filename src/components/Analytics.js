import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { calculateAnalytics } from '../utils/analytics';
import './Analytics.css';

const Analytics = ({ expenses, expenseHeads }) => {
  const analytics = calculateAnalytics(expenses, expenseHeads);

  const pieData = Object.entries(analytics.byHead).map(([name, data]) => ({
    name,
    value: data.total,
    percentage: data.percentage.toFixed(1)
  }));

  const barData = Object.entries(analytics.byHead).map(([name, data]) => ({
    name,
    amount: data.total,
    count: data.count
  }));

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140'];

  if (expenses.length === 0) {
    return (
      <div className="analytics-container">
        <h3>Analytics</h3>
        <p className="empty-message">No data available. Add expenses to see analytics.</p>
      </div>
    );
  }

  return (
    <div className="analytics-container">
      <h3>Analytics</h3>
      
      <div className="analytics-summary">
        <div className="summary-card">
          <div className="summary-label">Total Expenses</div>
          <div className="summary-value">${analytics.total.toFixed(2)}</div>
        </div>
        <div className="summary-card">
          <div className="summary-label">Number of Expenses</div>
          <div className="summary-value">{analytics.count}</div>
        </div>
        <div className="summary-card">
          <div className="summary-label">Average Expense</div>
          <div className="summary-value">${analytics.average.toFixed(2)}</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h4>Expenses by Head (Pie Chart)</h4>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percentage }) => `${name}: ${percentage}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h4>Expenses by Head (Bar Chart)</h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
              <Legend />
              <Bar dataKey="amount" fill="#667eea" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="expense-heads-breakdown">
        <h4>Detailed Breakdown</h4>
        <table className="breakdown-table">
          <thead>
            <tr>
              <th>Expense Head</th>
              <th>Total Amount</th>
              <th>Number of Expenses</th>
              <th>Percentage</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(analytics.byHead)
              .sort((a, b) => b[1].total - a[1].total)
              .map(([name, data]) => (
                <tr key={name}>
                  <td>{name}</td>
                  <td className="amount-cell">${data.total.toFixed(2)}</td>
                  <td>{data.count}</td>
                  <td>{data.percentage.toFixed(2)}%</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Analytics;
