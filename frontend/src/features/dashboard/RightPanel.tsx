import React from 'react';
import { Sparkles, MessageSquare, Play, Edit3, Loader2 } from 'lucide-react';
import { usePlanContext } from './PlanContext';
import { ApiClient } from '../../api/client';

const RightPanel: React.FC = () => {
  // Contextから patientData (左ペインのデータ) を取得
  const { setCurrentPlan, isGenerating, setIsGenerating, patientData } = usePlanContext();

  const handleGenerate = async (cardTitle: string) => {
    if (!patientData) {
      alert('患者データが読み込まれていません。左パネルを確認してください。');
      return;
    }

    setIsGenerating(true);
    try {
      console.log('Generating plan with data:', patientData);
      
      // API呼び出し
      // 左ペインで編集された最新の patientData を送信します
      // ※ IDは現状 'patient_001' 固定としていますが、将来的に動的にします
      const newPlan = await ApiClient.generatePlan('patient_001', patientData);
      
      setCurrentPlan(newPlan);
      // alert(`「${cardTitle}」の生成が完了しました！`); // 毎回出ると邪魔なのでコメントアウト推奨
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
          左側のデータを元に計画書を作成します
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
                disabled={isGenerating || card.status !== 'ready' || !patientData}
                style={{ 
                  flex: 1, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  gap: '4px',
                  padding: '8px', 
                  backgroundColor: (isGenerating || !patientData) ? '#a5b4fc' : '#4f46e5', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '6px',
                  cursor: (isGenerating || !patientData) ? 'not-allowed' : 'pointer',
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