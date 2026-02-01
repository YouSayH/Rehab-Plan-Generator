import React from 'react';
import { Settings, FileText, Database } from 'lucide-react';
import { usePlanContext } from './PlanContext';

const LeftPanel: React.FC = () => {
  const { selectedPatientId, setSelectedPatientId } = usePlanContext();

  const patients = [
    { id: 'hash_001', name: '田中 太郎 (82)', status: '脳梗塞・右片麻痺' },
    { id: 'hash_002', name: '鈴木 花子 (75)', status: '大腿骨頚部骨折' },
  ];

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', padding: '16px', overflowY: 'auto', backgroundColor: '#f8f9fa' }}>
      <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Database size={20} />
        Input & Context
      </h2>

      <section style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '0.9rem', color: '#666', marginBottom: '8px' }}>担当患者選択</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {patients.map(p => (
            <button
              key={p.id}
              onClick={() => setSelectedPatientId(p.id)}
              style={{
                padding: '10px',
                border: selectedPatientId === p.id ? '2px solid #3b82f6' : '1px solid #ddd',
                borderRadius: '8px',
                backgroundColor: 'white',
                textAlign: 'left',
                cursor: 'pointer'
              }}
            >
              <div style={{ fontWeight: 'bold' }}>{p.name}</div>
              <div style={{ fontSize: '0.8rem', color: '#555' }}>{p.status}</div>
            </button>
          ))}
        </div>
      </section>

      <section style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '0.9rem', color: '#666', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Settings size={14} /> マッピング設定
        </h3>
        <div style={{ padding: '12px', backgroundColor: 'white', borderRadius: '8px', border: '1px solid #ddd', fontSize: '0.85rem' }}>
          <div>出力先シート: <strong>様式23_v1</strong></div>
          <div style={{ marginTop: '4px', color: '#3b82f6', cursor: 'pointer' }}>設定を変更...</div>
        </div>
      </section>

      <section>
        <h3 style={{ fontSize: '0.9rem', color: '#666', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <FileText size={14} /> 参照ソース (RAG)
        </h3>
        <ul style={{ listStyle: 'none', padding: 0, fontSize: '0.85rem' }}>
          <li style={{ padding: '8px', borderBottom: '1px solid #eee' }}>📄 類似症例: hash_092 (85%一致)</li>
          <li style={{ padding: '8px', borderBottom: '1px solid #eee' }}>📘 ガイドライン: 脳卒中治療2021</li>
        </ul>
      </section>
    </div>
  );
};

export default LeftPanel;