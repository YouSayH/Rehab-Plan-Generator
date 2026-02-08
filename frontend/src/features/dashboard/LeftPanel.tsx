// frontend/src/features/dashboard/LeftPanel.tsx
import React, { useEffect, useState } from 'react';
import { usePlanContext } from './PlanContext';
import { ApiClient } from '../../api/client';
import { ChevronDown, ChevronRight, LayoutGrid, Save, Plus, Trash2, ArrowRight } from 'lucide-react';
import { ValueMapping } from '../../api/types';

const presetBtnStyle: React.CSSProperties = {
  fontSize: '0.7rem', padding: '2px 6px', border: '1px solid #cbd5e1', 
  borderRadius: '4px', background: 'white', cursor: 'pointer', color: '#64748b'
};

const mappingInputStyle: React.CSSProperties = {
  border: '1px solid #e2e8f0', borderRadius: '3px', padding: '2px 4px', 
  fontSize: '0.75rem', width: '60px', color: '#334155'
};

// ==============================================================
// 1. Schema Definition (Mapping Labels & Structure)
// ==============================================================
// 表示用のラベル定義（階層構造）
const SCHEMA_DEF = [
  {
    key: 'basic', label: '基本情報',
    fields: [
      { key: 'name', label: '氏名', type: 'text' },
      { key: 'age', label: '年齢', type: 'number' },
      { key: 'gender', label: '性別', type: 'text' },
      { key: 'disease_name', label: '疾患名', type: 'text' },
      { key: 'diagnosis_code', label: '診断コード', type: 'text' }, // 追加
      { key: 'onset_date', label: '発症日', type: 'date' },
      { key: 'history', label: '病歴', type: 'text' }, // 追加
    ]
  },
  {
    key: 'medical', label: '医学的リスク・合併症',
    fields: [
      { key: 'comorbidities', label: '合併症詳細', type: 'text' },
      { key: 'risks', label: 'リスク管理', type: 'text' },
      { key: 'hypertension', label: '高血圧', type: 'boolean' },
      { key: 'diabetes', label: '糖尿病', type: 'boolean' },
      { key: 'dyslipidemia', label: '脂質異常症', type: 'boolean' },
      { key: 'ckd', label: 'CKD', type: 'boolean' },
      { key: 'angina', label: '狭心症', type: 'boolean' },
      { key: 'omi', label: '陳旧性心筋梗塞', type: 'boolean' },
    ]
  },
  {
    key: 'function', label: '心身機能',
    fields: [
      { key: 'paralysis', label: '麻痺', type: 'boolean' },
      { key: 'muscle_weakness', label: '筋力低下', type: 'boolean' },
      { key: 'rom_limitation', label: '可動域制限', type: 'boolean' },
      { key: 'pain', label: '疼痛', type: 'boolean' },
      { key: 'consciousness_disorder', label: '意識障害', type: 'boolean' },
      { key: 'disorientation', label: '見当識障害', type: 'boolean' },
      { key: 'aphasia', label: '失語症', type: 'boolean' },
      { key: 'swallowing_disorder', label: '嚥下障害', type: 'boolean' },
      { key: 'memory_disorder', label: '記憶障害', type: 'boolean' },
    ]
  },
  {
    key: 'basic_movement', label: '基本動作能力',
    fields: [
      { key: 'rolling_level', label: '寝返り', type: 'text' },
      { key: 'getting_up_level', label: '起き上がり', type: 'text' },
      { key: 'sitting_balance_level', label: '座位保持', type: 'text' },
      { key: 'standing_up_level', label: '立ち上がり', type: 'text' },
      { key: 'standing_balance_level', label: '立位保持', type: 'text' },
      { key: 'locomotion_walk.fim_current', label: '歩行(FIM)', type: 'number', pathOverride: 'adl.locomotion_walk.fim_current' }, // 便宜上ここにも表示
    ]
  },
  {
    key: 'adl', label: 'ADL (FIM/BI)',
    fields: [
      // FIM items
      { key: 'eating.fim_current', label: '食事', type: 'number' },
      { key: 'grooming.fim_current', label: '整容', type: 'number' },
      { key: 'bathing.fim_current', label: '入浴', type: 'number' },
      { key: 'dressing_upper.fim_current', label: '更衣(上)', type: 'number' },
      { key: 'dressing_lower.fim_current', label: '更衣(下)', type: 'number' },
      { key: 'toileting.fim_current', label: 'トイレ動作', type: 'number' },
      { key: 'transfer_bed.fim_current', label: '移乗(B)', type: 'number' },
      { key: 'transfer_toilet.fim_current', label: '移乗(T)', type: 'number' },
      { key: 'transfer_tub.fim_current', label: '移乗(Y)', type: 'number' },
      { key: 'locomotion_walk.fim_current', label: '移動(歩行)', type: 'number' },
      { key: 'locomotion_stairs.fim_current', label: '移動(階段)', type: 'number' },
      { key: 'comprehension.fim_current', label: '理解', type: 'number' },
      { key: 'expression.fim_current', label: '表出', type: 'number' },
      { key: 'social.fim_current', label: '社会的交流', type: 'number' },
      { key: 'problem_solving.fim_current', label: '問題解決', type: 'number' },
      { key: 'memory.fim_current', label: '記憶', type: 'number' },
    ]
  },
  {
    key: 'social', label: '社会背景',
    fields: [
      { key: 'care_level', label: '介護度', type: 'text' },
      { key: 'care_level_status', label: '申請状況', type: 'boolean' },
      { key: 'household_role_detail', label: '家庭内の役割', type: 'text' },
      { key: 'hobby_detail', label: '趣味', type: 'text' },
    ]
  },
  {
    key: 'goals', label: '目標・方針',
    fields: [
      { key: 'short_term_goal', label: '短期目標', type: 'text' },
      { key: 'long_term_goal', label: '長期目標', type: 'text' },
      { key: 'policy_content', label: '治療方針', type: 'text' },
    ]
  }
];

// ユーティリティ: オブジェクトからパスで値を取得
const getValue = (obj: any, path: string) => {
  return path.split('.').reduce((acc, part) => acc && acc[part], obj);
};

// ==============================================================
// 2. Components
// ==============================================================

const LeftPanel: React.FC = () => {
  const { 
    patientData, setPatientData, registerPatientName, 
    currentHashId, setCurrentHashId, patientList,
    fieldConfigs, updateFieldConfig, saveStructureToStorage
  } = usePlanContext();
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // アコーディオンの開閉状態
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    'basic': true,
    'medical': true,
    'adl': true
  });

  const toggleSection = (key: string) => {
    setOpenSections(prev => ({ ...prev, [key]: !prev[key] }));
  };

  // データ取得
  useEffect(() => {
    const fetchData = async () => {
      if (!currentHashId) return;
      setIsLoading(true);
      setError(null);
      try {
        console.log(`Fetching data for: ${currentHashId}`);
        const data = await ApiClient.getLatestState(currentHashId);
        setPatientData(data);
        if (data.basic && data.basic.name) {
          registerPatientName(currentHashId, data.basic.name);
        }
      } catch (err) {
        console.error(err);
        setError('患者データの取得に失敗しました');
        setPatientData(null);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [currentHashId, setPatientData, registerPatientName]);

  const handlePatientSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCurrentHashId(e.target.value);
  };

  // 設定変更ハンドラ
  const handleConfigChange = (path: string, key: keyof typeof fieldConfigs[string], value: any) => {
    updateFieldConfig(path, { [key]: value });
  };

  // ==============================================================
  // Render Helper
  // ==============================================================
  const renderFieldRow = (sectionKey: string, field: { key: string, label: string, type: string, pathOverride?: string }) => {
    if (!patientData) return null;

    const path = field.pathOverride || `${sectionKey}.${field.key}`;
    const value = getValue(patientData, path);
    const config = fieldConfigs[path] || { 
      path, targetCell: '', mappings: [], includeInPrompt: true 
    };

    // マッピング操作ヘルパー
    const addMapping = () => {
      const newMap = [...(config.mappings || []), { from: '', to: '' }];
      handleConfigChange(path, 'mappings', newMap);
    };
    
    const updateMapping = (index: number, key: 'from' | 'to', val: string) => {
      const newMap = [...(config.mappings || [])];
      newMap[index] = { ...newMap[index], [key]: val };
      handleConfigChange(path, 'mappings', newMap);
    };

    const removeMapping = (index: number) => {
      const newMap = (config.mappings || []).filter((_, i) => i !== index);
      handleConfigChange(path, 'mappings', newMap);
    };

    const applyPreset = (type: 'checkbox' | 'gender' | 'boolean') => {
      let presets: ValueMapping[] = [];
      if (type === 'checkbox') presets = [{ from: 'true', to: '☑' }, { from: 'false', to: '□' }];
      if (type === 'gender') presets = [{ from: '男', to: '㊚' }, { from: '女', to: '㊛' }];
      if (type === 'boolean') presets = [{ from: 'true', to: 'あり' }, { from: 'false', to: 'なし' }];
      handleConfigChange(path, 'mappings', presets);
    };

    // 表示用値の整形
    let displayValue = value;
    if (value === true) displayValue = "True";
    if (value === false) displayValue = "False";
    if (value === null || value === undefined) displayValue = "(なし)";

    return (
      <div key={path} style={{ 
        display: 'flex', flexDirection: 'column', gap: '4px',
        padding: '8px', borderBottom: '1px solid #f1f5f9', background: 'white'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {/* ラベルとプロンプト選択 */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
            <input 
              type="checkbox" 
              checked={config.includeInPrompt} 
              onChange={(e) => handleConfigChange(path, 'includeInPrompt', e.target.checked)}
              title="プロンプトに含める"
              style={{ cursor: 'pointer', width: '16px', height: '16px' }}
            />
            <span style={{ 
              fontSize: '0.85rem', fontWeight: 600, color: config.includeInPrompt ? '#334155' : '#94a3b8',
              textDecoration: config.includeInPrompt ? 'none' : 'line-through'
            }}>
              {field.label}
            </span>
          </div>
          
          {/* 値の表示 (編集機能は今回は省略、表示のみ) */}
          <span style={{ fontSize: '0.8rem', color: '#1e293b', fontWeight: 500, maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {String(displayValue)}
          </span>
        </div>

        {/* 詳細設定行 */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '4px', paddingLeft: '24px' }}>
          
          {/* セル指定 */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <LayoutGrid size={14} color="#94a3b8" />
            <input 
              type="text" 
              placeholder="セル (例: B10)" 
              value={config.targetCell}
              onChange={(e) => handleConfigChange(path, 'targetCell', e.target.value)}
              style={{ 
                border: '1px solid #e2e8f0', borderRadius: '4px', padding: '4px 8px', 
                fontSize: '0.8rem', width: '80px', color: '#334155'
              }}
            />
            {/* 簡易プリセットボタン */}
            <div style={{ display: 'flex', gap: '4px', marginLeft: 'auto' }}>
              <button onClick={() => applyPreset('checkbox')} title="☑/□" style={presetBtnStyle}>☑</button>
              <button onClick={() => applyPreset('gender')} title="㊚/㊛" style={presetBtnStyle}>㊚</button>
              <button onClick={() => applyPreset('boolean')} title="あり/なし" style={presetBtnStyle}>有</button>
            </div>
          </div>

          {/* マッピングリスト */}
          {config.mappings && config.mappings.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '4px' }}>
              {config.mappings.map((m, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <input 
                    placeholder="値 (例: true)" 
                    value={m.from} 
                    onChange={e => updateMapping(idx, 'from', e.target.value)}
                    style={mappingInputStyle}
                  />
                  <ArrowRight size={12} color="#cbd5e1"/>
                  <input 
                    placeholder="変換 (例: ☑)" 
                    value={m.to} 
                    onChange={e => updateMapping(idx, 'to', e.target.value)}
                    style={mappingInputStyle}
                  />
                  <button onClick={() => removeMapping(idx)} style={{ border:'none', background:'none', cursor:'pointer', color: '#ef4444' }}>
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
            </div>
          )}
          
          <button onClick={addMapping} style={{ fontSize: '0.75rem', color: '#4f46e5', background:'none', border:'none', cursor:'pointer', textAlign: 'left', padding: 0, display: 'flex', alignItems: 'center', gap: '2px' }}>
            <Plus size={12}/> 変換ルールを追加
          </button>
        </div>
      </div>
    );
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#f8fafc', borderRight: '1px solid #e2e8f0' }}>
      
      {/* Header */}
      <div style={{ padding: '16px', borderBottom: '1px solid #e2e8f0', background: 'white' }}>
        <h3 style={{ fontSize: '1.0rem', fontWeight: 'bold', marginBottom: '12px', color: '#333' }}>
          患者情報管理
        </h3>
        <select 
          value={currentHashId || ''} 
          onChange={handlePatientSelect}
          style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #cbd5e1' }}
        >
          <option value="" disabled>担当患者を選択してください</option>
          {patientList.map(p => (
            <option key={p.hash_id} value={p.hash_id}>
              {p.name ? p.name : p.hash_id}
            </option>
          ))}
        </select>
        
        {/* 設定保存ボタン */}
        <div style={{ marginTop: '8px', display: 'flex', justifyContent: 'flex-end' }}>
             <button 
               onClick={() => { saveStructureToStorage(); alert('設定を保存しました'); }}
               style={{ 
                 display: 'flex', alignItems: 'center', gap: '4px', 
                 fontSize: '0.75rem', padding: '4px 8px', borderRadius: '4px', 
                 border: '1px solid #cbd5e1', background: '#f1f5f9', cursor: 'pointer', color: '#475569'
               }}
             >
               <Save size={14}/> 設定保存
             </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '0' }}>
        {isLoading && <div style={{ padding: 16, color: '#666' }}>読み込み中...</div>}
        {error && <div style={{ padding: 16, color: 'red' }}>{error}</div>}
        
        {!isLoading && patientData && (
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            
            {/* 各セクションのレンダリング */}
            {SCHEMA_DEF.map(section => (
              <div key={section.key} style={{ borderBottom: '1px solid #e2e8f0' }}>
                <button 
                  onClick={() => toggleSection(section.key)}
                  style={{ 
                    width: '100%', padding: '10px 16px', background: '#f8fafc', border: 'none', 
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer'
                  }}
                >
                  <span style={{ fontWeight: 'bold', fontSize: '0.9rem', color: '#475569' }}>{section.label}</span>
                  {openSections[section.key] ? <ChevronDown size={16} color="#94a3b8"/> : <ChevronRight size={16} color="#94a3b8"/>}
                </button>
                
                {openSections[section.key] && (
                  <div style={{ background: '#f1f5f9' }}>
                    {section.fields.map(field => renderFieldRow(section.key, field))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {!isLoading && !patientData && !error && (
           <div style={{ padding: 16, color: '#94a3b8', fontSize: '0.9rem' }}>
             患者を選択すると詳細が表示されます。
           </div>
        )}
      </div>
    </div>
  );
};

export default LeftPanel;