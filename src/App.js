import React, { useState, useEffect } from 'react';
import { format, parseISO, isWithinInterval } from 'date-fns';
import DateRangeSelector from './components/DateRangeSelector';
import ExpenseHeadsEditor from './components/ExpenseHeadsEditor';
import ExpenseForm from './components/ExpenseForm';
import ExpenseList from './components/ExpenseList';
import Analytics from './components/Analytics';
import { loadData, saveData } from './utils/storage';
import { exportToGoogleSheets } from './utils/googleSheets';
import './App.css';

function App() {
  const [timePeriods, setTimePeriods] = useState([]);
  const [currentPeriodIndex, setCurrentPeriodIndex] = useState(-1);
  const [startDate, setStartDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [endDate, setEndDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [expenseHeads, setExpenseHeads] = useState([
    { id: '1', name: 'Food' },
    { id: '2', name: 'Transport' },
    { id: '3', name: 'Utilities' },
    { id: '4', name: 'Entertainment' }
  ]);
  const [expenses, setExpenses] = useState([]);

  useEffect(() => {
    const data = loadData();
    if (data.timePeriods && data.timePeriods.length > 0) {
      setTimePeriods(data.timePeriods);
      setCurrentPeriodIndex(0);
      loadPeriodData(data.timePeriods[0]);
    }
  }, []);

  useEffect(() => {
    if (timePeriods.length > 0) {
      saveData({ timePeriods });
    }
  }, [timePeriods]);

  const loadPeriodData = (period) => {
    if (period) {
      setStartDate(period.startDate);
      setEndDate(period.endDate);
      setExpenseHeads(period.expenseHeads || []);
      setExpenses(period.expenses || []);
    }
  };

  const createNewPeriod = () => {
    const newPeriod = {
      id: Date.now().toString(),
      startDate,
      endDate,
      expenseHeads: [...expenseHeads],
      expenses: []
    };
    const updatedPeriods = [...timePeriods, newPeriod];
    setTimePeriods(updatedPeriods);
    setCurrentPeriodIndex(updatedPeriods.length - 1);
    setExpenses([]);
  };

  const updateCurrentPeriod = () => {
    if (currentPeriodIndex >= 0 && currentPeriodIndex < timePeriods.length) {
      const updatedPeriods = [...timePeriods];
      updatedPeriods[currentPeriodIndex] = {
        ...updatedPeriods[currentPeriodIndex],
        startDate,
        endDate,
        expenseHeads: [...expenseHeads],
        expenses: [...expenses]
      };
      setTimePeriods(updatedPeriods);
    }
  };

  const handleStartDateChange = (date) => {
    setStartDate(date);
    if (currentPeriodIndex >= 0) {
      updateCurrentPeriod();
    }
  };

  const handleEndDateChange = (date) => {
    setEndDate(date);
    if (currentPeriodIndex >= 0) {
      updateCurrentPeriod();
    }
  };

  const handleHeadsChange = (newHeads) => {
    setExpenseHeads(newHeads);
    if (currentPeriodIndex >= 0) {
      const updatedPeriods = [...timePeriods];
      updatedPeriods[currentPeriodIndex].expenseHeads = newHeads;
      setTimePeriods(updatedPeriods);
    }
  };

  const handleAddExpense = (expense) => {
    const expenseDate = parseISO(expense.date);
    const periodStart = parseISO(startDate);
    const periodEnd = parseISO(endDate);

    if (!isWithinInterval(expenseDate, { start: periodStart, end: periodEnd })) {
      alert('Expense date must be within the selected date range!');
      return;
    }

    const newExpenses = [...expenses, expense];
    setExpenses(newExpenses);
    
    if (currentPeriodIndex >= 0) {
      const updatedPeriods = [...timePeriods];
      updatedPeriods[currentPeriodIndex].expenses = newExpenses;
      setTimePeriods(updatedPeriods);
    }
  };

  const handleDeleteExpense = (id) => {
    const newExpenses = expenses.filter(e => e.id !== id);
    setExpenses(newExpenses);
    
    if (currentPeriodIndex >= 0) {
      const updatedPeriods = [...timePeriods];
      updatedPeriods[currentPeriodIndex].expenses = newExpenses;
      setTimePeriods(updatedPeriods);
    }
  };

  const handleSelectPeriod = (index) => {
    setCurrentPeriodIndex(index);
    loadPeriodData(timePeriods[index]);
  };

  const handleExport = () => {
    if (currentPeriodIndex >= 0) {
      const currentPeriod = timePeriods[currentPeriodIndex];
      exportToGoogleSheets(currentPeriod, expenses, expenseHeads);
    } else {
      const tempPeriod = {
        startDate,
        endDate,
        expenseHeads,
        expenses
      };
      exportToGoogleSheets(tempPeriod, expenses, expenseHeads);
    }
  };

  const handleSavePeriod = () => {
    if (currentPeriodIndex >= 0) {
      updateCurrentPeriod();
      alert('Period updated successfully!');
    } else {
      createNewPeriod();
      alert('New period created successfully!');
    }
  };

  return (
    <div className="App">
      <div className="app-container">
        <header className="app-header">
          <h1>💰 Monthly Expense Tracker</h1>
          <p className="subtitle">Track your expenses with custom date ranges and analytics</p>
        </header>

        <div className="period-selector">
          <h3>Time Periods</h3>
          <div className="period-buttons">
            {timePeriods.map((period, index) => (
              <button
                key={period.id}
                onClick={() => handleSelectPeriod(index)}
                className={`period-btn ${currentPeriodIndex === index ? 'active' : ''}`}
              >
                {format(parseISO(period.startDate), 'MMM dd')} - {format(parseISO(period.endDate), 'MMM dd, yyyy')}
              </button>
            ))}
            <button
              onClick={() => {
                setCurrentPeriodIndex(-1);
                setStartDate(format(new Date(), 'yyyy-MM-dd'));
                setEndDate(format(new Date(), 'yyyy-MM-dd'));
                setExpenseHeads([
                  { id: '1', name: 'Food' },
                  { id: '2', name: 'Transport' },
                  { id: '3', name: 'Utilities' },
                  { id: '4', name: 'Entertainment' }
                ]);
                setExpenses([]);
              }}
              className="period-btn new-period-btn"
            >
              + New Period
            </button>
          </div>
        </div>

        <div className="main-content">
          <div className="left-panel">
            <DateRangeSelector
              startDate={startDate}
              endDate={endDate}
              onStartDateChange={handleStartDateChange}
              onEndDateChange={handleEndDateChange}
            />

            <ExpenseHeadsEditor
              expenseHeads={expenseHeads}
              onHeadsChange={handleHeadsChange}
            />

            <ExpenseForm
              expenseHeads={expenseHeads}
              onAddExpense={handleAddExpense}
            />

            <div className="action-buttons">
              <button onClick={handleSavePeriod} className="save-btn">
                {currentPeriodIndex >= 0 ? 'Update Period' : 'Save Period'}
              </button>
              <button onClick={handleExport} className="export-btn">
                Export to Google Sheets
              </button>
            </div>
          </div>

          <div className="right-panel">
            <ExpenseList
              expenses={expenses}
              expenseHeads={expenseHeads}
              onDeleteExpense={handleDeleteExpense}
            />

            <Analytics
              expenses={expenses}
              expenseHeads={expenseHeads}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
