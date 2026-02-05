// frontend/src/features/dashboard/RightPanel.tsx

import React, { useState, useMemo } from 'react';
import { 
  DndContext, 
  closestCenter, 
  KeyboardSensor, 
  PointerSensor, 
  useSensor, 
  useSensors,
  DragOverlay,
  defaultDropAnimationSideEffects,
  DragStartEvent,
  DragOverEvent,
  DragEndEvent
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { 
  Sparkles, Play, Edit3, Loader2, Plus, Trash2, Save, 
  MoreHorizontal, X, LayoutGrid, Folder, ChevronDown, 
  ChevronRight, GripVertical, FolderPlus
} from 'lucide-react';

import { usePlanContext } from './PlanContext';
import { ApiClient } from '../../api/client';
import { PlanItem, PlanGroup, PlanNode, PlanStructure, CELL_MAPPING } from '../../api/types';

// ==============================================================
// 1. Visual Components (見た目のみを担当)
// ==============================================================

interface ItemCardProps {
  item: PlanItem;
  currentText: string;
  isGenerating: boolean;
  onGenerate: () => void;
  onEdit: () => void;
  onTextChange: (val: string) => void;
  onTextBlur: (val: string) => void;
  dragHandleProps?: any;
}

const ItemCard: React.FC<ItemCardProps> = ({ 
  item, currentText, isGenerating, onGenerate, onEdit, onTextChange, onTextBlur, dragHandleProps 
}) => {
  return (
    <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {/* Drag Handle */}
          <div {...dragHandleProps} style={{ cursor: 'grab', color: '#cbd5e1', display: 'flex', alignItems: 'center' }}>
            <GripVertical size={18} />
          </div>
          <h3 style={{ fontWeight: 'bold', fontSize: '0.95rem', color: '#1e293b', margin: 0 }}>{item.title}</h3>
        </div>
        <button onClick={onEdit} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' }}><Edit3 size={14} /></button>
      </div>
      
      <p style={{ fontSize: '0.8rem', color: '#64748b', margin: 0 }}>{item.description}</p>
      
      {/* Action Bar */}
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        <button 
          onClick={onGenerate} 
          disabled={isGenerating}
          style={{ 
            flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', 
            padding: '8px', borderRadius: '6px', border: 'none',
            backgroundColor: isGenerating ? '#a5b4fc' : '#4f46e5', 
            color: 'white', fontSize: '0.85rem', fontWeight: 500,
            cursor: isGenerating ? 'not-allowed' : 'pointer', 
          }}
        >
          {isGenerating ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />} 
          {isGenerating ? '生成中...' : '生成'}
        </button>
        {item.targetCell && (
          <div title={`出力先セル: ${item.targetCell}`} style={{ fontSize: '0.75rem', color: '#64748b', backgroundColor: '#f1f5f9', padding: '6px 8px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '4px', border: '1px solid #e2e8f0' }}>
            <LayoutGrid size={12}/> {item.targetCell}
          </div>
        )}
      </div>

      {/* Text Area */}
      <div style={{ borderTop: '1px solid #f8fafc', paddingTop: '8px' }}>
        <textarea
          value={currentText}
          onChange={(e) => onTextChange(e.target.value)}
          onBlur={(e) => onTextBlur(e.target.value)}
          placeholder="まだ生成されていません"
          style={{
            width: '100%', minHeight: '80px', padding: '8px', borderRadius: '6px',
            border: '1px solid #e2e8f0', fontSize: '0.85rem', lineHeight: '1.5',
            resize: 'vertical', outline: 'none', fontFamily: 'inherit',
            color: '#334155', backgroundColor: '#fafafa'
          }}
        />
      </div>
    </div>
  );
};

// ==============================================================
// 2. Sortable Logic Wrappers
// ==============================================================

// Sortable Item (Leaf)
const SortablePlanItem: React.FC<{ 
  item: PlanItem; 
  onGenerate: (id: string) => void;
  generatingId: string | null;
  onEdit: (item: PlanItem) => void;
  currentPlanData: Record<string, any>;
  onTextUpdate: (key: string, val: string) => void;
  onTextBlur: (key: string, val: string) => void;
}> = ({ item, onGenerate, generatingId, onEdit, currentPlanData, onTextUpdate, onTextBlur }) => {
  
  const {
    attributes, listeners, setNodeRef, transform, transition, isDragging
  } = useSortable({ id: item.id, data: { type: 'item', item } });

  const style = {
    transform: CSS.Translate.toString(transform),
    transition,
    opacity: isDragging ? 0.3 : 1,
    marginBottom: '12px'
  };

  return (
    <div ref={setNodeRef} style={style}>
      <ItemCard 
        item={item}
        currentText={currentPlanData?.[item.targetKey] || ''}
        isGenerating={generatingId === item.id}
        onGenerate={() => onGenerate(item.id)}
        onEdit={() => onEdit(item)}
        onTextChange={(val) => onTextUpdate(item.targetKey, val)}
        onTextBlur={(val) => onTextBlur(item.targetKey, val)}
        dragHandleProps={{ ...attributes, ...listeners }}
      />
    </div>
  );
};

const SortablePlanGroup: React.FC<{
  group: PlanGroup;
  children: React.ReactNode;
  isGenerating: boolean;
  onEdit: (group: PlanGroup) => void;
  onDelete: (groupId: string) => void;
}> = ({ group, children, isGenerating, onEdit, onDelete }) => {
  const {
    attributes, listeners, setNodeRef, transform, transition, isDragging
  } = useSortable({ id: group.id, data: { type: 'group', group } });

  const [isOpen, setIsOpen] = useState(!group.isCollapsed);

  const style = {
    transform: CSS.Translate.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    backgroundColor: '#f1f5f9',
    borderRadius: '12px',
    padding: '12px',
    marginBottom: '16px',
    border: '1px dashed #cbd5e1'
  };

  return (
    <div ref={setNodeRef} style={style}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: isOpen ? '12px' : '0' }}>
        <div {...attributes} {...listeners} style={{ cursor: 'grab', color: '#94a3b8' }}>
          <GripVertical size={18} />
        </div>
        <button onClick={() => setIsOpen(!isOpen)} style={{ border: 'none', background: 'none', padding: 0, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}>
          {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          <Folder size={16} className="text-indigo-500" />
          <span style={{ fontWeight: 'bold', fontSize: '0.9rem', color: '#475569' }}>{group.title}</span>
        </button>
        
        {/* ローディング表示 */}
        {isGenerating && (
           <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: '#4f46e5', marginLeft: '8px' }}>
             <Loader2 size={14} className="animate-spin" /> 生成中...
           </span>
        )}

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8', marginRight: '4px' }}>
            {group.children.length} items
          </span>
          <button 
            onClick={(e) => { e.stopPropagation(); onEdit(group); }} 
            style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#94a3b8', padding: '4px' }}
            title="グループ編集"
          >
            <Edit3 size={14} />
          </button>
          <button 
            onClick={(e) => { e.stopPropagation(); onDelete(group.id); }} 
            style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#cbd5e1', padding: '4px' }}
            title="グループ削除"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {isOpen && (
        <div style={{ paddingLeft: '8px', minHeight: '50px' }}>
           <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
             {children}
           </div>
        </div>
      )}
    </div>
  );
};


// ==============================================================
// 3. Main RightPanel Component
// ==============================================================

const RightPanel: React.FC = () => {
  const { 
    currentPlan, setCurrentPlan, patientData, 
    planStructure, setPlanStructure, 
    resetPlanStructure, saveStructureToStorage 
  } = usePlanContext();
  
  // UI State
  const [generatingCardId, setGeneratingCardId] = useState<string | null>(null);
  const [editingItem, setEditingItem] = useState<PlanItem | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingGroup, setEditingGroup] = useState<PlanGroup | null>(null);
  const [isGroupModalOpen, setIsGroupModalOpen] = useState(false);
  const [showPresets, setShowPresets] = useState(false);
  
  // Dnd State
  const [activeId, setActiveId] = useState<string | null>(null);
  const [activeItem, setActiveItem] = useState<PlanNode | null>(null); 

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const TARGET_PATIENT_ID = 'patient_001';

  // Helpers
  const findNode = (id: string, list: PlanStructure): { node: PlanNode, parent: PlanGroup | null, index: number } | null => {
    for (let i = 0; i < list.length; i++) {
      const node = list[i];
      if (node.id === id) return { node, parent: null, index: i };
      
      if (node.type === 'group') {
        const childIndex = node.children.findIndex(c => c.id === id);
        if (childIndex !== -1) {
          return { node: node.children[childIndex], parent: node, index: childIndex };
        }
      }
    }
    return null;
  };

  // Handlers
  const handleGenerate = async (itemId: string) => {
    const found = findNode(itemId, planStructure);
    if (!found || found.node.type !== 'item') return;
    const item = found.node as PlanItem;

    if (!patientData) { alert('患者データがありません'); return; }

    setGeneratingCardId(item.id);
    try {
      console.log(`Generating ${item.title}...`);
      
      // 現在のデータを取得 (文脈として渡すため)
      const currentRawData = currentPlan?.raw_data || {};

      // 第4引数に currentRawData を追加
      const { result } = await ApiClient.generateCustom(
        patientData, 
        item.prompt, 
        item.targetKey,
        currentRawData 
      );
      
      const newRawData = { ...currentRawData, [item.targetKey]: result };
      if (currentPlan) {
        setCurrentPlan({ ...currentPlan, raw_data: newRawData });
        await ApiClient.updatePlan(currentPlan.plan_id, newRawData);
      } else {
        const newPlan = await ApiClient.createPlan(TARGET_PATIENT_ID, newRawData);
        setCurrentPlan(newPlan);
      }
    } catch (e) {
      console.error(e);
      alert('生成エラー');
    } finally {
      setGeneratingCardId(null);
    }
  };

  // 全パネルの一括生成 (シーケンシャル + バッチ処理)
  const handleGenerateAll = async () => {
    if (!patientData) {
      alert('患者データがありません。');
      return;
    }
    
    if (!window.confirm('全項目を順次生成しますか？\n（既存の入力内容は上書きされます）')) return;

    // 現在の最新データを取得するためのローカル変数（State更新の遅延対策）
    let currentRawData = currentPlan?.raw_data || {};

    try {
      // planStructure (階層構造) を上から順にループ
      for (const node of planStructure) {
        
        // === ケース1: 単体アイテム ===
        if (node.type === 'item') {
          setGeneratingCardId(node.id); // UIでローディング表示
          
          // 単体生成API呼び出し (currentRawData を渡す)
          const { result } = await ApiClient.generateCustom(
            patientData, 
            node.prompt, 
            node.targetKey,
            currentRawData
          );
          
          // データ更新
          currentRawData = { ...currentRawData, [node.targetKey]: result };
          
          // DB保存 & 画面更新
          if (currentPlan) {
            await ApiClient.updatePlan(currentPlan.plan_id, currentRawData);
            setCurrentPlan({ ...currentPlan, raw_data: currentRawData });
          } else {
            // 初回作成
            const newPlan = await ApiClient.createPlan(TARGET_PATIENT_ID, currentRawData);
            setCurrentPlan(newPlan);
          }
        } 
        
        // === ケース2: グループ (一括生成) ===
        else if (node.type === 'group') {
          setGeneratingCardId(node.id); // グループ全体をローディング表示
          
          // グループ内の生成対象リストを作成
          const batchItems = node.children.map(child => ({
            targetKey: child.targetKey,
            prompt: child.prompt
          }));

          if (batchItems.length > 0) {
            console.log(`Batch generating group: ${node.title}`);
            
            // バッチ生成API呼び出し (currentRawData を渡す)
            const results = await ApiClient.generateBatch(
              patientData, 
              batchItems,
              currentRawData
            );
            
            // 結果をマージ
            currentRawData = { ...currentRawData, ...results };
            
            // DB保存 & 画面更新
            if (currentPlan) {
              await ApiClient.updatePlan(currentPlan.plan_id, currentRawData);
              setCurrentPlan({ ...currentPlan, raw_data: currentRawData });
            } else {
               const newPlan = await ApiClient.createPlan(TARGET_PATIENT_ID, currentRawData);
               setCurrentPlan(newPlan);
            }
          }
        }
      }
      
      alert('すべての生成が完了しました！');

    } catch (error) {
      console.error('Batch generation failed:', error);
      alert('一括生成中にエラーが発生しました。中断します。');
    } finally {
      setGeneratingCardId(null);
    }
  };

  const handleEditGroup = (group: PlanGroup) => {
    setEditingGroup(group);
    setIsGroupModalOpen(true);
  };

  const handleSaveGroup = (group: PlanGroup) => {
    // グループ情報の更新
    setPlanStructure(prev => prev.map(node => {
      if (node.id === group.id && node.type === 'group') {
        return group;
      }
      return node;
    }));
    setIsGroupModalOpen(false);
    setEditingGroup(null);
    saveStructureToStorage(); // 保存
  };

  const handleDeleteGroup = (groupId: string) => {
    const group = planStructure.find(n => n.id === groupId);
    if (!group || group.type !== 'group') return;

    if (group.children.length > 0) {
      if (!window.confirm(`グループ「${group.title}」には ${group.children.length} 個のパネルが含まれています。\n削除すると中のパネルもすべて削除されます。\n本当によろしいですか？`)) {
        return;
      }
    } else {
      if (!window.confirm(`グループ「${group.title}」を削除しますか？`)) return;
    }

    setPlanStructure(prev => prev.filter(n => n.id !== groupId));
    saveStructureToStorage(); // 保存
  };

  const handleTextUpdate = (key: string, val: string) => {
    if (!currentPlan) return;
    setCurrentPlan({ ...currentPlan, raw_data: { ...currentPlan.raw_data, [key]: val } });
  };
  
  const handleTextBlur = async (key: string, val: string) => {
    if (!currentPlan) return;
    await ApiClient.updatePlan(currentPlan.plan_id, { ...currentPlan.raw_data, [key]: val });
  };

  // Drag & Drop Handlers (Updated for Groups)
  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    setActiveId(active.id as string);
    const found = findNode(active.id as string, planStructure);
    if (found) setActiveItem(found.node);
  };

  // コンテナ間移動ロジック
  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event;
    if (!over) return;
    if (active.id === over.id) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    const activeInfo = findNode(activeId, planStructure);
    const overInfo = findNode(overId, planStructure);

    if (!activeInfo) return; // Active must exist

    // Item以外（つまりGroup）を他のコンテナに混ぜることは今回は禁止（ルート並べ替えのみ）
    if (activeInfo.node.type === 'group') return;

    // 現在の親
    const activeParentId = activeInfo.parent ? activeInfo.parent.id : 'root';
    
    // 移動先の親を特定
    let overParentId = 'root';
    if (overInfo) {
      if (overInfo.node.type === 'group') {
        // グループの上にドラッグ -> そのグループの中へ
        overParentId = overInfo.node.id;
      } else {
        // アイテムの上にドラッグ -> そのアイテムと同じ親へ
        overParentId = overInfo.parent ? overInfo.parent.id : 'root';
      }
    } else {
       // overInfoがない（空のSortableContext領域など）場合はrootとみなす
       overParentId = 'root'; 
    }

    // 異なるコンテナへの移動の場合のみ処理
    if (activeParentId !== overParentId) {
      setPlanStructure((prev) => {
        // Deep copy
        const next = JSON.parse(JSON.stringify(prev)) as PlanStructure;

        // 1. 古い親から削除
        let itemToMove: PlanItem | null = null;
        if (activeParentId === 'root') {
          const idx = next.findIndex(n => n.id === activeId);
          if (idx !== -1) {
             itemToMove = next[idx] as PlanItem;
             next.splice(idx, 1);
          }
        } else {
          const group = next.find(n => n.id === activeParentId) as PlanGroup;
          if (group) {
             const idx = group.children.findIndex(c => c.id === activeId);
             if (idx !== -1) {
               itemToMove = group.children[idx];
               group.children.splice(idx, 1);
             }
          }
        }

        if (!itemToMove) return prev;

        // 2. 新しい親に追加
        if (overParentId === 'root') {
           // Rootへ移動
           const overIdx = next.findIndex(n => n.id === overId);
           // overが見つからない(group等)場合は末尾、見つかればその位置
           const insertIdx = overIdx >= 0 ? overIdx : next.length; 
           next.splice(insertIdx, 0, itemToMove);
        } else {
           // Groupへ移動
           const group = next.find(n => n.id === overParentId) as PlanGroup;
           if (group) {
             const overIdx = group.children.findIndex(c => c.id === overId);
             const insertIdx = overIdx >= 0 ? overIdx : group.children.length;
             group.children.splice(insertIdx, 0, itemToMove);
           }
        }
        return next;
      });
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);
    setActiveItem(null);

    if (!over) return;
    // if (active.id === over.id) return;

    const activeInfo = findNode(active.id as string, planStructure);
    const overInfo = findNode(over.id as string, planStructure);

    if (!activeInfo || !overInfo) return;

    const activeParentId = activeInfo.parent ? activeInfo.parent.id : 'root';
    const overParentId = overInfo.parent ? overInfo.parent.id : 'root';

    if (activeParentId === overParentId) {
      if (activeParentId === 'root') {
          const oldIndex = activeInfo.index;
          const newIndex = overInfo.index;
          if (oldIndex !== newIndex) {
            setPlanStructure((items) => arrayMove(items, oldIndex, newIndex));
          }
      } else {
          // グループ内での並べ替え
          setPlanStructure((prev) => {
             const next = [...prev];
             const groupIndex = next.findIndex(n => n.id === activeParentId);
        if (groupIndex !== -1) {
                const group = { ...next[groupIndex] } as PlanGroup;
                const oldIndex = activeInfo.index;
                // findNodeのindexはchildren配列内のindexなのでそのまま使える
                const newIndex = group.children.findIndex(c => c.id === over.id);
                
                if (oldIndex !== -1 && newIndex !== -1 && oldIndex !== newIndex) {
                   group.children = arrayMove(group.children, oldIndex, newIndex);
                   next[groupIndex] = group;
                }
             }
             return next;
          });
      }
    }
    
    // 状態確定後に保存
    saveStructureToStorage();
  };

  // Config Logic (Add Group)

  // グループ追加処理
  const handleCreateGroup = () => {
    const newGroup: PlanGroup = {
      id: `group_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, // ユニーク性を強化
      type: 'group',
      title: '新しいグループ',
      children: [],
      isCollapsed: false
    };
    
    setPlanStructure([...planStructure, newGroup]);
    saveStructureToStorage();
  };

  const openNewItemModal = () => {
    setEditingItem({
      id: `custom_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, // ユニーク性を強化
      type: 'item',
      title: '新規パネル',
      description: '',
      prompt: '',
      targetKey: 'new_key',
      targetCell: ''
    });
    setIsEditModalOpen(true);
  };

  const handleSaveItem = (item: PlanItem) => {
    let updated = false;
    const updateRecursive = (list: PlanStructure): PlanStructure => {
      return list.map(node => {
        if (node.id === item.id) {
          updated = true;
          return item; 
        }
        if (node.type === 'group') {
          return { ...node, children: updateRecursive(node.children) };
        }
        return node;
      });
    };

    let newStructure = updateRecursive(planStructure);
    if (!updated) {
      newStructure = [...newStructure, item];
    }
    
    setPlanStructure(newStructure);
    setIsEditModalOpen(false);
    saveStructureToStorage();
  };

  const handleDeleteItem = (id: string) => {
     if(!window.confirm('削除しますか？')) return;
     const deleteRecursive = (list: PlanStructure): PlanStructure => {
        return list
          .filter(node => node.id !== id)
          .map(node => {
             if(node.type === 'group') {
               return { ...node, children: deleteRecursive(node.children) };
             }
             return node;
          });
     };
     setPlanStructure(deleteRecursive(planStructure));
     setIsEditModalOpen(false);
     saveStructureToStorage();
  };


  // Render
  const rootIds = useMemo(() => planStructure.map(n => n.id), [planStructure]);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#f8fafc', borderLeft: '1px solid #e2e8f0' }}>
      
      {/* Header */}
      <div style={{ padding: '16px', backgroundColor: 'white', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between' }}>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#4f46e5', display: 'flex', gap: '8px' }}><Sparkles size={20}/> AI Co-Editor</h2>
        <div style={{ position: 'relative' }}>
          <button onClick={() => setShowPresets(!showPresets)} style={{ border:'none', background:'none', cursor:'pointer' }}><MoreHorizontal size={18} /></button>
          {showPresets && (
            <div style={{ position: 'absolute', right: 0, top: '100%', width: '200px', background: 'white', padding: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', borderRadius: '8px', zIndex: 10, border:'1px solid #e2e8f0' }}>
              <button onClick={() => { saveStructureToStorage(); alert('保存しました'); setShowPresets(false); }} style={menuBtnStyle}><Save size={14}/> レイアウト保存</button>
              <button onClick={() => { resetPlanStructure(); setShowPresets(false); }} style={menuBtnStyle}><Trash2 size={14}/> リセット</button>
              <button onClick={handleGenerateAll} style={{ ...menuBtnStyle, color: '#4f46e5', fontWeight: 'bold' }}><Play size={14}/> 全て生成</button>
            </div>
          )}
        </div>
      </div>

      {/* Main List Area */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        <DndContext 
          sensors={sensors} 
          collisionDetection={closestCenter} 
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
          onDragCancel={() => { setActiveId(null); setActiveItem(null); }}
        >
          <SortableContext items={rootIds} strategy={verticalListSortingStrategy}>
            {planStructure.map(node => {
              if (node.type === 'group') {
                return (
                  <SortablePlanGroup key={node.id} group={node as PlanGroup} isGenerating={generatingCardId === node.id} onEdit={handleEditGroup} onDelete={handleDeleteGroup}>
                    <SortableContext items={node.children.map(c => c.id)} strategy={verticalListSortingStrategy}>
                       {node.children.map(child => (
                         <SortablePlanItem 
                           key={child.id} 
                           item={child}
                           onGenerate={handleGenerate}
                           generatingId={generatingCardId}
                           onEdit={(itm) => { setEditingItem(itm); setIsEditModalOpen(true); }}
                           currentPlanData={currentPlan?.raw_data || {}}
                           onTextUpdate={handleTextUpdate}
                           onTextBlur={handleTextBlur}
                         />
                       ))}
                    </SortableContext>
                  </SortablePlanGroup>
                );
              } else {
                return (
                  <SortablePlanItem 
                    key={node.id} 
                    item={node as PlanItem}
                    onGenerate={handleGenerate}
                    generatingId={generatingCardId}
                    onEdit={(itm) => { setEditingItem(itm); setIsEditModalOpen(true); }}
                    currentPlanData={currentPlan?.raw_data || {}}
                    onTextUpdate={handleTextUpdate}
                    onTextBlur={handleTextBlur}
                  />
                );
              }
            })}
          </SortableContext>
          
          <DragOverlay dropAnimation={defaultDropAnimationSideEffects({ styles: { active: { opacity: '0.5' } } })}>
             {activeItem && activeItem.type === 'item' ? (
                <div style={{ opacity: 0.8 }}>
                   <ItemCard 
                     item={activeItem as PlanItem} 
                     currentText="" isGenerating={false} 
                     onGenerate={()=>{}} onEdit={()=>{}} onTextChange={()=>{}} onTextBlur={()=>{}} 
                   />
                </div>
             ) : activeItem && activeItem.type === 'group' ? (
                <div style={{ padding: '12px', background: '#f1f5f9', borderRadius: '12px', border: '1px dashed #cbd5e1' }}>
                  <strong>{(activeItem as PlanGroup).title}</strong>
                </div>
             ) : null}
          </DragOverlay>
        </DndContext>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
           <button onClick={handleCreateGroup} style={{ ...actionBtnStyle, backgroundColor: '#f1f5f9', color: '#475569' }}>
             <FolderPlus size={18}/> 新規グループ
           </button>
           <button onClick={openNewItemModal} style={{ ...actionBtnStyle, backgroundColor: 'transparent', border: '2px dashed #cbd5e1', color: '#64748b' }}>
          <Plus size={18}/> 新しいパネル
        </button>
        </div>
      </div>

      {/* Edit Modal (Item) */}
{isEditModalOpen && editingItem && (
        <div style={{ position: 'fixed', top:0, left:0, right:0, bottom:0, background: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
           <div style={{ background: 'white', padding: '24px', borderRadius: '12px', width: '450px', display: 'flex', flexDirection: 'column', gap: '16px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)' }}>
              
              {/* Header with Close Button */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontWeight: 'bold', fontSize: '1.1rem', margin: 0 }}>パネル設定</h3>
                <button onClick={() => setIsEditModalOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
                  <X size={20}/>
                </button>
              </div>

              {/* 2カラムレイアウト (タイトル & 出力セル) */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                 <label style={labelStyle}>タイトル
                   <input value={editingItem.title} onChange={e => setEditingItem({...editingItem, title: e.target.value})} style={inputStyle} placeholder="タイトル"/>
                 </label>
                 <label style={labelStyle}>出力先セル (任意)
                   <div style={{ display: 'flex', alignItems: 'center', position: 'relative' }}>
                     <input 
                       type="text" 
                       value={editingItem.targetCell || ''} 
                       onChange={e => setEditingItem({...editingItem, targetCell: e.target.value.toUpperCase()})}
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
                  value={editingItem.description || ''} 
                  onChange={e => setEditingItem({...editingItem, description: e.target.value})} 
                  style={inputStyle} 
                  placeholder="パネルの説明文..."
                />
              </label>

              <label style={labelStyle}>AIへの指示 (Prompt)
                <textarea value={editingItem.prompt} onChange={e => setEditingItem({...editingItem, prompt: e.target.value})} style={{...inputStyle, height: '100px', resize: 'vertical'}} placeholder="プロンプト"/>
              </label>

              <label style={labelStyle}>保存先データキー (Target Key)
                <input 
                  list="target-keys-list"
                  value={editingItem.targetKey} 
                  onChange={e => setEditingItem({...editingItem, targetKey: e.target.value})} 
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
              </label>
              
              <div style={{ display: 'flex', gap: '8px', marginTop: '8px', paddingTop: '12px', borderTop: '1px solid #f1f5f9' }}>
                <button onClick={() => handleDeleteItem(editingItem.id)} style={{...btnStyle, background:'#fee2e2', color:'#dc2626'}}>削除</button>
                <div style={{flex:1}}/>
                <button onClick={() => setIsEditModalOpen(false)} style={{...btnStyle, background:'#f1f5f9', color: '#64748b'}}>キャンセル</button>
                <button onClick={() => handleSaveItem(editingItem)} style={{...btnStyle, background:'#4f46e5', color:'white'}}>保存</button>
              </div>
           </div>
        </div>
      )}

      {/* Edit Modal (Group) */}
      {isGroupModalOpen && editingGroup && (
        <div style={{ position: 'fixed', top:0, left:0, right:0, bottom:0, background: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
           <div style={{ background: 'white', padding: '24px', borderRadius: '12px', width: '400px', display: 'flex', flexDirection: 'column', gap: '16px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)' }}>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontWeight: 'bold', fontSize: '1.1rem', margin: 0 }}>グループ編集</h3>
                <button onClick={() => setIsGroupModalOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
                  <X size={20}/>
                </button>
              </div>

              <label style={labelStyle}>グループ名
                <input 
                  value={editingGroup.title} 
                  onChange={e => setEditingGroup({...editingGroup, title: e.target.value})} 
                  style={inputStyle} 
                  placeholder="グループ名"
                  autoFocus
                />
              </label>
              
              <div style={{ display: 'flex', gap: '8px', marginTop: '8px', paddingTop: '12px', borderTop: '1px solid #f1f5f9' }}>
                <div style={{flex:1}}/>
                <button onClick={() => setIsGroupModalOpen(false)} style={{...btnStyle, background:'#f1f5f9', color: '#64748b'}}>キャンセル</button>
                <button onClick={() => handleSaveGroup(editingGroup)} style={{...btnStyle, background:'#4f46e5', color:'white'}}>保存</button>
              </div>
           </div>
        </div>
      )}
    </div>
  );
};

// Styles
const menuBtnStyle = { display: 'flex', alignItems: 'center', gap: '6px', padding: '8px', width: '100%', border: 'none', background: 'transparent', cursor: 'pointer', textAlign: 'left' as const, fontSize: '0.9rem' };
const labelStyle = { display: 'flex', flexDirection: 'column' as const, gap: '6px', fontSize: '0.85rem', fontWeight: 600, color: '#334155' };
const inputStyle = { padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.9rem', width: '100%', boxSizing: 'border-box' as const, outline: 'none' };
const btnStyle = { padding: '8px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 500 };
const actionBtnStyle = { flex: 1, padding: '12px', borderRadius: '12px', border: 'none', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', fontWeight: 500 };

export default RightPanel;