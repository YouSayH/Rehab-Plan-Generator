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

// Facade APIが利用可能な場合はこちらを使用 (npm install @univerjs/facade が必要)
// import { FUniver } from '@univerjs/facade';

import { usePlanContext } from './PlanContext';
import { CELL_MAPPING } from '../../api/types';

const UniverSheet: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const univerRef = useRef<Univer | null>(null);
  const { currentPlan } = usePlanContext();

  // 1. Univer初期化
  useEffect(() => {
    if (!containerRef.current || univerRef.current) return;

    const univer = new Univer({
      theme: defaultTheme,
      locale: LocaleType.JA_JP, // 日本語を指定
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
            // マッピング先のセルにラベルを表示しておくと分かりやすいです
            11: { 0: { v: '短期目標:' } }, // Row 11 (B12相当の左)
            13: { 0: { v: '長期目標:' } },
            15: { 0: { v: 'プログラム:' } },
            17: { 0: { v: 'リスク管理:' } },
          }
        }
      }
    });

    univerRef.current = univer;

    // クリーンアップ処理
    return () => {
      if (univerRef.current) {
        // setTimeoutを使わず、コンポーネント破棄時に即座にリソースを開放
        univerRef.current.dispose();
        univerRef.current = null;
      }
    };
  }, []);

  // 2. データ反映ロジック (Commandを使用)
  useEffect(() => {
    if (!currentPlan || !univerRef.current) return;

    console.log('[Univer] Writing data to sheet...', currentPlan.raw_data);

    // ICommandServiceを取得 (DIコンテナから取得)
    // ※ Univerの型定義によっては .get() が直接呼べない場合があるため、その場合は any キャストで回避します
    // @ts-ignore
    const commandService = univerRef.current.__getInjector().get(ICommandService);

    if (!commandService) {
      console.error('CommandService not found');
      return;
    }

    // 各項目をセルに書き込む
    Object.keys(CELL_MAPPING).forEach((key) => {
      const textValue = currentPlan.raw_data[key];
      
      if (textValue) {
        const { r, c } = CELL_MAPPING[key];
        
        // SetRangeValuesCommandを実行
        commandService.executeCommand(SetRangeValuesCommand.id, {
          unitId: 'workbook-01',
          subUnitId: 'sheet-01',
          range: { 
            startRow: r, 
            startColumn: c, 
            endRow: r, 
            endColumn: c 
          },
          value: {
            v: textValue, // 書き込む値
            // 必要に応じてスタイルも指定可能 (例: wrapStrategy: 1 で折り返し)
          },
        });
      }
    });

  }, [currentPlan]);

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