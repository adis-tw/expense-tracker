export const calculateAnalytics = (expenses, expenseHeads) => {
  if (!expenses || expenses.length === 0) {
    return {
      total: 0,
      byHead: {},
      percentages: {},
      average: 0,
      count: 0
    };
  }

  const total = expenses.reduce((sum, expense) => sum + parseFloat(expense.amount || 0), 0);
  const byHead = {};
  const percentages = {};

  expenseHeads.forEach(head => {
    const headExpenses = expenses.filter(e => e.head === head.name);
    const headTotal = headExpenses.reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
    byHead[head.name] = {
      total: headTotal,
      count: headExpenses.length,
      percentage: total > 0 ? (headTotal / total) * 100 : 0
    };
    percentages[head.name] = total > 0 ? (headTotal / total) * 100 : 0;
  });

  return {
    total,
    byHead,
    percentages,
    average: expenses.length > 0 ? total / expenses.length : 0,
    count: expenses.length
  };
};
