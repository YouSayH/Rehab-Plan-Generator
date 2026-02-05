import React, { useEffect, useState } from 'react';
import { usePlanContext } from './PlanContext';
import { ApiClient } from '../../api/client';
import { AdlItem } from '../../api/types';

const LeftPanel: React.FC = () => {
  const { patientData, setPatientData, registerPatientName } = usePlanContext();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      // 既にデータがある場合は再取得しない（必要に応じて変更）
      if (patientData) return;
      
      setIsLoading(true);
      try {
        // TODO: 本来はURLパラメータ等からIDを取得すべきだが、現在は固定
        const currentHashId = 'patient_001';

        const data = await ApiClient.getLatestState(currentHashId);
        setPatientData(data);

        // =================================================================
        // [Privacy Protection] 実名の登録
        // 取得したデータに含まれる実名を、ハッシュIDと紐付けてブラウザに保存する。
        // これにより、生成後の計画書(実名なし)を表示する際に名前を復元できる。
        // =================================================================
        if (data.basic && data.basic.name) {
          registerPatientName(currentHashId, data.basic.name);
        }

      } catch (err) {
        console.error(err);
        setError('患者データの取得に失敗しました');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [patientData, setPatientData, registerPatientName]);

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

  if (isLoading) return <div style={{ padding: 20 }}>データを読み込んでいます...</div>;
  if (error) return <div style={{ padding: 20, color: 'red' }}>{error}</div>;
  if (!patientData) return <div style={{ padding: 20 }}>データがありません</div>;

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
        患者情報 (Input)
      </h3>
      
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
    </div>
  );
};

export default LeftPanel;