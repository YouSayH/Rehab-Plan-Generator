# Rehab Plan Generator (RPG)

電子カルテ連携、予後予測、類似症例検索を備えた「リハビリテーション総合実施計画書」作成支援システム。
プライバシー保護（HashID運用）と、閉域網での運用（オフライン対応）を前提とした設計になっています。

## 🚀 技術スタック

* **Frontend:** React 19, TypeScript, Vite, Univer (Spreadsheet)
* **Backend:** Python 3.11, FastAPI, SQLAlchemy (Async), LangChain (Planned)
* **Database:** PostgreSQL 16 + pgvector (Vector Search)
* **Infrastructure:** Docker, Nginx

## 🛠️ 環境構築 & 起動

Docker Desktop がインストールされている必要があります。

### 1. 開発環境 (Development)
`compose.override.yaml` が自動的に読み込まれ、ホットリロード有効・ポート開放状態で起動します。

  ```bash
  # プロジェクトのクローン（初回のみ）
  git clone <repository-url>
  cd rehab-plan-generator

  # 開発用起動 (初回や構成変更時は --build を推奨)
  docker compose up --build

  ```

* **Frontend (App):** http://localhost (Nginx経由)
    * ※開発用ポート: http://localhost:3000 (React直接)


* **Backend API:** http://localhost:8000/docs (Swagger UI)

### 2. 本番環境 / デプロイ (Production)

`compose.override.yaml` を無視し、セキュアな設定（`compose.yaml`のみ）で起動します。
外部へのポート公開はNginx (80/443) のみに制限され、ソースコードはイメージ内包のものを使用します。

```bash
# 本番用起動 (オーバーライドファイルを無視して起動)
docker compose -f compose.yaml up -d --build

```

## 📁 ディレクトリ構成
  ```Text
  Rehab_Plan_Gen/
  ├──.github/                 # 🐙 GitHub設定
  │   └──workflows/           # CI/CD設定
  │    
  ├──backend/                 # 🐍 Python (FastAPI)
  │   ├──app/                 # アプリケーションコード本体
  │   │   ├── adapters/        # 🔌 Interface Adapters (腐敗防止層)
  │   │   │   ├── llm/         # LLMの切り替え (Gemini, Ollama...)
  │   │   │   ├── ehr/         # 電子カルテ連携 (Vendor A, CSV...)
  │   │   │   └── storage/     # ファイル保存 (Local, S3...)
  │   │   │    
  │   │   ├──api/             # 🌐 Web Interface Layer (FastAPI Router)
  │   │   │   ├──v1/          # API Versioning
  │   │   │   └──dependencies.py # DIコンテナ定義
  │   │   │
  │   │   ├──core/            # 設定・共通部品 (Config, Logging, Security)
  │   │   │
  │   │   ├──infrastructure/  # 🏗️ Frameworks & Drivers (詳細実装)
  │   │   │   ├── db/          # SQLAlchemy Models, Session
  │   │   │   │   └──models.py
  │   │   │   └── repositories/# データアクセス実装
  │   │   │    
  │   │   ├──schemas/
  │   │   │   ├──__init__.py
  │   │   │   └──schemas.py
  │   │   │
  │   │   ├──usecases/        # 🧠 Application Business Rules (フレームワーク非依存)
  │   │   │   ├──plan_generation.py
  │   │   │   └──prediction.py
  │   │   │
  │   │   └──main.py          # エントリーポイント
  │   │
  │   ├──migrations/          # Alembicマイグレーションスクリプト
  │   │   ├──versions/
  │   │   │   └──3b7d24c1aae5_initial_migration.py
  │   │   │
  │   │   ├──env.py
  │   │   ├──README
  │   │   └──script.py.mako
  │   │
  │   ├── ml_engine/           # 🤖 AIモデル学習・推論専用 (APIとは分離)
  │   │   ├── training/        # LightGBM等の学習スクリプト
  │   │   ├── models/          # 学習済みモデルファイル (.pkl, .bin)
  │   │   └── notebooks/       # 実験用Jupyter Notebook
  │   │    
  │   ├──requirements/        # 📦 ライブラリ定義 (環境別)
  │   │   ├──_base.txt        # 共通 (FastAPI, SQLAlchemy等)
  │   │   ├──cloud_llm.txt    # オンライン・軽量版 (GenAI等)
  │   │   └──local_gpu.txt    # オフライン・GPU用 (Torch+CUDA等)
  │   │
  │   ├──tests/               # ✅ テストコード (Pytest)
  │   │   ├──integration/     # 結合テスト (api, db)
  │   │   └──unit/            # 単体テスト (usecases, adapters)
  │   │    
  │   ├──alembic.ini          # DBマイグレーション設定
  │   ├──Dockerfile
  │   └──pyproject.toml       # 依存関係管理 (uv / poetry)
  │
  ├──contracts/               # 🤝 APIスキーマ・仕様書 (The Contract)
  │   ├──architecture.md      # アーキテクチャ図・決定事項
  │   └──openapi.yaml         # フロントとバックをつなぐ契約書 (SSOT)
  │
  ├──data/                    # 📄 データ・資料置き場
  │   ├──docs/                # 設計書や仕様書
  │   └──samples/             # テスト用Excel/CSV
  │    
  ├── db/                      # 🐘 データベース関連
  │   └── init/                # コンテナ初回起動用SQL
  │       └── 00_init_pgvector.sql # pgvector有効化など
  │
  ├──frontend/                # ⚛️ React + TypeScript
  │   ├──public/
  │   │   └──libs/            # 📦 オフライン用ライブラリ
  │   │       └──Univer/  # スプレッドシート(Univer) JS/CSS一式
  │   │        
  │   ├──src/                 # ソースコード
  │   │   ├──adapters/        # 🔌 APIクライアント (自動生成コード等)
  │   │   ├──components/      # 共通UIコンポーネント
  │   │   ├──features/        # 機能単位のモジュール (画面+ロジック)
  │   │   │   ├──dashboard/
  │   │   │   └──editor/
  │   │   │
  │   │   ├──hooks/           # Custom Hooks
  │   │   ├──types/           # 型定義
  │   │   ├──utils/           # ユーティリティ関数
  │   │   │
  │   │   ├──App.tsx
  │   │   ├──main.tsx
  │   │   ├──tsconfig.json
  │   │   └──tsconfig.node.json
  │   │
  │   ├──Dockerfile
  │   ├──index.html
  │   ├──package.json
  │   └──vite.config.ts
  │
  ├──logs/                    # 📝 ログ出力先 (Docker Mount)
  │   ├──app/                 # アプリログ
  │   ├──db/                  # DBログ
  │   └──nginx/               # アクセスログ
  │
  ├──nginx/                   # 🌐 Webサーバー (リバースプロキシ)
  │   ├──Dockerfile
  │   └──conf.d/
  │       └──default.conf     # ルーティング設定
  │
  ├──ops/                     # 🛠 運用・構成管理 (Operations)
  │   ├── compose.prod.yaml    # 本番サーバー用設定
  │   ├── compose.gpu.yaml     # GPUサーバー用設定
  │   └── scripts/             # 便利スクリプト (DBバックアップ, Restore等)
  │
  ├──tools/                   # 🛠 開発支援ツール
  │   ├──db_seeder/           # ダミーデータ生成スクリプト
  │   └──codegen/             # OpenAPIから型定義を生成するスクリプト
  │
  ├──.dockerignore
  ├──.env.example             # 🔐 環境変数のサンプル (Git管理対象)
  ├──.env                     # 🔐 実際の環境変数 (Git除外)
  ├──.gitignore
  ├──compose.yaml             # 🐳 【共通/本番】ベースとなるDocker設定
  ├──compose.override.yaml    # 🐳 【開発用】ローカル開発用の差分設定
  ├──CONTRIBUTING.md          # 📜 開発ルール・ガイドライン
  ├──README.md
  └──YOUKENTEIGI.md
  ```

## 🤝 開発ルール

`CONTRIBUTING.md` を参照してください。


## 🐘 データベース・マイグレーション (DB Migration)

本プロジェクトは **Alembic** を使用してデータベースのスキーマ変更を管理しています。
テーブル定義の変更は、直接SQLを実行せず、必ず以下の手順で行ってください。

### 1. テーブル構造を変更する場合
`backend/app/infrastructure/db/models.py` を編集した後、以下のコマンドを実行してマイグレーションファイル（変更の設計図）を作成します。

  ```bash
  # マイグレーションファイルの作成
  # -m "メッセージ" は変更内容がわかるように記述してください
  docker compose run --rm backend alembic revision --autogenerate -m "Add blood_type column to patients"
  ```

コマンド実行後、`backend/migrations/versions/` に生成された `.py` ファイルを確認してください。
**注意:** `pgvector` などの特殊な型を使用した場合、生成されたファイルに `import pgvector` が抜けていることがあるため、手動で追記が必要です。

### 2. 変更をDBに適用する場合

作成されたマイグレーションファイルを実際のデータベースに反映させます。

  ```bash
  # 最新の状態（head）まで更新する
  docker compose run --rm backend alembic upgrade head
  ```

### 3. DBをリセットしたい場合（開発用）

データを全て消して、最初から作り直したい場合の手順です。

  ```bash
  # 1. コンテナとボリューム（データの実体）を削除
  docker compose down -v

  # 2. コンテナを再起動（DBが空の状態で立ち上がる）
  docker compose up -d

  # 3. マイグレーションを最初から適用
  docker compose run --rm backend alembic upgrade head
  ```



### 4. 便利なコマンド集

- **現在のバージョン確認**
  今どのマイグレーションまで適用されているか確認します。
  ```bash
  docker compose run --rm backend alembic current
  ```

* **履歴（ログ）の確認**
これまでのマイグレーション履歴を表示します。
  ```bash
  docker compose run --rm backend alembic history
  ```


* **直前の変更を取り消す (Downgrade)**
一つ前のバージョンに戻します（マイグレーションに失敗した時などに使用）。
  ```bash
  docker compose run --rm backend alembic downgrade -1
  ```



### 5. DBクライアントからの接続（開発用）

DBeaverやTablePlusなどのGUIツールでデータベースの中身を確認したい場合の設定情報です。

* **Host**: `localhost`
* **Port**: `5432`
* **Database**: `rehab_db` (または .env で設定した名前)
* **User**: `user`
* **Password**: `password`

※ ポート `5432` は開発モード（`compose.override.yaml` 適用時）のみ `127.0.0.1` に公開されます。本番起動時は外部から接続できません。

### 6. よくあるエラーと対処

#### Q. `NameError: name 'pgvector' is not defined`

**原因:** マイグレーションファイルで `pgvector` がインポートされていません。
**対処:** `backend/migrations/versions/` 内の該当ファイルを開き、上部に `import pgvector` を追記してください。

#### Q. `alembic` コマンドが見つからない

**原因:** Dockerコンテナの外でコマンドを実行しているか、`docker compose` の接頭辞を忘れています。
**対処:** 必ず `docker compose run --rm backend ...` を付けて実行してください。





## License

Private / Proprietary
