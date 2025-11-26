import React from 'react';
import './ExpenseList.css';

const ExpenseList = ({ expenses, expenseHeads, onDeleteExpense, onEditExpense }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (expenses.length === 0) {
    return (
      <div className="expense-list-container">
        <h3>Expenses</h3>
        <p className="empty-message">No expenses added yet. Add your first expense above!</p>
      </div>
    );
  }

  return (
    <div className="expense-list-container">
      <h3>Expenses ({expenses.length})</h3>
      <div className="expense-table-wrapper">
        <table className="expense-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Head</th>
              <th>Amount</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {expenses
              .sort((a, b) => new Date(b.date) - new Date(a.date))
              .map(expense => (
                <tr key={expense.id}>
                  <td>{formatDate(expense.date)}</td>
                  <td>{expense.head}</td>
                  <td className="amount-cell">${expense.amount.toFixed(2)}</td>
                  <td className="description-cell">{expense.description || '-'}</td>
                  <td>
                    <button
                      onClick={() => onDeleteExpense(expense.id)}
                      className="delete-expense-btn"
                      title="Delete expense"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ExpenseList;
