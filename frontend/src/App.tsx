/**
 * File: frontend/src/App.tsx
 *
 * Summary:
 * アプリケーションのルートコンポーネント。
 * アプリ全体のUIを構成する `DashboardLayout` を呼び出し、それを状態管理コンテキストである `PlanProvider` でラップすることで、すべての子コンポーネントで共有ステート（患者情報や計画書データなど）を利用できるようにしています。
 *
 * Tags: Frontend, React, Root Component, Provider
 */

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