// Google Sheets Export Utility
// Note: This requires Google Sheets API setup. For now, we'll export as CSV
// which can be imported into Google Sheets

import { calculateAnalytics } from './analytics';

export const exportToCSV = (timePeriod, expenses, expenseHeads) => {
  const headers = ['Date', 'Expense Head', 'Amount', 'Description'];
  const rows = expenses.map(expense => [
    expense.date,
    expense.head,
    expense.amount,
    expense.description || ''
  ]);

  const csvContent = [
    `Time Period: ${timePeriod.startDate} to ${timePeriod.endDate}`,
    '',
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');

  // Add analytics summary
  const analytics = calculateAnalytics(expenses, expenseHeads);
  const summary = [
    '',
    'Summary',
    `Total Expenses,${analytics.total}`,
    `Number of Expenses,${analytics.count}`,
    `Average Expense,${analytics.average.toFixed(2)}`,
    '',
    'By Expense Head',
    ...Object.entries(analytics.byHead).map(([head, data]) => 
      `${head},${data.total},${data.percentage.toFixed(2)}%`
    )
  ].join('\n');

  const fullContent = csvContent + '\n' + summary;

  // Create download link
  const blob = new Blob([fullContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', `expenses_${timePeriod.startDate}_to_${timePeriod.endDate}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// For actual Google Sheets API integration, you would need:
// 1. Google API credentials
// 2. OAuth setup
// 3. Google Sheets API calls
// This is a placeholder for future implementation
export const exportToGoogleSheets = async (timePeriod, expenses, expenseHeads) => {
  // For now, we'll use CSV export which can be imported to Google Sheets
  // In production, you would implement actual Google Sheets API integration
  exportToCSV(timePeriod, expenses, expenseHeads);
  
  // TODO: Implement actual Google Sheets API integration
  // This would require:
  // - Google API client library setup
  // - OAuth authentication
  // - Creating/updating Google Sheets
};
