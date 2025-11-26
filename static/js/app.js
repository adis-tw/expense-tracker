let currentPeriodId = null;
let expenses = [];
let expenseHeads = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadTimePeriods();
    setupExpenseForm();
});

// Load all time periods
async function loadTimePeriods() {
    try {
        const response = await fetch('/api/time-periods');
        const periods = await response.json();
        displayPeriods(periods);
    } catch (error) {
        console.error('Error loading periods:', error);
    }
}

// Display time periods
function displayPeriods(periods) {
    const container = document.getElementById('periods-list');
    if (periods.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999;">No time periods yet. Create one to get started!</p>';
        return;
    }
    
    container.innerHTML = periods.map(period => `
        <div class="period-card ${period.id === currentPeriodId ? 'active' : ''}" 
             onclick="selectPeriod(${period.id})">
            <h3>${escapeHtml(period.name)}</h3>
            <p>${formatDate(period.start_date)} - ${formatDate(period.end_date)}</p>
        </div>
    `).join('');
}

// Select a time period
async function selectPeriod(periodId) {
    currentPeriodId = periodId;
    await loadPeriodDetails(periodId);
    loadTimePeriods(); // Refresh to show active state
}

// Load period details
async function loadPeriodDetails(periodId) {
    try {
        const [periodsResponse, headsResponse, expensesResponse] = await Promise.all([
            fetch('/api/time-periods'),
            fetch(`/api/time-periods/${periodId}/expense-heads`),
            fetch(`/api/time-periods/${periodId}/expenses`)
        ]);
        
        const periods = await periodsResponse.json();
        const period = periods.find(p => p.id === periodId);
        
        expenseHeads = await headsResponse.json();
        expenses = await expensesResponse.json();
        
        document.getElementById('period-name').textContent = period.name;
        document.getElementById('period-details').classList.remove('hidden');
        
        displayExpenseHeads();
        displayExpenses();
        updateExpenseHeadSelect();
    } catch (error) {
        console.error('Error loading period details:', error);
    }
}

// Display expense heads
function displayExpenseHeads() {
    const container = document.getElementById('expense-heads-list');
    if (expenseHeads.length === 0) {
        container.innerHTML = '<p style="color: #999;">No expense heads. Add one to start tracking expenses.</p>';
        return;
    }
    
    container.innerHTML = expenseHeads.map(head => `
        <div class="head-badge">
            <span>${escapeHtml(head.head_name)}</span>
            <button class="edit-btn" onclick="editHead(${head.id}, '${escapeHtml(head.head_name)}')" title="Edit">✏️</button>
            <button class="delete-btn" onclick="deleteHead(${head.id})" title="Delete">🗑️</button>
        </div>
    `).join('');
}

// Display expenses
function displayExpenses() {
    const tbody = document.getElementById('expenses-tbody');
    if (expenses.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">No expenses yet.</td></tr>';
        return;
    }
    
    const total = expenses.reduce((sum, exp) => sum + parseFloat(exp.amount), 0);
    
    tbody.innerHTML = expenses.map(exp => `
        <tr>
            <td>${formatDate(exp.expense_date)}</td>
            <td>${escapeHtml(exp.head_name)}</td>
            <td>₹${parseFloat(exp.amount).toFixed(2)}</td>
            <td>${escapeHtml(exp.description || '-')}</td>
            <td class="expense-actions">
                <button class="btn btn-sm btn-secondary" onclick="editExpense(${exp.id})">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteExpense(${exp.id})">Delete</button>
            </td>
        </tr>
    `).join('') + `
        <tr style="background: #f8f9fa; font-weight: bold;">
            <td colspan="2">Total</td>
            <td>₹${total.toFixed(2)}</td>
            <td colspan="2"></td>
        </tr>
    `;
}

// Update expense head select dropdown
function updateExpenseHeadSelect() {
    const select = document.getElementById('expense-head-select');
    select.innerHTML = '<option value="">Select Expense Head</option>' +
        expenseHeads.map(head => 
            `<option value="${head.id}">${escapeHtml(head.head_name)}</option>`
        ).join('');
}

// Setup expense form
function setupExpenseForm() {
    const form = document.getElementById('expense-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!currentPeriodId) {
            alert('Please select a time period first');
            return;
        }
        
        const data = {
            expense_head_id: parseInt(document.getElementById('expense-head-select').value),
            amount: parseFloat(document.getElementById('expense-amount').value),
            description: document.getElementById('expense-description').value,
            expense_date: document.getElementById('expense-date').value
        };
        
        try {
            const response = await fetch(`/api/time-periods/${currentPeriodId}/expenses`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                form.reset();
                await loadPeriodDetails(currentPeriodId);
            } else {
                alert('Error adding expense');
            }
        } catch (error) {
            console.error('Error adding expense:', error);
            alert('Error adding expense');
        }
    });
}

// Show add period modal
function showAddPeriodModal() {
    document.getElementById('modal-title').textContent = 'Create New Time Period';
    document.getElementById('modal-body').innerHTML = `
        <input type="text" id="period-name-input" placeholder="Period Name (e.g., January 2024)" required>
        <input type="date" id="period-start-date" required>
        <input type="date" id="period-end-date" required>
        <button class="btn btn-primary" onclick="createPeriod()" style="width: 100%;">Create Period</button>
    `;
    document.getElementById('modal-overlay').classList.remove('hidden');
}

// Create period
async function createPeriod() {
    const name = document.getElementById('period-name-input').value;
    const startDate = document.getElementById('period-start-date').value;
    const endDate = document.getElementById('period-end-date').value;
    
    if (!name || !startDate || !endDate) {
        alert('Please fill all fields');
        return;
    }
    
    try {
        const response = await fetch('/api/time-periods', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, start_date: startDate, end_date: endDate })
        });
        
        if (response.ok) {
            closeModals();
            await loadTimePeriods();
        } else {
            alert('Error creating period');
        }
    } catch (error) {
        console.error('Error creating period:', error);
        alert('Error creating period');
    }
}

// Show add head modal
function showAddHeadModal() {
    if (!currentPeriodId) {
        alert('Please select a time period first');
        return;
    }
    
    document.getElementById('modal-title').textContent = 'Add Expense Head';
    document.getElementById('modal-body').innerHTML = `
        <input type="text" id="head-name-input" placeholder="Expense Head Name (e.g., Food, Transport)" required>
        <button class="btn btn-primary" onclick="createHead()" style="width: 100%;">Add Head</button>
    `;
    document.getElementById('modal-overlay').classList.remove('hidden');
}

// Create expense head
async function createHead() {
    const headName = document.getElementById('head-name-input').value;
    
    if (!headName) {
        alert('Please enter a head name');
        return;
    }
    
    try {
        const response = await fetch(`/api/time-periods/${currentPeriodId}/expense-heads`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ head_name: headName })
        });
        
        if (response.ok) {
            closeModals();
            await loadPeriodDetails(currentPeriodId);
        } else {
            alert('Error creating expense head');
        }
    } catch (error) {
        console.error('Error creating head:', error);
        alert('Error creating expense head');
    }
}

// Edit expense head
function editHead(headId, currentName) {
    document.getElementById('modal-title').textContent = 'Edit Expense Head';
    document.getElementById('modal-body').innerHTML = `
        <input type="text" id="head-name-input" value="${escapeHtml(currentName)}" required>
        <button class="btn btn-primary" onclick="updateHead(${headId})" style="width: 100%;">Update Head</button>
    `;
    document.getElementById('modal-overlay').classList.remove('hidden');
}

// Update expense head
async function updateHead(headId) {
    const headName = document.getElementById('head-name-input').value;
    
    if (!headName) {
        alert('Please enter a head name');
        return;
    }
    
    try {
        const response = await fetch(`/api/expense-heads/${headId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ head_name: headName })
        });
        
        if (response.ok) {
            closeModals();
            await loadPeriodDetails(currentPeriodId);
        } else {
            alert('Error updating expense head');
        }
    } catch (error) {
        console.error('Error updating head:', error);
        alert('Error updating expense head');
    }
}

// Delete expense head
async function deleteHead(headId) {
    if (!confirm('Are you sure you want to delete this expense head? All associated expenses will also be deleted.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/expense-heads/${headId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadPeriodDetails(currentPeriodId);
        } else {
            alert('Error deleting expense head');
        }
    } catch (error) {
        console.error('Error deleting head:', error);
        alert('Error deleting expense head');
    }
}

// Edit expense
function editExpense(expenseId) {
    const expense = expenses.find(e => e.id === expenseId);
    if (!expense) return;
    
    document.getElementById('modal-title').textContent = 'Edit Expense';
    document.getElementById('modal-body').innerHTML = `
        <select id="expense-head-select-modal" required>
            ${expenseHeads.map(head => 
                `<option value="${head.id}" ${head.id === expense.expense_head_id ? 'selected' : ''}>${escapeHtml(head.head_name)}</option>`
            ).join('')}
        </select>
        <input type="number" id="expense-amount-modal" step="0.01" value="${expense.amount}" required>
        <input type="text" id="expense-description-modal" value="${escapeHtml(expense.description || '')}" placeholder="Description (optional)">
        <input type="date" id="expense-date-modal" value="${expense.expense_date}" required>
        <button class="btn btn-primary" onclick="updateExpense(${expenseId})" style="width: 100%;">Update Expense</button>
    `;
    document.getElementById('modal-overlay').classList.remove('hidden');
}

// Update expense
async function updateExpense(expenseId) {
    const data = {
        expense_head_id: parseInt(document.getElementById('expense-head-select-modal').value),
        amount: parseFloat(document.getElementById('expense-amount-modal').value),
        description: document.getElementById('expense-description-modal').value,
        expense_date: document.getElementById('expense-date-modal').value
    };
    
    try {
        const response = await fetch(`/api/expenses/${expenseId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            closeModals();
            await loadPeriodDetails(currentPeriodId);
        } else {
            alert('Error updating expense');
        }
    } catch (error) {
        console.error('Error updating expense:', error);
        alert('Error updating expense');
    }
}

// Delete expense
async function deleteExpense(expenseId) {
    if (!confirm('Are you sure you want to delete this expense?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/expenses/${expenseId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadPeriodDetails(currentPeriodId);
        } else {
            alert('Error deleting expense');
        }
    } catch (error) {
        console.error('Error deleting expense:', error);
        alert('Error deleting expense');
    }
}

// Delete current period
async function deleteCurrentPeriod() {
    if (!confirm('Are you sure you want to delete this time period? All expenses and heads will be deleted.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/time-periods/${currentPeriodId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            currentPeriodId = null;
            document.getElementById('period-details').classList.add('hidden');
            await loadTimePeriods();
        } else {
            alert('Error deleting period');
        }
    } catch (error) {
        console.error('Error deleting period:', error);
        alert('Error deleting period');
    }
}

// Show analytics
async function showAnalytics() {
    if (!currentPeriodId) {
        alert('Please select a time period first');
        return;
    }
    
    try {
        const response = await fetch(`/api/time-periods/${currentPeriodId}/analytics`);
        const analytics = await response.json();
        
        displayAnalytics(analytics);
        document.getElementById('analytics-modal').classList.remove('hidden');
    } catch (error) {
        console.error('Error loading analytics:', error);
        alert('Error loading analytics');
    }
}

// Display analytics
function displayAnalytics(analytics) {
    const content = document.getElementById('analytics-content');
    
    content.innerHTML = `
        <div class="analytics-grid">
            <div class="analytics-card">
                <h4>Total Expenses</h4>
                <div class="value">₹${analytics.total.toFixed(2)}</div>
            </div>
            <div class="analytics-card">
                <h4>Average Daily</h4>
                <div class="value">₹${analytics.average_daily.toFixed(2)}</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h4>Expenses by Head</h4>
            <canvas id="headChart"></canvas>
        </div>
        
        <div class="chart-container">
            <h4>Daily Expenses Trend</h4>
            <canvas id="dailyChart"></canvas>
        </div>
    `;
    
    // Chart for expenses by head
    const headCtx = document.getElementById('headChart').getContext('2d');
    new Chart(headCtx, {
        type: 'doughnut',
        data: {
            labels: analytics.by_head.map(h => h.head_name),
            datasets: [{
                data: analytics.by_head.map(h => h.total),
                backgroundColor: [
                    '#667eea', '#764ba2', '#f093fb', '#4facfe',
                    '#43e97b', '#fa709a', '#fee140', '#30cfd0'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
    
    // Chart for daily expenses
    const dailyCtx = document.getElementById('dailyChart').getContext('2d');
    new Chart(dailyCtx, {
        type: 'line',
        data: {
            labels: analytics.daily.map(d => formatDate(d.expense_date)),
            datasets: [{
                label: 'Daily Expenses',
                data: analytics.daily.map(d => d.total),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Close analytics
function closeAnalytics() {
    document.getElementById('analytics-modal').classList.add('hidden');
}

// Export to Google Sheets
async function exportToSheets() {
    if (!currentPeriodId) {
        alert('Please select a time period first');
        return;
    }
    
    if (!confirm('This will export your expenses to Google Sheets. Make sure you have set up Google Sheets credentials.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/time-periods/${currentPeriodId}/export`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`Successfully exported to Google Sheets!\n\nSheet URL: ${result.url || 'Check your Google Drive'}`);
        } else {
            alert(`Export failed: ${result.message}`);
        }
    } catch (error) {
        console.error('Error exporting:', error);
        alert('Error exporting to Google Sheets. Please check the setup instructions.');
    }
}

// Close modals
function closeModals() {
    document.getElementById('modal-overlay').classList.add('hidden');
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
