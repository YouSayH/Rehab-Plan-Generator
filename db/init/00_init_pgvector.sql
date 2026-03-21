-- File: db/init/00_init_pgvector.sql
--
-- Summary:
-- PostgreSQLコンテナの初回起動時に自動実行される初期化SQLスクリプト。
-- RAG（検索拡張生成）や類似患者検索の要となるベクトル検索機能を利用するために、`pgvector` 拡張機能をデータベース内で有効化します。また、データベースのデフォルトタイムゾーンを日本時間（Asia/Tokyo）に設定しています。
--
-- Tags: Database, SQL, Initialization, pgvector, Setup

-- pgvector拡張機能の有効化
CREATE EXTENSION IF NOT EXISTS vector;

-- タイムゾーンの設定
SET timezone TO 'Asia/Tokyo';