# 作業計画 (Phase 1) — 社内ナレッジ・ドキュメント管理システム

| 項目 | 内容 |
|---|---|
| 文書番号 | KNW-DOC-09 |
| 作成者 | Fable |
| 版数 | 2.0 (レビュー指摘 1〜5 反映。指摘内容は KNW-DOC-10 参照) |
| 対象フェーズ | Phase 1 (MVP) |
| 改訂日 | 2026-07-12 |

---

## 対象範囲

Phase 1 (MVP) のみ。全体の段取りは「11 全体作業計画」を参照。

### Phase 1 のスコープ確定事項 (v1.0 からの変更)

| 項目 | v1.0 | v2.0 (確定) |
|---|---|---|
| admin feature (SC-06) / API #12〜#13 | ファイル一覧に混入 | **Phase 2 へ移動** (kb-sync-func は S3 イベント + スケジュール起動のみ実装) |
| チャット履歴 | #11 とリポジトリが混入 | **保存のみ P1** (chat_repository は作成)。閲覧 API #11 と履歴 UI は Phase 3 |
| RAG フィルタ | 記載なし | **P1 から `visibility = "public"` の固定フィルタを適用** (`kb_filter.py` を先行実装)。P1 で誤って department 文書が登録されても RAG 回答根拠に漏れない安全側設計 |
| `.env` 方式 | `.env.production` をコミット | **GitHub Secrets からワークフローが生成する方式に一本化** (テンプレートのデプロイフロー準拠)。リポジトリには `.env.example` のみ配置、`.env*` は gitignore |
| API ワイヤー形式 | 未定義 | **snake_case を正** とする (axios インターセプターで camelCase 変換)。詳細設計書 (03) の API 例を snake_case に改訂すること |

---

## バックエンド — 新規作成ファイル

### Lambda: documents-func (文書CRUD)

| ファイルパス | 役割 |
|---|---|
| `lambda_functions/documents/lambda_function.py` | エントリポイント・ルーター登録 |
| `lambda_functions/documents/handlers/documents_handler.py` | API #1〜#9 ルーティング |
| `lambda_functions/documents/services/documents_service.py` | 文書CRUD ビジネスロジック |
| `lambda_functions/documents/repositories/documents_repository.py` | DynamoDB操作 |
| `lambda_functions/documents/infrastructure/dynamo_handler.py` | boto3 DynamoDB低レベル |
| `lambda_functions/documents/infrastructure/s3_handler.py` | boto3 S3・presigned URL |
| `lambda_functions/documents/config/settings.py` | 環境変数管理 (Fail-Fast) |
| `lambda_functions/documents/config/constants.py` | 定数 |

### Lambda: chat-func (RAGチャット)

| ファイルパス | 役割 |
|---|---|
| `lambda_functions/chat/lambda_function.py` | エントリポイント |
| `lambda_functions/chat/handlers/chat_handler.py` | API #10 のみ (P1)。#11 は Phase 3 |
| `lambda_functions/chat/services/chat_service.py` | Retrieve (public 固定フィルタ) + Converse。0 件時は LLM を呼ばない (F-304) |
| `lambda_functions/chat/repositories/chat_repository.py` | チャット履歴 **保存のみ** (読み取り API は P3) |
| `lambda_functions/chat/infrastructure/bedrock_handler.py` | boto3 bedrock-agent-runtime / bedrock-runtime |
| `lambda_functions/chat/config/settings.py` | 環境変数管理 (KB_ID / MODEL_ID) |

### Lambda: kb-sync-func (KB同期)

| ファイルパス | 役割 |
|---|---|
| `lambda_functions/kb_sync/lambda_function.py` | エントリポイント |
| `lambda_functions/kb_sync/handlers/kb_sync_handler.py` | **S3 イベント / EventBridge のみ** (#12〜#13 は Phase 2) |
| `lambda_functions/kb_sync/services/kb_sync_service.py` | ingestion job 制御 (実行中ガード + pending フラグ) |
| `lambda_functions/kb_sync/infrastructure/bedrock_handler.py` | boto3 bedrock-agent |
| `lambda_functions/kb_sync/config/settings.py` | 環境変数管理 (KB_ID / DS_ID) |

### 共通Layer (pip依存 + 共有Pythonコード)

| ファイルパス | 役割 |
|---|---|
| `layer/library/Makefile` | SAM Makefile build (pip install + shared コピー) |
| `layer/library/requirements.txt` | aws-lambda-powertools / pydantic 等 (バージョン固定) |
| `layer/library/python/shared/__init__.py` | 共通モジュール |
| `layer/library/python/shared/models.py` | Pydantic モデル (Document / ChatRequest 等) |
| `layer/library/python/shared/auth.py` | claims 解析・ロール/部署抽出 |
| `layer/library/python/shared/ddb.py` | DynamoDB 共通操作 (BaseRepository) |
| `layer/library/python/shared/kb_filter.py` | フィルタ式構築。P1 は `visibility=public` 固定、P2 で orAll 拡張 (単体テスト重点) |
| `layer/library/python/shared/s3util.py` | presigned URL / metadata.json 生成 |

### テスト・設定

| ファイルパス | 役割 |
|---|---|
| `tests/unit/documents/test_documents_service.py` | 文書サービス単体テスト (moto) |
| `tests/unit/chat/test_kb_filter.py` | フィルタ式構築 (P1: public 固定 / P2 拡張分はスケルトンに skip マーク) |
| `tests/unit/chat/test_chat_service.py` | 0 件時 LLM 非呼出 (F-304)・出典整形 |
| `tests/unit/kb_sync/test_kb_sync_service.py` | 実行中ガード・pending 追随 |
| `requirements.txt` | 本番依存関係 (バージョン固定) |
| `requirements-dev.txt` | pytest / moto / ruff / mypy |
| `pyproject.toml` | ruff / mypy 設定 |

---

## バックエンド — 変更ファイル

| ファイルパス | 変更内容 |
|---|---|
| `template.yaml` | 全面書き換え。**明記事項**: Lambda 3本 / DynamoDB main + idempotency / GSI1・GSI2 / Cognito グループ (admin・editor)・カスタム属性 department・`UserPoolTier: LITE` / DataBucket (**presigned PUT 用 CORS 設定含む**) / EventBridge Scheduler (15分) / kb-sync の S3 イベント通知 / **Parameters: `KnowledgeBaseId`・`DataSourceId`** (08 手順で構築後に注入)・KB ARN は `${AWS::Partition}` で構築 |
| `samconfig.toml` | `ProjectName=knowledge`、スタック名 `pjxxx-knowledge-system-dev` / `-prd` |

---

## フロントエンド — 新規作成ファイル

### 設定・エントリポイント

| ファイルパス | 役割 |
|---|---|
| `index.html` | HTMLエントリポイント |
| `vite.config.ts` | Vite設定 (alias) |
| `tsconfig.json` / `tsconfig.app.json` / `tsconfig.node.json` | TypeScript設定 |
| `env.d.ts` | VITE_環境変数型定義 |
| `.env.example` | 環境変数の雛形 (実値なし)。**実 `.env` は CI が Secrets から生成、ローカルは各自作成 (gitignore 対象)** |
| `src/main.ts` | アプリエントリポイント |
| `src/App.vue` | ルートコンポーネント (router-view + レイアウト) |

### 共通基盤

| ファイルパス | 役割 |
|---|---|
| `src/plugins/awsconfig.ts` | Amplify / Cognito 設定 (アプリ初期化系のため plugins/) |
| `src/shared/api/client.ts` | Axios インスタンス・JWT 付与・401 共通処理・camelCase ↔ snake_case インターセプター (**API 横断基盤のため shared/api/ に配置**) |
| `src/router/index.ts` | 各 feature の routes.ts 集約・`meta.requiredRole` ガード |
| `src/shared/stores/useAuthStore.ts` | claims / ロール / 部署 (全 feature で共有) |
| `src/shared/types/common.ts` | 共通型定義 (ApiError / Pagination) |
| `src/shared/index.ts` | バレルファイル |
| `src/layouts/components/AppHeader.vue` | ヘッダー (ロールバッジ・ナビ) |
| `src/shared/views/ForbiddenView.vue` | 403 (requiredRole 不足時の遷移先) |
| `src/shared/views/NotFoundView.vue` | 404 |

### feature: auth

| ファイルパス | 役割 |
|---|---|
| `src/features/auth/views/LoginView.vue` | SC-01 ログイン (Hosted UI リダイレクト) |
| `src/features/auth/routes.ts` | /login ルート定義 |
| `src/features/auth/index.ts` | バレルファイル |

### feature: documents

| ファイルパス | 役割 |
|---|---|
| `src/features/documents/views/DocumentListView.vue` | SC-02 文書一覧・検索 |
| `src/features/documents/views/DocumentDetailView.vue` | SC-03 文書詳細 |
| `src/features/documents/views/DocumentFormView.vue` | SC-04 文書登録・編集 (editor以上) |
| `src/features/documents/components/DocumentTable.vue` | 一覧テーブル |
| `src/features/documents/components/TagFilter.vue` | タグ絞り込み |
| `src/features/documents/components/SearchBar.vue` | キーワード検索 |
| `src/features/documents/components/UploadDropzone.vue` | ファイルアップロード (進捗バー) |
| `src/features/documents/composables/useDocumentUpload.ts` | アップロード2段階コミットロジック |
| `src/features/documents/services/documentService.ts` | 文書API呼び出し |
| `src/features/documents/stores/useDocumentStore.ts` | 一覧・検索条件・ページング |
| `src/features/documents/types/document.ts` | Document / Tag 型定義 |
| `src/features/documents/routes.ts` | /documents/* ルート定義 |
| `src/features/documents/index.ts` | バレルファイル |

### feature: chat

| ファイルパス | 役割 |
|---|---|
| `src/features/chat/views/ChatView.vue` | SC-05 RAGチャット |
| `src/features/chat/components/ChatWindow.vue` | メッセージ表示 |
| `src/features/chat/components/CitationCard.vue` | 出典カード (**router.push で文書詳細へ遷移。features/documents を import しない**) |
| `src/features/chat/services/chatService.ts` | チャットAPI呼び出し |
| `src/features/chat/stores/useChatStore.ts` | 会話状態管理 |
| `src/features/chat/types/chat.ts` | ChatMessage / Citation 型定義 |
| `src/features/chat/routes.ts` | /chat ルート定義 |
| `src/features/chat/index.ts` | バレルファイル |

### 単体テスト (vitest) ※ CI 必須

| ファイルパス | 役割 |
|---|---|
| `src/features/documents/composables/useDocumentUpload.spec.ts` | 2段階コミット (presigned 取得 → PUT → complete)・失敗時の状態遷移 |
| `src/features/documents/stores/useDocumentStore.spec.ts` | 検索条件・ページング |
| `src/shared/api/client.spec.ts` | camel↔snake 変換・401 処理 |

> vitest のテストが 0 件だと frontend-ci の `test:unit` が失敗するため、最低この 3 本を feature 実装と同時に作成する。

### E2Eテスト

| ファイルパス | 役割 |
|---|---|
| `e2e/playwright.config.ts` | Playwright設定 |
| `e2e/fixtures/auth.ts` | ロール別認証フィクスチャ |
| `e2e/specs/documents.spec.ts` | 文書CRUD・editor/viewer 権限テスト |
| `e2e/specs/chat.spec.ts` | チャット動作テスト (出典→詳細遷移含む) |

---

## フロントエンド — 変更ファイル

| ファイルパス | 変更内容 |
|---|---|
| `package.json` | `name` を `pjxxx-knowledge-portal` に変更 |
| `.gitignore` | `.env` / `.env.*` (`.env.example` 除く) を追加 |

## 設計書への反映 (実装前に実施)

| 文書 | 修正内容 |
|---|---|
| 03 詳細設計書 | API 例のフィールドを snake_case に統一 (`docId` → `doc_id` 等) |
| 06 フロントエンド構成図 | useAuthStore を `shared/stores/` 配置に変更 (本計画の判断を正とする) |

## 変更しないファイル

| ファイルパス | 理由 |
|---|---|
| `frontend/.oxlintrc.json` / `.prettierrc.json` / `eslint.config.ts` | 既存設定をそのまま使用 |

---

## 実装順序

1. 設計書反映 (03 / 06) → template.yaml + samconfig.toml → `sam validate` / cfn-lint
2. Layer (`shared/`、特に kb_filter + 単体テスト) → Lambda 3本 (documents → kb_sync → chat) → pytest
3. KB 構築 (08 手順、dev) → `KnowledgeBaseId` / `DataSourceId` を samconfig に反映 → sam deploy (dev) → 手動疎通 (curl)
4. フロントエンド: 設定 → plugins / shared → features (auth → documents → chat) → router → 単体テスト → E2E
5. CI 全通し (lint / test:unit / pytest / E2E) → dev デプロイ → 動作確認チェックリスト

## Phase 1 完了条件

- editor で文書登録 → 15 分以内に RAG チャットの回答根拠に反映される
- visibility=public 固定フィルタが Retrieve リクエストに常に付与されている (単体テスト + 実機ログで確認)
- CI 全ジョブ緑・dev 自動デプロイ成功
- アイドル時コストが想定内 (OpenSearch Serverless のコレクションが存在しないことを確認)
