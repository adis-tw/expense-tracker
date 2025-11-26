const STORAGE_KEY = 'expenseTrackerData';

export const loadData = () => {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : { timePeriods: [] };
  } catch (error) {
    console.error('Error loading data:', error);
    return { timePeriods: [] };
  }
};

export const saveData = (data) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (error) {
    console.error('Error saving data:', error);
  }
};
