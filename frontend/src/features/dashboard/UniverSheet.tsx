import React, { useEffect, useRef } from 'react';
import '@univerjs/design/lib/index.css';
import '@univerjs/ui/lib/index.css';
import '@univerjs/sheets-ui/lib/index.css';

import { Univer, LocaleType, UniverInstanceType, ICommandService, WrapStrategy } from '@univerjs/core';
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
// ユーティリティと型定義を追加インポート
import { CELL_MAPPING, parseCellAddress, CellMapping } from '../../api/types';

const UniverSheet: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const univerRef = useRef<Univer | null>(null);
  
  // Contextから currentPlan と cards (ユーザー定義設定) を取得
  const { currentPlan, cards } = usePlanContext();

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

  // 2. データ反映ロジック (動的マッピング対応)
  useEffect(() => {
    if (!currentPlan || !univerRef.current) return;

    console.log('[Univer] Updating sheet with plan data...');

    // ICommandServiceを取得
    // ※ Univerの型定義によっては .get() が直接呼べない場合があるため、その場合は any キャストで回避します
    // @ts-ignore
    const commandService = univerRef.current.__getInjector().get(ICommandService);
    if (!commandService) return;

    // 現在生成されているデータのキー一覧を取得
    const dataKeys = Object.keys(currentPlan.raw_data);

    dataKeys.forEach((key) => {
      const textValue = currentPlan.raw_data[key];
      // 値がない場合はスキップ
      if (textValue === undefined || textValue === null) return;

      // 書き込み先の座標を決定する変数
      let mapping: CellMapping | null = null;

      // 【優先順位 1】 カード設定 (ユーザー定義)
      // そのデータのキー(targetKey)を持つカードを探す
      const matchingCard = cards.find(c => c.targetKey === key);
      
      // カードが見つかり、かつ有効なセル指定("A1"など)がある場合
      if (matchingCard && matchingCard.targetCell) {
        mapping = parseCellAddress(matchingCard.targetCell);
      }

      // 【優先順位 2】 デフォルトマッピング (types.ts)
      // カード設定がない、またはセル指定が無効だった場合のフォールバック
      if (!mapping && CELL_MAPPING[key]) {
        mapping = CELL_MAPPING[key];
      }

      // マッピングが確定できれば書き込む
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

  }, [currentPlan, cards]); // cardsの変更も監視し、設定が変われば即再描画

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