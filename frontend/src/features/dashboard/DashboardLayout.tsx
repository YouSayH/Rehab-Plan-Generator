import React, { Suspense, useState, useCallback, useEffect } from 'react';
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
  // パネル幅のState (初期値)
  const [leftWidth, setLeftWidth] = useState(300);
  const [rightWidth, setRightWidth] = useState(350);

  // ドラッグ中かどうかのフラグ
  const [isDraggingLeft, setIsDraggingLeft] = useState(false);
  const [isDraggingRight, setIsDraggingRight] = useState(false);

  // ドラッグ開始
  const startResizeLeft = useCallback(() => setIsDraggingLeft(true), []);
  const startResizeRight = useCallback(() => setIsDraggingRight(true), []);

  // マウスイベント処理 (Global)
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDraggingLeft) {
        // 左パネルの幅 = マウスのX座標 (最小200px, 最大600pxで制限)
        const newWidth = Math.max(200, Math.min(e.clientX, 600));
        setLeftWidth(newWidth);
      }
      if (isDraggingRight) {
        // 右パネルの幅 = 画面幅 - マウスのX座標 (最小250px, 最大800pxで制限)
        const newWidth = Math.max(250, Math.min(window.innerWidth - e.clientX, 800));
        setRightWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsDraggingLeft(false);
      setIsDraggingRight(false);
      // カーソルと選択状態をリセット
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };

    // ドラッグ中のみイベントリスナーを登録
    if (isDraggingLeft || isDraggingRight) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      
      // ドラッグ中のUX改善
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none'; // テキスト選択防止
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDraggingLeft, isDraggingRight]);

  // リサイザーのスタイル (共通)
  const resizerStyle: React.CSSProperties = {
    position: 'absolute',
    top: 0,
    bottom: 0,
    width: '6px',
    cursor: 'col-resize',
    zIndex: 10,
    // 透明だがホバー時に少し色を付けるなどの装飾が可能
    backgroundColor: 'transparent', 
    transition: 'background-color 0.2s',
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      
      {/* 左カラム */}
      <div style={{ width: `${leftWidth}px`, flexShrink: 0, borderRight: '1px solid #ddd', position: 'relative' }}>
        <LeftPanel />
        
        {/* 左リサイザー (右端に配置) */}
        <div 
          onMouseDown={startResizeLeft}
          style={{ ...resizerStyle, right: '-3px' }}
          className="hover-resizer" // CSSでホバー色をつける場合用
        />
      </div>

      {/* 中央カラム (スプレッドシート) */}
      <div style={{ flex: 1, minWidth: 0, overflow: 'hidden', position: 'relative' }}>
        <Suspense fallback={<SheetLoading />}>
          <UniverSheet />
        </Suspense>
      </div>

      {/* 右カラム */}
      <div style={{ width: `${rightWidth}px`, flexShrink: 0, borderLeft: '1px solid #ddd', position: 'relative' }}>
        
        {/* 右リサイザー (左端に配置) */}
        <div 
          onMouseDown={startResizeRight}
          style={{ ...resizerStyle, left: '-3px' }}
          className="hover-resizer"
        />
        
        <RightPanel />
      </div>

      {/* ホバー時のスタイル定義 (インラインで簡易的に挿入) */}
      <style>{`
        .hover-resizer:hover, .hover-resizer:active {
          background-color: rgba(79, 70, 229, 0.3) !important; /* 薄い青色 */
        }
      `}</style>
    </div>
  );
};

export default DashboardLayout;