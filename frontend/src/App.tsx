// frontend/src/App.tsx
import React from 'react';
import DashboardLayout from './features/dashboard/DashboardLayout';
import { PlanProvider } from './features/dashboard/PlanContext';
import './index.css'; // Tailwind等のスタイルがある場合

function App() {
  return (
    <PlanProvider>
      <div className="App">
        <DashboardLayout />
      </div>
    </PlanProvider>
  );
}

export default App;