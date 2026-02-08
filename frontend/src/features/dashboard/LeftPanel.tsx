// frontend/src/features/dashboard/LeftPanel.tsx
import React, { useEffect, useState } from 'react';
import { usePlanContext } from './PlanContext';
import { ApiClient } from '../../api/client';
import { AdlItem } from '../../api/types';

const LeftPanel: React.FC = () => {
  const { 
    patientData, setPatientData, registerPatientName, 
    currentHashId, setCurrentHashId, patientList 
  } = usePlanContext();
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // currentHashId が変更されたらデータを取得する
  useEffect(() => {
    const fetchData = async () => {
      // IDが未選択の場合は何もしない
      if (!currentHashId) return;

      setIsLoading(true);
      setError(null);
      
      try {
        console.log(`Fetching data for: ${currentHashId}`);
        const data = await ApiClient.getLatestState(currentHashId);
        setPatientData(data);

        // =================================================================
        // [Privacy Protection] 実名の登録
        // =================================================================
        if (data.basic && data.basic.name) {
          registerPatientName(currentHashId, data.basic.name);
        }

      } catch (err) {
        console.error(err);
        setError('患者データの取得に失敗しました');
        setPatientData(null); // エラー時はクリア
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [currentHashId, setPatientData, registerPatientName]); // dependencyを currentHashId に変更

  // ハンドラー: ドロップダウン変更
  const handlePatientSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCurrentHashId(e.target.value);
  };

  const handleFimChange = (
    category: 'adl', 
    itemKey: string, 
    value: string
  ) => {
    if (!patientData) return;

    const numValue = parseInt(value, 10);
    if (isNaN(numValue)) return;

    const newData = JSON.parse(JSON.stringify(patientData));
    
    // 安全にデータへアクセスして書き換え
    if (newData[category] && newData[category][itemKey]) {
      newData[category][itemKey].fim_current = numValue;
      setPatientData(newData);
    }
  };

  // ADL項目の日本語ラベル定義
  const labelMap: Record<string, string> = {
    eating: '食事',
    grooming: '整容',
    bathing: '入浴',
    dressing_upper: '更衣(上)',
    dressing_lower: '更衣(下)',
    toileting: 'トイレ動作',
    transfer_bed: '移乗(B)',
    transfer_toilet: '移乗(T)',
    transfer_tub: '移乗(Y)',
    locomotion_walk: '移動(歩行)',
    locomotion_stairs: '移動(階段)',
    comprehension: '理解',
    expression: '表出',
    social: '社会的交流',
    problem_solving: '問題解決',
    memory: '記憶'
  };

  return (
    <div style={{ padding: '16px', height: '100%', overflowY: 'auto', backgroundColor: '#f8fafc', borderRight: '1px solid #e2e8f0' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '12px', color: '#333' }}>
        患者選択 (Select)
      </h3>
      
      <div style={{ marginBottom: '16px' }}>
        <select 
          value={currentHashId || ''} 
          onChange={handlePatientSelect}
          style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #cbd5e1' }}
        >
          <option value="" disabled>担当患者を選択してください</option>
          {patientList.map(p => (
            <option key={p.hash_id} value={p.hash_id}>
              {p.name ? p.name : p.hash_id} ({p.diagnosis_code || '診断名なし'})
            </option>
          ))}
        </select>
      </div>

      <hr style={{ border: 'none', borderTop: '1px solid #e2e8f0', margin: '16px 0' }} />

      <h3 style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '12px', color: '#333' }}>
        患者情報 (Input)
      </h3>

      {/* ローディング・エラー表示 */}
      {isLoading && <div style={{ padding: 10, color: '#666' }}>データを読み込んでいます...</div>}
      {error && <div style={{ padding: 10, color: 'red' }}>{error}</div>}
      
      {/* データがない場合のメッセージ (ロード中でなければ) */}
      {!isLoading && !patientData && !error && (
        <div style={{ padding: 10, color: '#94a3b8' }}>患者を選択してください</div>
      )}

      {/* データがある場合のみ詳細を表示 */}
      {!isLoading && patientData && (
        <>
          {/* 基本情報カード */}
          <div style={{ marginBottom: '16px', padding: '12px', background: 'white', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
            <p style={{ margin: '4px 0' }}><strong>氏名:</strong> {patientData.basic.name}</p>
            <p style={{ margin: '4px 0' }}><strong>年齢:</strong> {patientData.basic.age}歳 ({patientData.basic.gender})</p>
            <p style={{ margin: '4px 0' }}><strong>疾患:</strong> {patientData.basic.disease_name}</p>
            <div style={{ marginTop: '8px', fontSize: '0.8rem', color: '#64748b', background: '#f1f5f9', padding: '4px 8px', borderRadius: '4px' }}>
                💡 数値を変更して「生成」を押すと、結果に反映されます
            </div>
          </div>

          {/* FIM入力フォーム */}
          <h4 style={{ fontSize: '0.9rem', fontWeight: 'bold', marginBottom: '8px', color: '#475569', marginTop: '20px' }}>
            ADL評価 (FIM現在値)
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Object.entries(labelMap).map(([key, label]) => {
              const item = (patientData.adl as any)[key];
              
              if (!item || typeof item !== 'object') return null;

              const adlItem = item as AdlItem;
              
              return (
                <div key={key} style={{ 
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  background: 'white', padding: '8px 12px', borderRadius: '6px', border: '1px solid #e2e8f0'
                }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: '500' }}>{label}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <input 
                      type="number" 
                      min="1" max="7"
                      value={adlItem.fim_current ?? ''}
                      onChange={(e) => handleFimChange('adl', key, e.target.value)}
                      style={{ 
                        width: '40px', padding: '4px', borderRadius: '4px', border: '1px solid #cbd5e1',
                        textAlign: 'center', fontWeight: 'bold', color: '#2563eb', outline: 'none'
                      }}
                    />
                    <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>点</span>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};

export default LeftPanel;