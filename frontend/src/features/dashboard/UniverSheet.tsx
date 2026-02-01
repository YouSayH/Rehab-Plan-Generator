import React, { useEffect, useRef } from 'react';
import '@univerjs/design/lib/index.css';
import '@univerjs/ui/lib/index.css';
import '@univerjs/sheets-ui/lib/index.css';

import { Univer, LocaleType, UniverInstanceType } from '@univerjs/core';
import { defaultTheme } from '@univerjs/design';
import { UniverDocsPlugin } from '@univerjs/docs';
import { UniverDocsUIPlugin } from '@univerjs/docs-ui';
import { UniverFormulaEnginePlugin } from '@univerjs/engine-formula';
import { UniverRenderEnginePlugin } from '@univerjs/engine-render';
import { UniverSheetsPlugin } from '@univerjs/sheets';
import { UniverSheetsFormulaPlugin } from '@univerjs/sheets-formula';
import { UniverSheetsUIPlugin } from '@univerjs/sheets-ui';
import { UniverUIPlugin } from '@univerjs/ui';

const UniverSheet: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const univerRef = useRef<Univer | null>(null);

  useEffect(() => {
    if (!containerRef.current || univerRef.current) return;

    // 1. Univer本体の初期化
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
            0: {
              0: { v: 'リハビリテーション総合実施計画書' },
            }
          }
        }
      }
    });

    univerRef.current = univer;

    // クリーンアップ処理
    return () => {
      const univerInstance = univerRef.current;
      if (univerInstance) {
        // Reactのレンダリングサイクルと衝突しないよう、破棄処理を次のタイミングに遅らせます
        setTimeout(() => {
          try {
            univerInstance.dispose();
          } catch (e) {
            console.warn('Univer cleanup warning:', e);
          }
        }, 10); // 10ms待機
        univerRef.current = null;
      }
    };
  }, []);

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