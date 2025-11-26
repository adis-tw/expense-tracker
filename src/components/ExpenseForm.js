import React, { useState } from 'react';
import './ExpenseForm.css';

const ExpenseForm = ({ expenseHeads, onAddExpense }) => {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [head, setHead] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (date && head && amount && parseFloat(amount) > 0) {
      onAddExpense({
        id: Date.now().toString(),
        date,
        head,
        amount: parseFloat(amount),
        description: description.trim()
      });
      setDate(new Date().toISOString().split('T')[0]);
      setHead('');
      setAmount('');
      setDescription('');
    }
  };

  return (
    <div className="expense-form-container">
      <h3>Add Expense</h3>
      <form onSubmit={handleSubmit} className="expense-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="expense-date">Date:</label>
            <input
              id="expense-date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
              className="form-input"
            />
          </div>
          <div className="form-group">
            <label htmlFor="expense-head">Expense Head:</label>
            <select
              id="expense-head"
              value={head}
              onChange={(e) => setHead(e.target.value)}
              required
              className="form-input"
            >
              <option value="">Select head</option>
              {expenseHeads.map(h => (
                <option key={h.id} value={h.name}>{h.name}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="expense-amount">Amount:</label>
            <input
              id="expense-amount"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              min="0"
              step="0.01"
              required
              className="form-input"
              placeholder="0.00"
            />
          </div>
          <div className="form-group">
            <label htmlFor="expense-description">Description (optional):</label>
            <input
              id="expense-description"
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="form-input"
              placeholder="Add description"
            />
          </div>
        </div>
        <button type="submit" className="submit-btn">
          Add Expense
        </button>
      </form>
    </div>
  );
};

export default ExpenseForm;
