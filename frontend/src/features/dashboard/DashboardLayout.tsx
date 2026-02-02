// frontend/src/features/dashboard/DashboardLayout.tsx
import React from 'react';
import LeftPanel from './LeftPanel';   // 既存の左パネル
import RightPanel from './RightPanel'; // 今回作成した右パネル
import UniverSheet from './UniverSheet'; // 中央のUniver

const DashboardLayout: React.FC = () => {
  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* 左カラム: 固定幅 (例: 300px) */}
      <div style={{ width: '300px', flexShrink: 0, borderRight: '1px solid #ddd' }}>
        <LeftPanel />
      </div>

      {/* 中央カラム: 残りの幅を埋める (flex: 1) */}
      <div style={{ flex: 1, minWidth: 0, overflow: 'hidden' }}>
        <UniverSheet />
      </div>

      {/* 右カラム: 固定幅 (例: 350px) */}
      <div style={{ width: '350px', flexShrink: 0, borderLeft: '1px solid #ddd' }}>
        <RightPanel />
      </div>
    </div>
  );
};

export default DashboardLayout;