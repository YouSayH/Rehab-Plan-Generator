// frontend/src/features/dashboard/LeftPanel.tsx (未作成の場合のみ)
import React from 'react';

const LeftPanel: React.FC = () => {
  return (
    <div style={{ padding: '16px', height: '100%', overflowY: 'auto' }}>
      <h3>患者情報</h3>
      <div style={{ marginBottom: '16px', padding: '10px', background: '#f9f9f9', borderRadius: '4px' }}>
        <p><strong>ID:</strong> P001</p>
        <p><strong>氏名:</strong> 田中 太郎</p>
        <p><strong>年齢:</strong> 75歳 (男性)</p>
      </div>
      <hr />
      <p style={{ fontSize: '0.8rem', color: '#666' }}>
        ここにFIM推移グラフや<br />類似症例リストが表示されます。
      </p>
    </div>
  );
};

export default LeftPanel;