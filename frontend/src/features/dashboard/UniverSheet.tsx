import React, { useEffect, useRef } from 'react';
import '@univerjs/design/lib/index.css';
import '@univerjs/ui/lib/index.css';
import '@univerjs/sheets-ui/lib/index.css';

import { Univer, LocaleType, UniverInstanceType, ICommandService } from '@univerjs/core';
import { defaultTheme } from '@univerjs/design';
import { UniverDocsPlugin } from '@univerjs/docs';
import { UniverDocsUIPlugin } from '@univerjs/docs-ui';
import { UniverFormulaEnginePlugin } from '@univerjs/engine-formula';
import { UniverRenderEnginePlugin } from '@univerjs/engine-render';
import { UniverSheetsPlugin, SetRangeValuesCommand } from '@univerjs/sheets';
import { UniverSheetsFormulaPlugin } from '@univerjs/sheets-formula';
import { UniverSheetsUIPlugin } from '@univerjs/sheets-ui';
import { UniverUIPlugin } from '@univerjs/ui';

import { usePlanContext } from './PlanContext';
import { CELL_MAPPING, parseCellAddress, CellMapping, PlanStructure, PlanItem } from '../../api/types';

const UniverSheet: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const univerRef = useRef<Univer | null>(null);
  
  // cards ではなく planStructure を取得
  const { currentPlan, planStructure } = usePlanContext();

  // ヘルパー: 階層構造から指定されたキーを持つアイテムを探す
  const findItemByKey = (structure: PlanStructure, key: string): PlanItem | undefined => {
    for (const node of structure) {
      if (node.type === 'item' && node.targetKey === key) {
        return node;
      }
      if (node.type === 'group') {
        const found = node.children.find(child => child.targetKey === key);
        if (found) return found;
      }
    }
    return undefined;
  };

  // 1. Univer初期化
  useEffect(() => {
    if (!containerRef.current || univerRef.current) return;

    const univer = new Univer({
      theme: defaultTheme,
      locale: LocaleType.JA_JP, 
      locales: {
        // ロケール定義がないと "Locale not initialized" エラーになるため、
        // インポートエラーを避けるために一旦空のオブジェクトを定義して回避します。
        [LocaleType.JA_JP]: {},
      },
    });

    // 2. コアプラグイン登録
    univer.registerPlugin(UniverRenderEnginePlugin);
    univer.registerPlugin(UniverFormulaEnginePlugin);

    // 3. UIプラグイン登録
    univer.registerPlugin(UniverUIPlugin, {
      container: containerRef.current,
      header: true,
      footer: true,
    });

    // 4. ドキュメント・シート機能登録
    univer.registerPlugin(UniverDocsPlugin, { hasScroll: false });
    univer.registerPlugin(UniverDocsUIPlugin);
    univer.registerPlugin(UniverSheetsPlugin);
    univer.registerPlugin(UniverSheetsUIPlugin);
    univer.registerPlugin(UniverSheetsFormulaPlugin);

    // 5. ワークブック作成
    // UniverInstanceType.UNIVER_SHEET (通常は1) を指定
    univer.createUnit(UniverInstanceType.UNIVER_SHEET, {
      id: 'workbook-01',
      name: 'リハビリ計画書',
      appVersion: '3.0.0',
      sheets: {
        'sheet-01': {
          id: 'sheet-01',
          name: '様式23',
          cellData: {
            0: { 0: { v: 'リハビリテーション総合実施計画書' } },
            // 必要に応じて初期ラベルなどを配置
            11: { 0: { v: '短期目標:' } },
            13: { 0: { v: '長期目標:' } },
            15: { 0: { v: 'プログラム:' } },
            17: { 0: { v: 'リスク管理:' } },
          }
        }
      }
    });

    univerRef.current = univer;

    // クリーンアップ
    return () => {
      if (univerRef.current) {
        // setTimeoutを使わず、コンポーネント破棄時に即座にリソースを開放
        univerRef.current.dispose();
        univerRef.current = null;
      }
    };
  }, []);

  // 2. データ反映ロジック
  useEffect(() => {
    // planStructureが読み込まれるまで待機
    if (!currentPlan || !univerRef.current || !planStructure) return;

    console.log('[Univer] Updating sheet with plan data...');

    // ICommandServiceを取得
    // ※ Univerの型定義によっては .get() が直接呼べない場合があるため、その場合は any キャストで回避します
    // @ts-ignore
    const commandService = univerRef.current.__getInjector().get(ICommandService);
    if (!commandService) return;

    const dataKeys = Object.keys(currentPlan.raw_data);

    dataKeys.forEach((key) => {
      const textValue = currentPlan.raw_data[key];
      // 値がない場合はスキップ
      if (textValue === undefined || textValue === null) return;

      let mapping: CellMapping | null = null;

      // 修正: ヘルパー関数を使って階層構造から検索
      const matchingCard = findItemByKey(planStructure, key);
      
      if (matchingCard && matchingCard.targetCell) {
        mapping = parseCellAddress(matchingCard.targetCell);
      }

      if (!mapping && CELL_MAPPING[key]) {
        mapping = CELL_MAPPING[key];
      }

      if (mapping) {
        const { r, c } = mapping;
        
        commandService.executeCommand(SetRangeValuesCommand.id, {
          unitId: 'workbook-01',
          subUnitId: 'sheet-01',
          range: { startRow: r, startColumn: c, endRow: r, endColumn: c },
          value: { 
            v: textValue,
            // 長文用に折り返し設定などを入れる場合はここに追加
            // s: {
            //   tb: WrapStrategy.WRAP, // tb = Text Wrap (折り返し)
            //   // vt: 1, // (任意) 垂直方向の配置: 1=Middle, 0=Top, 2=Bottom
            // }
           },
        });
      }
    });

  }, [currentPlan, planStructure]); // planStructureの変更も監視

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '8px', background: '#fff', borderBottom: '1px solid #ddd' }}>
        <strong>Canvas (Univer)</strong>
      </div>
      <div ref={containerRef} style={{ flex: 1, overflow: 'hidden' }} />
    </div>
  );
};

export default UniverSheet;