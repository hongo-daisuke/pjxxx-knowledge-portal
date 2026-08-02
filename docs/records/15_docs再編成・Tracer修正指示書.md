# docs 再編成 + Tracer 記述修正 指示書 (Claude Code 向け)

| 項目 | 内容 |
|---|---|
| 文書番号 | KNW-DOC-15 |
| 作成者 | Fable |
| 対象 | `docs/` 配下全ファイル + 設計書の Tracer 記述 |
| 完了報告 | `docs/records/16_docs再編成・Tracer修正記録.md` (KNW-DOC-16) を KNW-DOC-14 と同形式で作成 |

> 本指示は **1 コミット** で完結させること。作業順序は「タスク 1 → 2 → 3 → 4」の順を厳守
> (NFC リネームを移動より先に行うのは、git mv を正規化済みファイル名で行うため)。

---

## タスク 1: ファイル名の Unicode NFC 統一

macOS 経由で NFD (濁点分解) になったファイル名が 6 件ある (md/06, md/07, md/11レビュー, Fable/10, html/06, html/07)。Linux CI・スクリプト・文書間リンクで「ファイルが見つからない」事故の原因になるため、docs 配下全ファイル名を NFC に統一する。

```bash
cd docs && python3 -c "
import os, unicodedata
for root, dirs, files in os.walk('.', topdown=False):
    for f in files:
        n = unicodedata.normalize('NFC', f)
        if f != n: os.rename(os.path.join(root, f), os.path.join(root, n))
"
```

### 受入条件

- 以下のチェックが何も出力しないこと:

```bash
cd docs && python3 -c "
import os, unicodedata
for root, dirs, files in os.walk('.'):
    for f in files:
        if f != unicodedata.normalize('NFC', f): print(os.path.join(root, f))
"
```

---

## タスク 2: Tracer 記述の修正 (4 点)

テンプレート規約 (`.claude/rules/lambda-python-instructions.md`「Tracer 規約」: **Tracer は使用しない**) に対し、設計書 3 箇所が違反したまま残っている。KNW-DOC-14 で 03 のみ修正済みのため、残りを揃える。行番号は目安とし、**内容で特定して** 修正すること。

| # | ファイル | 修正前 (アンカー) | 修正後 |
|---|---|---|---|
| 2-1 | `02_基本設計書.md` (L71 付近、方式設計の表) | `Lambda Powertools (Logger / Tracer / Metrics / Idempotency)` | `Lambda Powertools (Logger / Metrics / Idempotency)。Tracer は不使用 (規約: lambda-python-instructions「Tracer 規約」)` |
| 2-2 | `07_バックエンド構成図.md` (L158 付近、§6 監視・ログの表) | `Powertools Tracer (X-Ray)。※ aws-xray-sdk は 2027-02 EOS 予定のため、OpenTelemetry (ADOT) 移行を Phase 3 で評価` | `Tracer 不使用 (規約)。aws-xray-sdk が 2027-02 EOL のため。Powertools の OTEL ベース Tracer 正式リリース時に再導入を検討 (Phase 3)` |
| 2-3 | `11_全体作業計画_v1.1.md` (L144 付近、Phase 3-3) | `X-Ray SDK の EOS (2027-02) に備えた OpenTelemetry (ADOT) 移行評価` | `Powertools の OTEL ベース Tracer のリリース状況確認と再導入評価 (現行は規約により Tracer 不使用)` |
| 2-4 | `03_詳細設計書.md` (L73 付近、POST /chat 処理フロー 6.) | `citations (docId, title, s3Uri, score)` | `citations (doc_id, title, s3_uri, score)` |

### 過剰変換の禁止 (重要)

2-4 は **API レスポンス (ワイヤー形式) の記述のみ** が対象。以下の `docId` 等は内部表現であり **変換しないこと**:

- DynamoDB の属性名・キー構成 (`DOC#<docId>`, `latestVersion` 等)
- API のパスパラメータ表記 (`/documents/{docId}`)
- S3 オブジェクトキー (`documents/<docId>/v<N>/...`)
- KB メタデータキー (`ownerId` — KNW-DOC-14 の突き合わせ結果を維持)

### 受入条件

- `grep -rn "Tracer" docs/` のヒットが「Tracer を使用しない方針を説明する行」のみであること (使用を前提とした記述が 0 件)

---

## タスク 3: docs ディレクトリ再編成

### 最終形

```text
docs/
├── README.md
├── design/    # 01〜08
├── plan/      # 09, 11
└── records/   # 10, 12, 13, 14, (本作業の 16)
```

### 3-1. 移動 (git mv)

| 現在地 | 移動先 |
|---|---|
| `md/01〜08_*.md` (8 本) | `design/` |
| `Fable/09_作業計画_Phase1.md` | `plan/09_作業計画_Phase1.md` |
| `Fable/11_全体作業計画_v1.1.md` | `plan/11_全体作業計画.md` (**リネームして正本化**。ヘッダの版数 1.1 はそのまま) |
| `Fable/10_作業計画レビュー指摘事項.md` | `records/` |
| `Fable/13_v2追加修正指示書.md` | `records/` |
| `md/11_全体作業計画レビュー.md` | `records/` |
| `md/12_v1_v2修正内容.md` | `records/` |
| `md/14_v2_v3修正内容.md` | `records/` |

### 3-2. 削除 (git rm)

| 対象 | 理由 |
|---|---|
| `md/09_作業計画.md` | 旧 v1.0。正本は plan/09 (v2.0)。履歴は Git が保持 |
| `Fable/11_全体作業計画.md` | 旧 v1.0。正本は plan/11 (v1.1) |
| `html/` (フォルダごと 8 本) | 生成物。既に md との乖離が発生している (html/03 に修正前の `nextToken` が残存)。必要時に md から再生成する運用とする |

移動・削除後、空になった `md/` `Fable/` `html/` ディレクトリが残らないこと。

### 3-3. records の不変ルール

records/ へ移動した文書の **本文は一切書き換えない** (文書番号・パス参照が旧構成を指していてもそのまま。当時の記録として正)。ただし各文書ヘッダ表に `| 作成者 | ... |` 行が無いものへの **追記のみ許可** (10・13 = Fable、12・14 = Claude Code)。design/ と plan/ の文書にも同様に作成者行を追記する (01〜09, 11 = Fable ※ v2/v3 で Claude Code が改訂した 03・06 は `Fable (改訂: Claude Code)`)。

---

## タスク 4: docs/README.md の新規作成

以下の内容で作成する:

```markdown
# docs 配置ルール

- design/ : 設計書 (KNW-DOC-01〜08)。常に最新のみ。旧版は Git 履歴で参照
- plan/   : 作業計画 (09, 11)。常に最新のみ。版数はヘッダ表で管理
- records/: レビュー指摘・修正指示・修正記録 (10, 12〜)。追記専用、既存本文の書き換え禁止
- 作成者はフォルダで分けず、各文書ヘッダ表の「作成者」行に記載する
- 文書番号 (KNW-DOC-NN) は全フォルダ横断で一意。欠番可、再利用禁止
- 判定基準: 今後も更新する文書 → design/plan、その時点の記録 → records
```

---

## 全体の受入条件

1. `find docs -type f | sort` が最終形 (README + design 8 + plan 2 + records 5〜6) と一致
2. タスク 1 の NFC チェックが出力なし
3. タスク 2 の Tracer grep 条件を満たす
4. records/ 配下の既存本文に差分がない (作成者行の追記を除く) — `git diff` で確認
5. 移動は履歴が追える形 (git mv) で行われている

## 完了報告 (KNW-DOC-16) に含めること

- タスクごとの実施内容と受入条件の充足結果 (**実行していない検証に ✅ を付けないこと**。未実施は「未検証」と明記)
- 最終的な `find docs -type f | sort` の出力
- 判断に迷った点・指示から逸脱した点があれば理由と併せて記載
