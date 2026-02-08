import React, { useEffect, useRef, useState } from 'react';
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

// @ts-ignore
import ExcelJS from 'exceljs';
import { Save, FileSpreadsheet, Download, RefreshCw, FileDown } from 'lucide-react';

import { usePlanContext } from './PlanContext';
import { ApiClient, TemplateRead } from '../../api/client';
import { CELL_MAPPING, parseCellAddress, CellMapping, PlanStructure, PlanItem, ValueMapping } from '../../api/types';

const UniverSheet: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const univerRef = useRef<Univer | null>(null);
  const workbookRef = useRef<any>(null); 
  
  const [workbookId, setWorkbookId] = useState<string>('');
  // インスタンス再生成を検知するためのバージョンキーを追加
  const [univerVersion, setUniverVersion] = useState(0);

  const { currentPlan, planStructure, fieldConfigs, patientData } = usePlanContext();
  const [templates, setTemplates] = useState<TemplateRead[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // ---------------------------------------------------------------------------
  // Restore Map & Helpers
  // ---------------------------------------------------------------------------
  // 自動入力前の値を保持するマップ (Undo用)
  // workbookId も保持して、シート切り替え時に履歴が無効であることを検知できるようにする
  const restoreMapRef = useRef<Map<string, { cellId: string, value: any, workbookId: string }>>(new Map());

  // ユーティリティ: パスから値を取得
  const getValueByPath = (obj: any, path: string) => path.split('.').reduce((acc, part) => acc && acc[part], obj);

  // ユーティリティ: 値変換
  const transformValue = (rawValue: any, mappings: ValueMapping[]) => {
    const strValue = String(rawValue);
    if (!mappings || mappings.length === 0) return rawValue;
    const found = mappings.find(m => m.from === strValue || m.from.toLowerCase() === strValue.toLowerCase());
    return found ? found.to : rawValue;
  };

// ---------------------------------------------------------------------------
  // 1. ExcelJS -> Univer 変換ロジック (Styles & Data)
  // ---------------------------------------------------------------------------
  
  // ARGBカラー(FF000000) を Hex(#000000) に変換
  const argbToHex = (argb: string | undefined): string | undefined => {
    if (!argb) return undefined;
    // 8桁 (Alpha付き) の場合
    if (argb.length === 8) {
      return '#' + argb.substring(2);
    }
    return '#' + argb;
  };

  // 枠線のスタイル変換
  const convertBorder = (border: Partial<ExcelJS.Border> | undefined) => {
    if (!border || !border.style) return undefined;
    // Univerのボーダー定数に合わせて調整 (簡易マッピング)
    // 0:none, 1:thin, 8:medium, 11:thick ...
    let style = 1;
    if (border.style === 'medium') style = 8;
    if (border.style === 'thick') style = 11;
    if (border.style === 'dotted') style = 3;
    if (border.style === 'dashed') style = 4;
    
    return { 
      s: style, 
      cl: { rgb: border.color && border.color.argb ? argbToHex(border.color.argb) : '#000000' } 
    };
  };

  // "A1:B2" 形式の文字列をインデックスに変換
  const decodeRange = (rangeStr: string) => {
    // 簡易的なパース (正規表現で分割)
    const match = rangeStr.match(/([A-Z]+)([0-9]+):([A-Z]+)([0-9]+)/);
    if (!match) return null;

    const colToIndex = (colStr: string) => {
      let num = 0;
      for (let i = 0; i < colStr.length; i++) {
        num = num * 26 + (colStr.charCodeAt(i) - 64);
      }
      return num - 1; // 0-indexed
    };

    return {
      startColumn: colToIndex(match[1]),
      startRow: parseInt(match[2]) - 1,
      endColumn: colToIndex(match[3]),
      endRow: parseInt(match[4]) - 1
    };
  };

const transformExcelJSToUniver = (workbook: ExcelJS.Workbook) => {
  const sheets: Record<string, any> = {};
  const sheetOrder: string[] = [];

  workbook.worksheets.forEach((worksheet, index) => {
    const sheetId = `sheet-${index}`; // 一意のIDを生成
    console.log(`[Import] Converting sheet [${index}]:`, worksheet.name);

    const sheetData: any = {
      id: sheetId,
      name: worksheet.name,
      cellData: {},
      rowData: {},
      columnData: {},
      mergeData: [],
      rowCount: Math.max(worksheet.rowCount + 20, 50),
      columnCount: Math.max(worksheet.columnCount + 10, 20),
    };

    // --- A. 列幅 ---
    worksheet.columns?.forEach((col, colIdx) => {
      if (col.width) sheetData.columnData[colIdx] = { w: col.width * 7 };
    });

    // --- B. 行とセル (既存のループ処理をここに含める) ---
    worksheet.eachRow({ includeEmpty: true }, (row, rowNumber) => {
      const r = rowNumber - 1;
      if (row.height) sheetData.rowData[r] = { h: row.height };

      row.eachCell({ includeEmpty: true }, (cell, colNumber) => {
        const c = colNumber - 1;
        if (!sheetData.cellData[r]) sheetData.cellData[r] = {};
        
        // 値の取得 (フリガナ混入を回避)
        let cellValue: any = null;
        let cellFormula: string | undefined = undefined;

        // cell.value がオブジェクトかどうかチェック
        if (cell.value && typeof cell.value === 'object') {
          // 1. 数式 (Formula)
          if ('formula' in cell.value) {
            cellFormula = (cell.value as any).formula;
            const result = (cell.value as any).result;
            
            // 計算結果がエラーオブジェクト({ error: '#DIV/0!' })の場合などの対処
            if (result && typeof result === 'object') {
               if ('error' in result) {
                 cellValue = result.error;
               } else {
                 // その他のオブジェクトならJSON化してデバッグ表示（または空文字）
                 cellValue = JSON.stringify(result); 
               }
            } else {
               cellValue = result;
            }
          } 
          // 2. リッチテキスト (Rich Text)
          else if ('richText' in cell.value && Array.isArray((cell.value as any).richText)) {
            cellValue = (cell.value as any).richText.map((t: any) => t.text).join('');
          } 
          // 3. ハイパーリンク (Hyperlink)
          else if ('hyperlink' in cell.value) {
             cellValue = (cell.value as any).text || (cell.value as any).hyperlink;
          } 
          // 4. エラー値 (Shared Formulaの結果などで直接Errorが入る場合など)
          else if ('error' in cell.value) {
             cellValue = (cell.value as any).error;
          }
          // 5. その他
          else {
             // 想定外のオブジェクトが来た場合は、[object Object]にならないようJSON化
             // Dateオブジェクトの場合は文字列化
             if (cell.value instanceof Date) {
                cellValue = cell.value.toString();
             } else {
                cellValue = JSON.stringify(cell.value); 
             }
          }
        } else {
          // 通常の値 (String, Number, Boolean, null)
          cellValue = cell.value;
        }

        // スタイル変換
        const style: any = {};
        const s = cell.style;

        // Font
        if (s.font) {
            if (s.font.bold) style.bl = 1;
            if (s.font.italic) style.it = 1;
            if (s.font.size) style.fs = s.font.size;
            
            // フォント名があればそれを使い、なければ 'ＭＳ Ｐゴシック' を強制適用
            style.ff = s.font.name || 'ＭＳ Ｐゴシック';

            if (s.font.color && s.font.color.argb) {
                const hex = argbToHex(s.font.color.argb);
                if (hex) style.cl = { rgb: hex };
            }
        } else {
            // fontプロパティ自体がない場合もデフォルトを適用
            style.ff = 'ＭＳ Ｐゴシック';
        }
        
        // Background (Fill)
        if (s.fill && s.fill.type === 'pattern' && s.fill.fgColor && s.fill.fgColor.argb) {
             const hex = argbToHex(s.fill.fgColor.argb);
             if (hex) style.bg = { rgb: hex };
        }

        // Alignment
        if (s.alignment) {
            // Horizontal
            if (s.alignment.horizontal === 'left') style.ht = 1;
            else if (s.alignment.horizontal === 'center') style.ht = 2;
            else if (s.alignment.horizontal === 'right') style.ht = 3;
            
            // Vertical
            if (s.alignment.vertical === 'top') style.vt = 1;
            else if (s.alignment.vertical === 'middle') style.vt = 2;
            else if (s.alignment.vertical === 'bottom') style.vt = 3;

            // Wrap Text
            if (s.alignment.wrapText) style.tb = 1;
        }

        // Borders
        if (s.border) {
            style.bd = {};
            if (s.border.top) style.bd.t = convertBorder(s.border.top);
            if (s.border.bottom) style.bd.b = convertBorder(s.border.bottom);
            if (s.border.left) style.bd.l = convertBorder(s.border.left);
            if (s.border.right) style.bd.r = convertBorder(s.border.right);
        }
        
        sheetData.cellData[r][c] = {
          v: cellValue, // 既存ロジックで取得した値
          f: cellFormula,
          s: Object.keys(style).length > 0 ? style : undefined
        };
      });
    });

    // --- C. 結合セル (Merge) ---
    // ExcelJSの merges は ['A1:B2', 'C3:C5'] のような形式
    if (worksheet.model.merges) {
      worksheet.model.merges.forEach((rangeStr: string) => {
        const range = decodeRange(rangeStr);
        if (range) sheetData.mergeData.push(range);
      });
    }

    sheets[sheetId] = sheetData;
    sheetOrder.push(sheetId);
  });

  return {
    id: 'workbook-01',
    appVersion: '3.0.0',
    locale: LocaleType.JA_JP,
    name: 'Imported Workbook',
    sheetOrder, // 全シートのID配列
    sheets,     // 全シートのデータオブジェクト
    styles: {}
  };
};
  // ---------------------------------------------------------------------------
  // 2. Univer 初期化
  // ---------------------------------------------------------------------------
  const initUniver = (snapshot?: any) => {
    if (univerRef.current) {
      try { univerRef.current.dispose(); } catch (e) { console.warn(e); }
      univerRef.current = null;
      workbookRef.current = null;
      if (containerRef.current) containerRef.current.innerHTML = '';
      
      // ワークブック切り替え時は復元履歴をクリアする
      // これをしないと、新しいシートに対して「前のシートの復元値」を適用しようとしたり、
      // 逆に「既に書き込み済み」と誤判定して書き込まれなかったりします。
      restoreMapRef.current.clear();
    }

    const defaultSnapshot = {
      id: 'workbook-01',
      appVersion: '3.0.0',
      locale: LocaleType.JA_JP,
      name: 'リハビリ計画書',
      sheetOrder: ['sheet-01'],
      sheets: {
        'sheet-01': {
          id: 'sheet-01',
          name: '様式23',
          rowCount: 50,
          columnCount: 20,
          cellData: {
            0: { 0: { v: 'リハビリテーション総合実施計画書' } },
            11: { 0: { v: '短期目標:' } },
            13: { 0: { v: '長期目標:' } },
            15: { 0: { v: 'プログラム:' } },
            17: { 0: { v: 'リスク管理:' } },
          }
        }
      }
    };

    const data = snapshot || defaultSnapshot;

    const univer = new Univer({
      theme: defaultTheme,
      locale: LocaleType.JA_JP,
      locales: { [LocaleType.JA_JP]: {} },
    });

    univer.registerPlugin(UniverRenderEnginePlugin);
    univer.registerPlugin(UniverFormulaEnginePlugin);
    univer.registerPlugin(UniverUIPlugin, { container: containerRef.current!, header: true, footer: true });
    univer.registerPlugin(UniverDocsPlugin, { hasScroll: false });
    univer.registerPlugin(UniverDocsUIPlugin);
    univer.registerPlugin(UniverSheetsPlugin);
    univer.registerPlugin(UniverSheetsUIPlugin);
    univer.registerPlugin(UniverSheetsFormulaPlugin);

    const unit = univer.createUnit(UniverInstanceType.UNIVER_SHEET, data);
    setWorkbookId(unit.getUnitId());
    workbookRef.current = unit; 
    univerRef.current = univer;

    // バージョンを更新して useEffect を強制発火させる
    setUniverVersion(v => v + 1);
  };

  useEffect(() => {
    if (!containerRef.current) return;
    initUniver();
    loadTemplates();
    return () => {
      if (univerRef.current) {
        try { univerRef.current.dispose(); } catch (e) {}
        univerRef.current = null;
        workbookRef.current = null;
      }
    };
  }, []);

  // ---------------------------------------------------------------------------
  // 3. データ反映ロジック
  // ---------------------------------------------------------------------------
  const findItemByKey = (structure: PlanStructure, key: string): PlanItem | undefined => {
    for (const node of structure) {
      if (node.type === 'item' && node.targetKey === key) return node;
      if (node.type === 'group') {
        const found = node.children.find(child => child.targetKey === key);
        if (found) return found;
      }
    }
    return undefined;
  };

  useEffect(() => {
    if (!currentPlan || !univerRef.current || !planStructure) return;

    // @ts-ignore
    const commandService = univerRef.current.__getInjector().get(ICommandService);
    if (!commandService) return;

    const dataKeys = Object.keys(currentPlan.raw_data);

    dataKeys.forEach((key) => {
      const textValue = currentPlan.raw_data[key];
      if (textValue === undefined || textValue === null) return;

      let mapping: CellMapping | null = null;
      const matchingCard = findItemByKey(planStructure, key);
      
      if (matchingCard && matchingCard.targetCell) {
        mapping = parseCellAddress(matchingCard.targetCell);
      }
      if (!mapping && CELL_MAPPING[key]) {
        mapping = CELL_MAPPING[key];
      }

      if (mapping) {
        const { r, c } = mapping;
        const activeWorkbook = workbookRef.current; 
        // 最初のシートIDを取得
        const targetSheetId = activeWorkbook?.getSheets()[0]?.getSheetId() || 'sheet-01';

        commandService.executeCommand(SetRangeValuesCommand.id, {
          unitId: workbookId || 'workbook-01',
          subUnitId: targetSheetId, 
          range: { startRow: r, startColumn: c, endRow: r, endColumn: c },
          value: { v: textValue },
        });
      }
    });

  }, [currentPlan, planStructure, workbookId]);

  // ---------------------------------------------------------------------------
  // 4. [NEW] 患者データのリアルタイム反映 & 復元ロジック
  // ---------------------------------------------------------------------------
  useEffect(() => {
    console.log('[UniverSheet] Data Reflection Effect Triggered', { 
      workbookId, 
      univerVersion, // ログに追加
      hasUniver: !!univerRef.current, 
      hasWorkbook: !!workbookRef.current,
      hasPatientData: !!patientData 
    });

    if (!univerRef.current || !workbookRef.current || !patientData || !fieldConfigs) {
      console.log('[UniverSheet] Skipping: Missing dependencies');
      return;
    }

    // @ts-ignore
    const commandService = univerRef.current.__getInjector().get(ICommandService);
    if (!commandService) return;

    const activeWorkbook = workbookRef.current;
    // workbookIdが変わった直後はアクティブシートが正しく取れない場合があるため、unitIdから取得
    const sheet = activeWorkbook.getActiveSheet(); 
    if (!sheet) {
      console.log('[UniverSheet] Skipping: No active sheet');
      return;
    }
    
    // 現在のWorkbookIDと一致しているか確認 (タイミング問題の防止)
    const currentUnitId = activeWorkbook.getUnitId();
    console.log(`[UniverSheet] ID Check: state=${workbookId}, current=${currentUnitId}`);
    
    if (currentUnitId !== workbookId) {
      console.log(`[UniverSheet] Skipping: ID mismatch (State: ${workbookId}, Current: ${currentUnitId})`);
      return;
    }

    const sheetId = sheet.getSheetId();

    Object.keys(fieldConfigs).forEach(path => {
      const config = fieldConfigs[path];
      const rawValue = getValueByPath(patientData, path);
      
      const hasValue = rawValue !== undefined && rawValue !== null;
      const targetCell = config.targetCell ? config.targetCell.toUpperCase() : '';
      
      // 1. 復元処理 (セル指定が変更/解除された場合) 
      const restoreInfo = restoreMapRef.current.get(path);
      
      // ワークブックが変わった場合、古い履歴は無効なので無視（復元しない）
      // 同じワークブック内でセルが変わった場合のみ復元
      if (restoreInfo && restoreInfo.workbookId === workbookId) {
        if (restoreInfo.cellId !== targetCell) {
          const { r, c } = parseCellAddress(restoreInfo.cellId) || { r: -1, c: -1 };
          if (r >= 0) {
            console.log(`[UniverSheet] Restoring cell: ${restoreInfo.cellId}`);
            commandService.executeCommand(SetRangeValuesCommand.id, {
              unitId: workbookId,
              subUnitId: sheetId,
              range: { startRow: r, startColumn: c, endRow: r, endColumn: c },
              value: { v: restoreInfo.value },
            });
          }
          restoreMapRef.current.delete(path);
        }
      } else if (restoreInfo && restoreInfo.workbookId !== workbookId) {
          // ワークブックが変わっていたら、古い履歴は削除
          restoreMapRef.current.delete(path);
      }

      // 2. 書き込み処理
      if (targetCell && hasValue) {
        const mapping = parseCellAddress(targetCell);
        if (mapping) {
          const { r, c } = mapping;
          
          // まだこのワークブックでの履歴がなければ、書き込む前の「現在の値」を保存する (Undo用)
          if (!restoreMapRef.current.has(path)) {
            const currentCellData = sheet.getCell(r, c);
            const originalVal = currentCellData ? currentCellData.v : null;
            
            console.log(`[UniverSheet] Saving original value for ${path} at ${targetCell}:`, originalVal);
            restoreMapRef.current.set(path, { 
                cellId: targetCell, 
                value: originalVal,
                workbookId: workbookId // IDを保存
            });
          }

          // マッピング変換を適用
          const finalValue = transformValue(rawValue, config.mappings);

          // 書き込み実行
          // console.log(`[UniverSheet] Writing ${path} -> ${targetCell}:`, finalValue);
          commandService.executeCommand(SetRangeValuesCommand.id, {
            unitId: workbookId,
            subUnitId: sheetId,
            range: { startRow: r, startColumn: c, endRow: r, endColumn: c },
            value: { v: finalValue },
          });
        }
      }
    });
  }, [patientData, fieldConfigs, workbookId, univerVersion]); // fieldConfigsの変更やシート切り替えで発火

  // ---------------------------------------------------------------------------
  // 5. ハンドラ
  // ---------------------------------------------------------------------------
  const loadTemplates = async () => {
    try {
      const list = await ApiClient.getTemplates();
      setTemplates(list);
    } catch (e) { console.error(e); }
  };

  const handleRegisterTemplate = async () => {
    // 1. Workbookインスタンスの存在確認
    if (!workbookRef.current) {
        alert("ワークブックが初期化されていません。");
        return;
    }
    
    const name = prompt("テンプレート名を入力してください:", "新規テンプレート");
    if (!name) return; // キャンセル

    const description = prompt("テンプレートの説明を入力してください（任意）:", "") || undefined;

    try {
      // 2. 保持しているインスタンスから直接スナップショットを取得
      const snapshot = workbookRef.current.getSnapshot();

      if (snapshot) {
        await ApiClient.saveTemplate(name, snapshot, description);
        alert("テンプレートを登録しました！");
        loadTemplates();
      } else {
        throw new Error("スナップショットが取得できませんでした。");
      }

    } catch (e: any) {
      console.error("Template Save Error:", e);
      alert(`保存に失敗しました。\n詳細: ${e.message || JSON.stringify(e)}`);
    }
  };

  const executeLoadTemplate = async (id: string) => {
    if (!id) return;
    try {
      const template = await ApiClient.getTemplate(Number(id));
      if (template.data) initUniver(template.data);
    } catch (e) { alert("読込失敗"); }
  };

  // ボタンクリック時は、現在選択されているID (selectedTemplateId) を使用
  const handleLoadTemplate = () => executeLoadTemplate(selectedTemplateId);

  // プルダウン変更時は、新しいIDですぐに読み込みを実行
  const handleTemplateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newId = e.target.value;
    setSelectedTemplateId(newId);
    executeLoadTemplate(newId);
  };

  const handleImportExcel = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsLoading(true);

    try {
      const ExcelJSModule = await import('exceljs');
      const ExcelJS = ExcelJSModule.default || ExcelJSModule; // CJS/ESM互換用

      const reader = new FileReader();
      
      reader.onload = async (event) => {
        const buffer = event.target?.result as ArrayBuffer;
        if (!buffer) {
             setIsLoading(false);
             return;
        }

        // ExcelJSでロード
        const workbook = new ExcelJS.Workbook();
        await workbook.xlsx.load(buffer);

        // データ変換を実行
        const univerData = transformExcelJSToUniver(workbook);
        
        if (univerData) {
            initUniver(univerData);
        } else {
            alert("シートデータの読み込みに失敗しました");
        }
        setIsLoading(false);
      };

      reader.onerror = (error) => {
        console.error(error);
        alert("ファイル読み込みエラー");
        setIsLoading(false);
      };

      reader.readAsArrayBuffer(file);

    } catch (error) {
      console.error(error);
      alert("処理エラー: ExcelJSの読み込みに失敗しました");
      setIsLoading(false);
    } finally {
      e.target.value = '';
    }
  };

  const handleDownloadExcel = async () => {
    if (!workbookRef.current) return;

    try {
      const ExcelJSModule = await import('exceljs');
      const ExcelJS = ExcelJSModule.default || ExcelJSModule;
      const workbook = new ExcelJS.Workbook();
      
      // 現在のデータを取得
      const snapshot = workbookRef.current.getSnapshot();

      // 各シートをループしてExcelJSに追加
      // @ts-ignore
      Object.keys(snapshot.sheets).forEach((sheetId) => {
        const sheetData = snapshot.sheets[sheetId];
        const worksheet = workbook.addWorksheet(sheetData.name || 'Sheet1');

        // 1. セルデータの書き出し
        if (sheetData.cellData) {
          Object.keys(sheetData.cellData).forEach((rowKey) => {
            const r = parseInt(rowKey);
            const rowData = sheetData.cellData[rowKey];
            Object.keys(rowData).forEach((colKey) => {
              const c = parseInt(colKey);
              const cell = rowData[colKey];
              
              if (cell && (cell.v !== null && cell.v !== undefined)) {
                // ExcelJSは 1-based index
                const excelCell = worksheet.getCell(r + 1, c + 1);
                excelCell.value = cell.v;
                
                // ※注: ここで cell.s (スタイル) を逆変換して excelCell に適用すれば
                // 色やフォントもエクスポート可能ですが、記述量が多いため今回は「値と結合」のみ実装します
              }
            });
          });
        }

        // 2. 結合セルの適用
        if (sheetData.mergeData) {
          sheetData.mergeData.forEach((merge: any) => {
            // Univer: 0-based { startRow, endRow, startColumn, endColumn }
            // ExcelJS: 1-based, top, left, bottom, right
            worksheet.mergeCells(
              merge.startRow + 1,
              merge.startColumn + 1,
              merge.endRow + 1,
              merge.endColumn + 1
            );
          });
        }
        
        // 3. 列幅の簡易適用 (任意)
        if (sheetData.columnData) {
           Object.keys(sheetData.columnData).forEach((colKey) => {
             const c = parseInt(colKey);
             const width = sheetData.columnData[colKey].w;
             if (width) {
               worksheet.getColumn(c + 1).width = width / 7; // 簡易換算
             }
           });
        }
      });

      // ブラウザでダウンロード発火
      const buffer = await workbook.xlsx.writeBuffer();
      const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `plan_${new Date().toISOString().slice(0,10)}.xlsx`;
      anchor.click();
      window.URL.revokeObjectURL(url);

    } catch (e) {
      console.error(e);
      alert("ダウンロードに失敗しました");
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '8px', background: '#f8fafc', borderBottom: '1px solid #e2e8f0', display: 'flex', gap: '12px', alignItems: 'center' }}>
        <strong>Canvas</strong>
        <select value={selectedTemplateId} onChange={handleTemplateChange} style={{ padding: '4px', border: '1px solid #ccc', borderRadius: '4px' }}>
          <option value="">テンプレートを選択</option>
          {templates.map(t => <option key={t.template_id} value={t.template_id}>{t.name}</option>)}
        </select>
        <button onClick={handleLoadTemplate} disabled={!selectedTemplateId} style={btnStyle}><Download size={14} /> 読込</button>
        <div style={{ width: 1, height: 20, background: '#ccc' }} />
        <label style={btnStyle}>
          {isLoading ? <RefreshCw size={14} className="animate-spin"/> : <FileSpreadsheet size={14} />} 
          Excel取込
          <input type="file" accept=".xlsx" onChange={handleImportExcel} style={{ display: 'none' }} disabled={isLoading} />
        </label>
        <button onClick={handleDownloadExcel} style={btnStyle}>
          <FileDown size={14} /> Excel出力
        </button>
        {/* ボタンラベル変更と右寄せ(marginLeft: auto)を追加 */}
        <button 
          onClick={handleRegisterTemplate} 
          style={{ ...btnStyle, background: '#4f46e5', color: '#fff', border:'none', marginLeft: 'auto' }}
        >
          <Save size={14} /> 現在の状態をテンプレートとして保存
        </button>
      </div>
      <div ref={containerRef} style={{ flex: 1, overflow: 'hidden' }} />
    </div>
  );
};

const btnStyle: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: '4px',
  padding: '6px 12px', borderRadius: '4px', border: '1px solid #cbd5e1',
  background: '#fff', cursor: 'pointer', fontSize: '0.85rem'
};

export default UniverSheet;