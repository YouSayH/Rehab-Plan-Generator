// frontend/src/features/dashboard/RightPanel.tsx
import React from 'react';
import { Sparkles, MessageSquare, Play, Edit3, Loader2 } from 'lucide-react';
import { usePlanContext } from './PlanContext';
import { ApiClient } from '../../api/client';
import { PatientExtractionData } from '../../api/types';

const RightPanel: React.FC = () => {
  const { setCurrentPlan, isGenerating, setIsGenerating } = usePlanContext();

  // Backendの PatientExtractionSchema (Pydantic) に準拠した構造にする
  const DUMMY_PATIENT: PatientExtractionData = {
  basic: {
      age: 82,
      gender: '男',
      disease_name: '脳梗塞 (右片麻痺)', 
      onset_date: '2026-04-01',
    },
    medical: {
      comorbidities: '高血圧症',
      risks: '転倒リスクあり',
    },
    function: {
      paralysis: true,
      jcs_gcs: 'I-1',
    },
    basic_movement: {
      rolling_level: 'independent',
    },
    adl: {
      // ADLスキーマはネストが深いので、必須フィールドがない場合は空オブジェクトでも通る場合が多いですが
      // エラーが出る場合はここに中身を追加します
      eating: { fim_current: 5 },
      transfer_bed: { fim_current: 4 },
      toileting: { fim_current: 4 },
    },
    nutrition: {},
    social: {},
    goals: {
      short_term_goal: 'トイレ動作の見守りレベル',
      long_term_goal: '自宅復帰',
    },
    signature: {}
  };

  const handleGenerate = async (cardTitle: string) => {
    setIsGenerating(true);
    try {
      // API呼び出し
      const newPlan = await ApiClient.generatePlan('patient_001', DUMMY_PATIENT);
      
      setCurrentPlan(newPlan);
      alert(`「${cardTitle}」の生成が完了しました！`);
    } catch (error) {
      console.error('Generation failed:', error);
      alert('生成に失敗しました。コンソールログを確認してください。');
    } finally {
      setIsGenerating(false);
    }
  };

  const generatorCards = [
    { id: 1, title: '現状評価（リスク・禁忌）', status: 'ready', desc: 'バイタル、リスク管理、痛みの状態を生成' },
    { id: 2, title: '目標設定（短期・長期）', status: 'ready', desc: 'FIM予測に基づいたSMARTゴールを設定' },
    { id: 3, title: '治療プログラム', status: 'pending', desc: '具体的な訓練内容と頻度を提案' },
  ];

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#f0f4f8', borderLeft: '1px solid #ddd' }}>
      <div style={{ padding: '16px', backgroundColor: 'white', borderBottom: '1px solid #eee' }}>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px', color: '#4f46e5' }}>
          <Sparkles size={20} /> AI Co-Editor
        </h2>
        <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '4px' }}>
          各カードを実行して計画書を作成します
        </p>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {generatorCards.map(card => (
          <div key={card.id} style={{ 
            backgroundColor: 'white', 
            borderRadius: '12px', 
            padding: '16px', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
            border: '1px solid #e5e7eb'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
              <h3 style={{ fontWeight: 'bold', fontSize: '0.95rem' }}>{card.title}</h3>
              <span style={{ 
                fontSize: '0.7rem', 
                padding: '2px 8px', 
                borderRadius: '10px', 
                backgroundColor: card.status === 'ready' ? '#dbeafe' : '#f3f4f6',
                color: card.status === 'ready' ? '#1e40af' : '#6b7280'
              }}>
                {card.status === 'ready' ? '準備OK' : '待機中'}
              </span>
            </div>
            
            <p style={{ fontSize: '0.8rem', color: '#666', marginBottom: '12px' }}>{card.desc}</p>
            
            <div style={{ display: 'flex', gap: '8px' }}>
              <button 
                onClick={() => handleGenerate(card.title)}
                disabled={isGenerating || card.status !== 'ready'}
                style={{ 
                  flex: 1, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  gap: '4px',
                  padding: '8px', 
                  backgroundColor: isGenerating ? '#a5b4fc' : '#4f46e5', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '6px',
                  cursor: isGenerating || card.status !== 'ready' ? 'not-allowed' : 'pointer',
                  fontSize: '0.85rem'
                }}
              >
                {isGenerating ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />} 
                {isGenerating ? '生成中...' : '生成'}
              </button>
              <button style={{ 
                padding: '8px', 
                backgroundColor: 'white', 
                border: '1px solid #ddd', 
                borderRadius: '6px',
                cursor: 'pointer' 
              }}>
                <Edit3 size={14} color="#666" />
              </button>
            </div>
          </div>
        ))}
      </div>

      <div style={{ padding: '12px', backgroundColor: 'white', borderTop: '1px solid #ddd' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', border: '1px solid #ddd', borderRadius: '20px', padding: '8px 12px' }}>
          <MessageSquare size={18} color="#999" />
          <input 
            type="text" 
            placeholder="AIに修正指示を出す..." 
            style={{ border: 'none', outline: 'none', flex: 1, fontSize: '0.9rem' }}
          />
        </div>
      </div>
    </div>
  );
};

export default RightPanel;