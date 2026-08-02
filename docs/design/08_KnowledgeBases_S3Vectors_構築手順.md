# Bedrock Knowledge Bases × S3 Vectors 構築手順書

| 項目 | 内容 |
|---|---|
| 文書番号 | KNW-DOC-08 |
| 作成者 | Fable |
| 版数 | 1.0 |
| 対象 | dev / prd 各環境 (環境ごとに本手順を 1 回実施) |
| 所要時間 | 約 30〜45 分 (モデルアクセス承認待ち除く) |

---

## 0. 最重要注意 (コスト事故防止)

> **KB 作成時、ベクトルストアの「クイック作成」で OpenSearch Serverless を選択しないこと。**
> OpenSearch Serverless は OCU が常時確保され、使っていなくても月額数万円規模の課金が発生する。
> 本システムは必ず **S3 Vectors (S3 ベクトルバケット)** を選択する。
> 誤って作成した場合は KB 削除だけでなく **OpenSearch Serverless コレクションの削除まで** 確認すること (KB を消してもコレクションは残り課金され続ける)。

## 1. 事前準備

### 1.1 リージョン確認

- S3 Vectors および Bedrock Knowledge Bases の対応リージョンを確認する (S3 Vectors は 2025-12 GA。東京リージョンの対応状況は構築時に AWS ドキュメントで確認)
- 東京未対応の場合: KB 関連 (ベクトルバケット / KB / 埋め込み) のみ対応リージョン (例: us-east-1) に構築し、DataBucket はクロスリージョンのデータソースとして扱えるかを確認。不可の場合は文書レプリケーション用バケットを KB 側リージョンに用意する

### 1.2 モデルアクセス有効化

Bedrock コンソール → Model access で以下をリクエスト:

| 用途 | モデル | 備考 |
|---|---|---|
| 埋め込み | Titan Text Embeddings V2 | 次元数 1024 を使用 |
| 生成 | Claude 系 (例: Haiku クラス) | クロスリージョン推論プロファイルの ID を控える |

### 1.3 データソース用バケットの確認

- `pjxxx-{env}-001-knowledge-data` (SAM で構築済み) の `documents/` プレフィックスをデータソースにする
- テスト用に文書 2〜3 件と対応する `.metadata.json` を配置しておく (形式は 3.3 参照)

## 2. S3 Vectors ベクトルバケット・インデックス作成

コンソール (S3 → ベクトルバケット) または CLI で作成する。

```bash
# ベクトルバケット作成
aws s3vectors create-vector-bucket \
  --vector-bucket-name pjxxx-dev-001-knowledge-vectors

# インデックス作成 (Titan V2 = 1024 次元 / cosine)
aws s3vectors create-index \
  --vector-bucket-name pjxxx-dev-001-knowledge-vectors \
  --index-name knowledge-index \
  --dimension 1024 \
  --distance-metric cosine \
  --data-type float32 \
  --metadata-configuration '{"nonFilterableMetadataKeys":["AMAZON_BEDROCK_TEXT"]}'
```

補足:

- `nonFilterableMetadataKeys` にチャンク本文キーを指定するのは、フィルタ可能メタデータの容量制限を本文が圧迫しないようにするため (KB のクイック作成では自動設定される。手動作成時は KB ドキュメントで最新のキー名を確認)
- 次元数はインデックス作成後に変更できない。埋め込みモデルを変える場合はインデックス再作成 + 全再同期

## 3. Knowledge Base 作成

### 3.1 KB 本体 (コンソール)

1. Bedrock コンソール → Knowledge Bases → **Create knowledge base with vector store**
2. 名前: `pjxxx-{env}-001-knowledge-kb`
3. IAM: 「新しいサービスロールを作成」(後で最小権限に絞る場合は 5.1 のポリシー例を参照)
4. データソースタイプ: **Amazon S3**

### 3.2 データソース設定

| 項目 | 設定値 |
|---|---|
| S3 URI | `s3://pjxxx-{env}-001-knowledge-data/documents/` |
| チャンキング戦略 | 固定サイズ / **512 トークン / オーバーラップ 15%** |
| パーシング | 標準パーサ (PDF/Word/テキスト等)。図表中心の文書が増えたら FM パーシングを再評価 |

チャンク戦略の根拠: 規程・手順書など構造化文書が中心のため固定 512 を汎用スタート地点とし、議事録など散文が増えた段階で階層チャンキングを比較検証する (戦略により正答率に最大 15% 程度の差が出るという検証報告があるため、Phase 2 で自データ評価を行う)。

### 3.3 メタデータサイドカーの形式

データソース内の各文書 `<fileName>` に対し、同一プレフィックスに `<fileName>.metadata.json` を置く:

```json
{
  "metadataAttributes": {
    "docId": "d_01HXXXXXXXX",
    "title": "経理規程",
    "visibility": "department",
    "department": "keiri",
    "ownerId": "cognito-sub-uuid",
    "tags": "経理,規程"
  }
}
```

- 本システムでは `documents-func` が自動生成する (手動配置はテスト時のみ)
- 属性はフィルタ可能メタデータとして取り込まれ、Retrieve のフィルタ式で使用できる
- S3 Vectors のフィルタ可能メタデータには 1 ベクトルあたりの容量制限があるため、属性は上記 6 項目に限定する (自由記述の説明文などを入れない)

### 3.4 埋め込みモデル・ベクトルストア選択

1. 埋め込みモデル: **Titan Text Embeddings V2** (1024 次元)
2. ベクトルデータベース: **「S3 ベクトルバケット」を選択** ← 本手順書 0 章の通り最重要
   - 「新しいベクトルストアをクイック作成 (S3 Vectors)」を選ぶとバケット・インデックスが自動作成される (2 章を省略可)
   - 2 章で手動作成済みの場合は「既存のベクトルストア」でバケット・インデックスを指定
3. 作成を実行し、**Knowledge Base ID (`KB_ID`) とデータソース ID (`DS_ID`) を控える** → SAM の Parameter に設定

## 4. 同期と動作確認

### 4.1 初回同期

```bash
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id <KB_ID> \
  --data-source-id <DS_ID>

# 状態確認
aws bedrock-agent list-ingestion-jobs \
  --knowledge-base-id <KB_ID> \
  --data-source-id <DS_ID> \
  --max-results 1
```

statistics の `numberOfDocumentsScanned / Indexed / Failed` を確認。metadata.json はメタデータとして消費され、文書数にはカウントされない。

### 4.2 コンソールでの検索テスト

Bedrock コンソール → 対象 KB → Test で以下を確認:

1. フィルタ無し Retrieve: 質問に関連するチャンクが返ること
2. フィルタ付き Retrieve: `visibility = "public"` を指定し、department 文書が **返らない** こと
3. Retrieve and generate: 回答が生成されること (本番は自前 Converse を使うが、疎通確認として有効)

### 4.3 Lambda からの呼び出し例 (chat-func 抜粋)

```python
import boto3

agent_rt = boto3.client("bedrock-agent-runtime")

def build_filter(department: str, user_sub: str) -> dict:
    return {"orAll": [
        {"equals": {"key": "visibility", "value": "public"}},
        {"andAll": [
            {"equals": {"key": "visibility", "value": "department"}},
            {"equals": {"key": "department", "value": department}},
        ]},
        {"andAll": [
            {"equals": {"key": "visibility", "value": "private"}},
            {"equals": {"key": "ownerId", "value": user_sub}},
        ]},
    ]}

def retrieve(kb_id: str, question: str, department: str, user_sub: str) -> list:
    res = agent_rt.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={"text": question},
        retrievalConfiguration={"vectorSearchConfiguration": {
            "numberOfResults": 6,
            "filter": build_filter(department, user_sub),
        }},
    )
    return res["retrievalResults"]
```

## 5. IAM 設定

### 5.1 KB サービスロール (最小権限の要点)

| 対象 | アクション |
|---|---|
| DataBucket | `s3:ListBucket` (prefix 条件 `documents/*`), `s3:GetObject` (`documents/*`) |
| ベクトルバケット | `s3vectors:GetIndex`, `s3vectors:QueryVectors`, `s3vectors:PutVectors`, `s3vectors:GetVectors`, `s3vectors:DeleteVectors`, `s3vectors:ListVectors` (対象インデックス ARN) |
| 埋め込みモデル | `bedrock:InvokeModel` (Titan Embeddings V2 の ARN) |

(自動作成ロールの内容を確認し、対象 ARN が絞られていることをレビューする。アクション名は構築時に自動作成ポリシーで最新名を確認)

### 5.2 アプリ側 Lambda への追加権限

- chat-func: `bedrock:Retrieve` (KB ARN)、`bedrock:InvokeModel` (生成モデル / 推論プロファイル ARN)
- kb-sync-func: `bedrock:StartIngestionJob`, `bedrock:GetIngestionJob`, `bedrock:ListIngestionJobs` (KB / DS ARN)

SAM 側は `KnowledgeBaseId` / `DataSourceId` を Parameter で受け取り、ARN を `!Sub "arn:${AWS::Partition}:bedrock:${AWS::Region}:${AWS::AccountId}:knowledge-base/${KnowledgeBaseId}"` の形で構築する。

## 6. コスト管理

| 項目 | 内容 |
|---|---|
| 発生する課金 | S3 Vectors (ストレージ + PUT/クエリ従量)、埋め込み (同期時)、生成モデル (質問時)、通常の S3/リクエスト |
| 発生しない課金 | ベクトルストアの常時課金 (OCU 等) — S3 Vectors には存在しない |
| 目安 | 数千文書・社内数十ユーザー規模でベクトルストア分は月数十〜数百円。OpenSearch Serverless 比で 90% 以上の削減報告が一般的 |
| 監視 | コスト配分タグ `Project=knowledge` を全リソースに付与し、Cost Explorer でサービス別に月次確認。Budgets で環境ごとに閾値アラート (dev: 3,000 円 / prd: 10,000 円 目安) |
| PUT 課金の注意 | S3 Vectors の PUT は最小課金単位があるため、大量文書の初期投入はまとめて 1 回の ingestion で行う (細切れ同期の繰り返しを避ける) |

## 7. トラブルシューティング

| 症状 | 原因と対処 |
|---|---|
| 同期は成功するが検索でフィルタが効かない | metadata.json のファイル名不一致 (`<fileName>.metadata.json` 厳密一致) / JSON ルートが `metadataAttributes` でない / 同期前の質問。再同期して確認 |
| ingestion job が Failed | statistics の失敗文書を確認。非対応ファイル形式・サイズ超過・KB ロールの GetObject 権限不足が典型 |
| Retrieve が AccessDenied | chat-func ロールに `bedrock:Retrieve` (KB ARN) が無い / リージョン違い |
| 回答が遅い | S3 Vectors の検索は数百 ms〜のレイテンシ特性。生成モデルの出力トークン数を絞る、numberOfResults を減らす。恒常的に厳しければ OpenSearch Serverless へのエクスポートを検討 |
| 予期しない課金 | ほぼ確実に OpenSearch Serverless コレクションの残存。OpenSearch コンソールでコレクション一覧を確認し削除 |

## 8. 撤去手順 (dev 検証終了時)

1. KB のデータソース削除 → KB 削除
2. S3 Vectors インデックス削除 → ベクトルバケット削除
3. (誤作成していた場合) OpenSearch Serverless コレクションの有無を確認・削除
4. SAM スタック削除 (`sam delete`)。DataBucket に DeletionPolicy: Retain を設定している場合は手動削除
