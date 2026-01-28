# 開発者ガイドライン (Contribution Guidelines)

このプロジェクト（Rehab Plan Generator）の開発に参加していただきありがとうございます。
本プロジェクトは、医療情報を扱うシステムであり、かつ複数人での開発を行うため、品質とセキュリティを担保するためのルールを定めています。

開発に着手する前に、必ず本ドキュメントを一読してください。

---

## 🚩 最重要原則 (Core Principles)

1.  **プライバシー絶対遵守 (Privacy First)**
    * **Backend/DB/AIにいかなる個人特定情報（PHI: 氏名、住所、生年月日）も保存・送信してはいけません。**
    * Backendでの処理は常にハッシュ化された `hash_id` を使用してください。実名の扱いはFrontend（ブラウザメモリ）のみに限定されます。

2.  **責任あるAI活用 (Responsible AI)**
    * LLMによるコーディングを推奨しますが、**「生成されたコードの動作と副作用を完全に理解し、説明できる状態」**でコミットしてください。
    * AIの出力を盲目的にコピペすることは禁止です。

---

## 🛠 開発フロー (Workflow)

GitHub Flowに基づき、以下の手順で開発を進めます。

1.  **Issueの作成**
    * タスクに着手する前にIssueを作成し、WBS（作業内容、入力、出力）を定義してください。
2.  **ブランチ作成**
    * `main` ブランチから機能ブランチを作成します。
    * 命名規則: `feature/{Issue番号}-{簡易説明}`
    * 例: `feature/12-add-fim-chart`, `fix/25-typo-correction`
3.  **実装 & テスト**
    * ローカル環境でコードを書き、テストを通します。
4.  **Pull Request (PR) 作成**
    * 実装完了後、`main` に向けてPRを作成します。
    * PRテンプレートに従い、変更内容と「検証方法」を記載してください。
5.  **レビュー & マージ**
    * 他のメンバー1名以上の承認（Approve）を得てからマージします。

### コミットメッセージ規約 (Conventional Commits)
コミットログの可読性を高めるため、以下のプレフィックスを付けてください。

* `feat:` 新機能
* `fix:` バグ修正
* `docs:` ドキュメントのみの変更
* `style:` コードの意味に影響しないフォーマット変更
* `refactor:` バグ修正や機能追加を含まないコード変更
* `test:` テストの追加・修正
* `chore:` ビルドプロセスやツール設定の変更

---

## 🤖 AI・LLM活用ガイドライン

* **プロンプト入力の注意:**
    * **厳禁:** 実際の患者データ、APIキー、パスワードをプロンプトに入力すること。
    * 必ず「ダミーデータ」や「匿名化された構造」を使用してください。
* **コード品質:**
    * AIが生成したコードには、必要に応じて「なぜそうするのか」というコメント（意図）を日本語で追記してください。
    * 複雑なロジックの場合、AIにDocstringも生成させてください。

---

## 📏 コーディング規約 (Coding Standards)

### 共通
## 命名規則 (Naming Conventions)

言語ごとの標準（PEP8, TS Style Guide）に準拠しつつ、**医療ドメイン特有の混乱**を避けるルールを設けます。

| 対象 | 規則 | 例 | 備考 |
| --- | --- | --- | --- |
| **Python変数/関数** | `snake_case` | `calc_fim_score`, `user_id` |  |
| **Pythonクラス** | `PascalCase` | `FimCalculator`, `PatientModel` |  |
| **TS変数/関数** | `camelCase` | `fetchPatientData`, `isOpen` | `is`, `has` 等の接頭辞を推奨 |
| **Reactコンポーネント** | `PascalCase` | `PatientCard`, `FimChart` | ファイル名も `PatientCard.tsx` |
| **定数 (全言語)** | `UPPER_SNAKE` | `MAX_RETRY_COUNT`, `API_URL` |  |
| **DBテーブル/カラム** | `snake_case` | `patients_view`, `hash_id` | PostgreSQL標準 |

### ⚠️ プロジェクト特有の命名ルール

* **IDの明確化:**
* 単に `id` と書かない。
* 実名を含む内部ID（もしあれば）: `internal_uid`
* ハッシュ化された公開ID: `hash_id` (または `public_uid`)
* これを取り違えると**情報漏洩**に繋がるため、変数名で厳密に区別する。


### Backend (Python / FastAPI)
* **フォーマッター:** `Ruff` を使用し、PEP8に準拠させてください。
* **型ヒント:** 関数の引数と戻り値には必ず型ヒント（Type Hints）を記述してください。
* **Docstring:** 公開関数・クラスにはGoogle Style等のDocstringを記述してください。

### Frontend (React / TypeScript)
* **フォーマッター:** `Prettier` を使用してください。
* **型安全性:** `any` 型の使用は原則禁止です。型定義が見つからない場合は、適切なInterfaceを定義するか、コメントで理由を説明してください。
* **コンポーネント:** 関数コンポーネント（Functional Components）とHooksを使用してください。

---

## ✅ テスト・品質保証 (Testing & QA)

バグの手戻りを防ぐため、以下のテスト方針に従ってください。

### テスト範囲
1.  **Backend (Pytest):**
    * `services/` 以下のビジネスロジック（計算、判定など）は**必須**で単体テストを書いてください。
    * APIエンドポイントは正常系・異常系の結合テストの実装を推奨します。
2.  **Frontend:**
    * 複雑なロジックを持つ関数（utils等）はテストを書いてください。UIコンポーネントのテストは任意です。

### 実行ルール
* PRを出す前に、必ずローカル環境で全テストが通過することを確認してください。
* バグ修正時は、**「バグを再現するテストケース」**を作成してから修正を行ってください（回帰テスト）。

---

## 🗄 データベース管理 (Database)

* **マイグレーション:**
    * DBスキーマの変更は必ず **Alembic** を使用して行ってください。
    * 直接SQLコマンド（`CREATE`, `ALTER`）を実行することは禁止です。
* **手順:**
    1.  SQLAlchemyモデルを修正
    2.  `alembic revision --autogenerate -m "変更内容"`
    3.  生成されたファイルをコミット

---

## 🔒 セキュリティ・環境設定

* **機密情報:**
    * APIキー、DBパスワード等は `.env` ファイルで管理してください。
    * **`.env` ファイルは絶対にGitにコミットしないでください（`.gitignore` 必須）。**
* **依存関係:**
    * 新しいライブラリを追加した場合は、必ず `pyproject.toml` (または `requirements.txt`) を更新してください。

---
Copyright © 2026 Rehab Plan Generator Project Team