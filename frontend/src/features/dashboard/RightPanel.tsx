import React, { useState } from 'react';
import { Sparkles, Play, Edit3, Loader2, Plus, Trash2, Save, MoreHorizontal, X, LayoutGrid } from 'lucide-react';
import { usePlanContext } from './PlanContext';
import { ApiClient } from '../../api/client';
import { CardConfig, CELL_MAPPING } from '../../api/types';

const RightPanel: React.FC = () => {
  // PlanContextから状態と操作メソッドを取得
  const { currentPlan, setCurrentPlan, patientData, cards, setCards, resetCards, saveCardsToStorage } = usePlanContext();
  
  // ローカルUI状態
  const [generatingCardId, setGeneratingCardId] = useState<string | null>(null);
  const [editingCard, setEditingCard] = useState<CardConfig | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [showPresets, setShowPresets] = useState(false);

  // 仮の患者ID (将来的に動的化が必要)
  const TARGET_PATIENT_ID = 'patient_001';

  // --- 生成実行ロジック ---
  const handleGenerate = async (card: CardConfig) => {
    if (!patientData) {
      alert('患者データがありません。');
      return;
    }
    
    setGeneratingCardId(card.id);
    try {
      console.log(`Generating for ${card.title}...`);
      
      // 1. AIでテキスト生成 (カスタム生成API)
      const { result } = await ApiClient.generateCustom(patientData, card.prompt, card.targetKey);
      
      // 2. 結果を保存
      if (currentPlan) {
        // ▼ パターンA: 既存の計画書がある場合 -> 更新 (Update)
        const newRawData = { ...currentPlan.raw_data, [card.targetKey]: result };
        
        // フロントエンドの表示更新（楽観的UI）
        setCurrentPlan({ ...currentPlan, raw_data: newRawData });
        
        // DB保存 (バックグラウンド)
        await ApiClient.updatePlan(currentPlan.plan_id, newRawData);

      } else {
        // ▼ パターンB: 計画書がまだない場合 -> 新規作成 (Create)
        console.log('Creating new plan with generated content...');
        const initialData = { [card.targetKey]: result };
        
        // createPlanメソッドを使用して新規保存
        const newPlan = await ApiClient.createPlan(TARGET_PATIENT_ID, initialData);
        setCurrentPlan(newPlan);
      }
      
    } catch (error) {
      console.error('Generation failed:', error);
      alert(`生成エラー: ${card.title}\nコンソールログを確認してください。`);
    } finally {
      setGeneratingCardId(null);
    }
  };

  // 全パネルの一括生成
  const handleGenerateAll = async () => {
    if (!window.confirm('すべてのパネルを順次生成しますか？\n（既存の入力内容は上書きされます）')) return;
    
    // 順次実行
    for (const card of cards) {
      await handleGenerate(card);
    }
  };

  // 入力中はContextのみ更新（画面反映を高速化）
  const handleTextChange = (key: string, val: string) => {
    if (!currentPlan) return;
    const newRawData = { ...currentPlan.raw_data, [key]: val };
    setCurrentPlan({ ...currentPlan, raw_data: newRawData });
  };

  // フォーカスが外れたらDB保存（API通信を節約）
  const handleTextBlur = async (key: string, val: string) => {
    if (!currentPlan) return;
    try {
      console.log('Saving changes for:', key);
      await ApiClient.updatePlan(currentPlan.plan_id, { ...currentPlan.raw_data, [key]: val });
    } catch (e) {
      console.error('Save failed:', e);
    }
  };

  // --- カード編集・追加・削除ロジック ---
  const handleSaveCard = (card: CardConfig) => {
    // IDが一致するものを更新、なければ追加
    const updatedCards = cards.find(c => c.id === card.id)
      ? cards.map(c => c.id === card.id ? card : c)
      : [...cards, card];
    
    setCards(updatedCards);
    setIsEditModalOpen(false);
    setEditingCard(null);
  };

  const handleDeleteCard = (id: string) => {
    if (window.confirm('このパネルを削除しますか？')) {
      setCards(cards.filter(c => c.id !== id));
      setIsEditModalOpen(false);
    }
  };

  const openNewCardModal = () => {
    setEditingCard({
      id: `custom_${Date.now()}`,
      title: '新規パネル',
      description: '説明文を入力...',
      prompt: 'ここにAIへの指示を入力してください...',
      targetKey: 'new_item_txt',
      targetCell: '' // デフォルトは空
    });
    setIsEditModalOpen(true);
  };

  // 設定メニュー操作
  const handleConfigSave = () => {
    saveCardsToStorage();
    alert('現在のパネル設定をブラウザに保存しました。');
    setShowPresets(false);
  };

  const handleConfigReset = () => {
    if(window.confirm('パネル設定を初期状態に戻しますか？')) {
      resetCards();
      setShowPresets(false);
    }
  };

  // --- UI描画 ---
  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#f8fafc', borderLeft: '1px solid #e2e8f0' }}>
      
      {/* ヘッダーエリア */}
      <div style={{ padding: '16px', backgroundColor: 'white', borderBottom: '1px solid #e2e8f0' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px', color: '#4f46e5' }}>
            <Sparkles size={20} /> AI Co-Editor
          </h2>
          
          <div style={{ position: 'relative' }}>
             <button 
               onClick={() => setShowPresets(!showPresets)} 
               title="メニュー"
               style={{ padding: '6px', cursor: 'pointer', border: 'none', background: 'transparent', borderRadius: '4px' }}
             >
               <MoreHorizontal size={18} color="#64748b" />
             </button>
             
             {/* プリセットメニュー */}
             {showPresets && (
              <div style={{ 
                position: 'absolute', right: 0, top: '100%', width: '220px', 
                padding: '8px', backgroundColor: 'white', borderRadius: '8px', 
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)', border: '1px solid #e2e8f0', zIndex: 10 
              }}>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                  <button onClick={handleConfigSave} style={presetBtnStyle}><Save size={14}/> 設定保存</button>
                  <button onClick={handleConfigReset} style={presetBtnStyle}><Trash2 size={14}/> リセット</button>
                </div>
                {/* 計画書がない場合は、まず個別の「生成」ボタンで計画書を作成してもらうフローにします。 */}
                <button 
                  onClick={handleGenerateAll} 
                  disabled={!patientData || !!generatingCardId || !currentPlan} 
                  style={{ ...presetBtnStyle, width: '100%', backgroundColor: !currentPlan ? '#94a3b8' : '#4f46e5', color: 'white', border: 'none', justifyContent: 'center' }}
                  title={!currentPlan ? "まずは個別のパネルを生成して計画書を作成してください" : "全項目を生成"}
                >
                  <Play size={14} /> 全パネルを一括生成
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* カードリストエリア */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {cards.map(card => {
          const textValue = currentPlan?.raw_data?.[card.targetKey] || '';

          return (
            <div key={card.id} style={{ backgroundColor: 'white', borderRadius: '12px', padding: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', border: '1px solid #e2e8f0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <h3 style={{ fontWeight: 'bold', fontSize: '0.95rem', color: '#1e293b' }}>{card.title}</h3>
                <button onClick={() => { setEditingCard(card); setIsEditModalOpen(true); }} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' }}><Edit3 size={14} /></button>
              </div>
              
              <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '12px' }}>{card.description}</p>
              
              {/* アクションボタン */}
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <button 
                  onClick={() => handleGenerate(card)} 
                  disabled={!!generatingCardId || !patientData}
                  style={{ 
                    flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', 
                    padding: '8px', borderRadius: '6px', border: 'none',
                    backgroundColor: generatingCardId === card.id ? '#a5b4fc' : '#4f46e5', 
                    color: 'white', fontSize: '0.85rem', fontWeight: 500,
                    cursor: (generatingCardId || !patientData) ? 'not-allowed' : 'pointer', 
                  }}
                >
                  {generatingCardId === card.id ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />} 
                  {generatingCardId === card.id ? '生成中...' : '生成'}
                </button>
                {card.targetCell && (
                  <div title={`出力先セル: ${card.targetCell}`} style={{ fontSize: '0.75rem', color: '#64748b', backgroundColor: '#f1f5f9', padding: '6px 8px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '4px', border: '1px solid #e2e8f0' }}>
                    <LayoutGrid size={12}/> {card.targetCell}
                  </div>
                )}
              </div>

              {currentPlan && (
                <div style={{ marginTop: '12px', borderTop: '1px solid #f8fafc', paddingTop: '8px' }}>
                  <textarea
                    value={textValue}
                    onChange={(e) => handleTextChange(card.targetKey, e.target.value)}
                    onBlur={(e) => handleTextBlur(card.targetKey, e.target.value)}
                    placeholder="まだ生成されていません"
                    style={{
                      width: '100%',
                      minHeight: '80px',
                      padding: '8px',
                      borderRadius: '6px',
                      border: '1px solid #e2e8f0',
                      fontSize: '0.85rem',
                      lineHeight: '1.5',
                      resize: 'vertical',
                      outline: 'none',
                      fontFamily: 'inherit',
                      color: '#334155',
                      backgroundColor: '#fafafa'
                    }}
                  />
                </div>
              )}

            </div>
          );
        })}

        {/* 追加ボタン */}
        <button 
          onClick={openNewCardModal} 
          style={{ 
            padding: '12px', border: '2px dashed #cbd5e1', borderRadius: '12px', 
            backgroundColor: 'transparent', color: '#64748b', cursor: 'pointer', 
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
            fontWeight: 500
          }}
        >
          <Plus size={18} /> 新しいパネルを追加
        </button>
      </div>

      {/* 編集モーダル */}
      {isEditModalOpen && editingCard && (
        <div style={{ 
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000, 
          display: 'flex', alignItems: 'center', justifyContent: 'center' 
        }}>
          <div style={{ 
            backgroundColor: 'white', width: '450px', borderRadius: '12px', padding: '24px', 
            boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)' 
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h3 style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>パネル設定</h3>
              <button onClick={() => setIsEditModalOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}><X size={20}/></button>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                 <label style={labelStyle}>タイトル
                   <input 
                     type="text" 
                     value={editingCard.title} 
                     onChange={e => setEditingCard({...editingCard, title: e.target.value})} 
                     style={inputStyle} 
                   />
                 </label>
                 
                 {/* セル座標入力: "B12"形式 */}
                 <label style={labelStyle}>出力先セル (任意)
                   <div style={{ display: 'flex', alignItems: 'center', position: 'relative' }}>
                     <input 
                       type="text" 
                       value={editingCard.targetCell || ''} 
                       onChange={e => setEditingCard({...editingCard, targetCell: e.target.value.toUpperCase()})}
                       style={{ ...inputStyle, paddingLeft: '32px' }}
                       placeholder="A1"
                     />
                     <LayoutGrid size={16} style={{ position: 'absolute', left: '10px', color: '#94a3b8' }} />
                   </div>
                 </label>
              </div>

              <label style={labelStyle}>説明
                <input 
                  type="text" 
                  value={editingCard.description} 
                  onChange={e => setEditingCard({...editingCard, description: e.target.value})} 
                  style={inputStyle} 
                />
              </label>

              <label style={labelStyle}>AIへの指示 (Prompt)
                <textarea 
                  value={editingCard.prompt} 
                  onChange={e => setEditingCard({...editingCard, prompt: e.target.value})} 
                  style={{ ...inputStyle, minHeight: '100px', resize: 'vertical' }} 
                  placeholder="例：患者の主訴から、最も優先すべきリハビリ目標を1つ提案してください。"
                />
              </label>

              {/* ターゲットキー: Datalistで提案 + 自由入力 */}
              <label style={labelStyle}>
                保存先データキー (Target Key)
                <input 
                  list="target-keys-list" 
                  type="text" 
                  value={editingCard.targetKey} 
                  onChange={e => setEditingCard({...editingCard, targetKey: e.target.value})}
                  style={inputStyle}
                  placeholder="キーを入力または選択..."
                />
                <datalist id="target-keys-list">
                  {Object.keys(CELL_MAPPING).map(key => (
                    <option key={key} value={key} />
                  ))}
                  <option value="custom_memo_txt" />
                  <option value="summary_txt" />
                </datalist>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '4px' }}>
                  ※ 既存のキーを選択するか、新しいキー名を直接入力してください
                </span>
              </label>

              <div style={{ display: 'flex', gap: '12px', marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #f1f5f9' }}>
                <button onClick={() => handleDeleteCard(editingCard.id)} style={{ ...modalBtnStyle, backgroundColor: '#fee2e2', color: '#dc2626' }}>削除</button>
                <div style={{ flex: 1 }}></div>
                <button onClick={() => setIsEditModalOpen(false)} style={{ ...modalBtnStyle, backgroundColor: '#f1f5f9', color: '#64748b' }}>キャンセル</button>
                <button onClick={() => handleSaveCard(editingCard)} style={{ ...modalBtnStyle, backgroundColor: '#4f46e5', color: 'white' }}>保存</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// --- Styles ---
const presetBtnStyle = { 
  display: 'flex', alignItems: 'center', gap: '4px', 
  padding: '6px 10px', borderRadius: '6px', border: '1px solid #cbd5e1', 
  backgroundColor: 'white', cursor: 'pointer', fontSize: '0.8rem', color: '#475569', 
  flex: 1 
};
const labelStyle = { 
  display: 'flex', flexDirection: 'column' as const, gap: '6px', 
  fontSize: '0.85rem', fontWeight: 600, color: '#334155' 
};
const inputStyle = { 
  padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1', 
  fontSize: '0.9rem', width: '100%', boxSizing: 'border-box' as const,
  outline: 'none', transition: 'border-color 0.2s'
};
const modalBtnStyle = { 
  padding: '8px 16px', borderRadius: '6px', border: 'none', 
  cursor: 'pointer', fontWeight: 500, fontSize: '0.9rem' 
};

export default RightPanel;