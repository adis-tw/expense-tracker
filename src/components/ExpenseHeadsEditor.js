import React, { useState } from 'react';
import './ExpenseHeadsEditor.css';

const ExpenseHeadsEditor = ({ expenseHeads, onHeadsChange }) => {
  const [newHead, setNewHead] = useState('');

  const handleAddHead = () => {
    if (newHead.trim() && !expenseHeads.find(h => h.name === newHead.trim())) {
      onHeadsChange([...expenseHeads, { name: newHead.trim(), id: Date.now().toString() }]);
      setNewHead('');
    }
  };

  const handleDeleteHead = (id) => {
    onHeadsChange(expenseHeads.filter(h => h.id !== id));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAddHead();
    }
  };

  return (
    <div className="expense-heads-editor">
      <h3>Expense Heads</h3>
      <div className="heads-list">
        {expenseHeads.map(head => (
          <div key={head.id} className="head-item">
            <span>{head.name}</span>
            <button
              onClick={() => handleDeleteHead(head.id)}
              className="delete-btn"
              title="Delete expense head"
            >
              ×
            </button>
          </div>
        ))}
      </div>
      <div className="add-head-form">
        <input
          type="text"
          value={newHead}
          onChange={(e) => setNewHead(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Add new expense head"
          className="head-input"
        />
        <button onClick={handleAddHead} className="add-btn">
          Add
        </button>
      </div>
    </div>
  );
};

export default ExpenseHeadsEditor;
