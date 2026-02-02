// frontend/src/features/dashboard/DashboardLayout.tsx
import React, { Suspense } from 'react'; // Suspenseを追加
import LeftPanel from './LeftPanel';
import RightPanel from './RightPanel';

// 遅延ロード
const UniverSheet = React.lazy(() => import('./UniverSheet'));

// ローディング中の表示コンポーネント
const SheetLoading = () => (
  <div style={{ 
    height: '100%', 
    display: 'flex', 
    flexDirection: 'column',
    alignItems: 'center', 
    justifyContent: 'center',
    backgroundColor: '#f5f5f5',
    color: '#666',
    gap: '12px'
  }}>
    <div style={{
      width: '24px',
      height: '24px',
      border: '3px solid #ddd',
      borderTopColor: '#4f46e5',
      borderRadius: '50%',
      animation: 'spin 1s linear infinite'
    }} />
    <span style={{ fontSize: '0.9rem' }}>スプレッドシートを準備中...</span>
    <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
  </div>
);

const DashboardLayout: React.FC = () => {
  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* 左カラム: 固定幅 */}
      <div style={{ width: '300px', flexShrink: 0, borderRight: '1px solid #ddd' }}>
        <LeftPanel />
      </div>

      {/* 中央カラム: スプレッドシート */}
      <div style={{ flex: 1, minWidth: 0, overflow: 'hidden', position: 'relative' }}>
        {/* 修正2: Suspenseでラップして非同期読み込みを待機 */}
        <Suspense fallback={<SheetLoading />}>
          <UniverSheet />
        </Suspense>
      </div>

      {/* 右カラム: 固定幅 */}
      <div style={{ width: '350px', flexShrink: 0, borderLeft: '1px solid #ddd' }}>
        <RightPanel />
      </div>
    </div>
  );
};

export default DashboardLayout;