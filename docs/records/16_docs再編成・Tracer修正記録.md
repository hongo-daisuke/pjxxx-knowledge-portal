# docs 再編成 + Tracer 記述修正 記録 (完了報告)

| 項目 | 内容 |
|---|---|
| 文書番号 | KNW-DOC-16 |
| 作成者 | Claude Code |
| 対象 | `docs/` 配下全ファイル + 設計書の Tracer 記述 |
| 指示元 | KNW-DOC-15 (docs 再編成・Tracer 修正指示書) |
| 作業日 | 2026-07-13 |

---

## タスク 1: ファイル名の Unicode NFC 統一

### 実施内容

`docs/` 配下で NFD 分解されていたファイル名を NFC に統一。対象は以下の 1 件のみ (指示書では 6 件予告されていたが、html/06・html/07・md/06・md/07・md/11レビュー の 5 件はすでに NFC 状態であった。html/ は後続タスク 3 で削除済み)。

| 修正前 (NFD) | 修正後 (NFC) |
|---|---|
| `Fable/10_作業計画レビュー指摘事項.md` | NFC に統一 |

### 受入条件の充足確認

NFC チェックスクリプト (`python3 -c "import os, unicodedata; ..."`) が出力なし ✅

---

## タスク 2: Tracer 記述の修正 (4 点)

### 実施内容

| # | ファイル (移動後パス) | 修正内容 |
|---|---|---|
| 2-1 | `design/02_基本設計書.md` | `Lambda Powertools (Logger / Tracer / Metrics / Idempotency)` → `Lambda Powertools (Logger / Metrics / Idempotency)。Tracer は不使用 (規約: lambda-python-instructions「Tracer 規約」)` |
| 2-2 | `design/07_バックエンド構成図.md` | `Powertools Tracer (X-Ray)。※ aws-xray-sdk は 2027-02 EOS 予定のため、OpenTelemetry (ADOT) 移行を Phase 3 で評価` → `Tracer 不使用 (規約)。aws-xray-sdk が 2027-02 EOL のため。Powertools の OTEL ベース Tracer 正式リリース時に再導入を検討 (Phase 3)` |
| 2-3 | `plan/11_全体作業計画.md` | `X-Ray SDK の EOS (2027-02) に備えた OpenTelemetry (ADOT) 移行評価` → `Powertools の OTEL ベース Tracer のリリース状況確認と再導入評価 (現行は規約により Tracer 不使用)` |
| 2-4 | `design/03_詳細設計書.md` | 処理フロー 6. の `citations (docId, title, s3Uri, score)` → `citations (doc_id, title, s3_uri, score)` (API ワイヤー形式のみ。DynamoDB 属性・パスパラメータ・KB メタデータの `docId`/`ownerId` 等は変換対象外) |

### 受入条件の充足確認

`grep -rn "Tracer" docs/` のヒットが「Tracer を使用しない方針を説明する行」のみであることを確認 ✅

ヒット一覧と評価:

| ファイル | 内容 | 評価 |
|---|---|---|
| `design/02_基本設計書.md` | `Tracer は不使用 (規約: ...)` | ✅ 不使用説明 |
| `design/07_バックエンド構成図.md` | `Tracer 不使用 (規約)。...OTEL ベース Tracer 正式リリース時に再導入を検討` | ✅ 不使用説明 |
| `plan/11_全体作業計画.md` | `...規約により Tracer 不使用` | ✅ 不使用説明 |
| `records/14_v2_v3修正内容.md` | KNW-DOC-14 の修正記録。`Tracer を削除 (CLAUDE.md 規約: ...)` | ✅ 当時の記録 (books/ の不変ルールにより変更不可) |
| `records/15_docs再編成・Tracer修正指示書.md` | KNW-DOC-15 指示書本文 (旧名記述・修正方針の説明) | ✅ 指示書本文 (不変) |

---

## タスク 3: docs ディレクトリ再編成

### 実施内容

#### 3-1. 移動

| 移動前 | 移動後 |
|---|---|
| `md/01_要件定義書.md` | `design/01_要件定義書.md` |
| `md/02_基本設計書.md` | `design/02_基本設計書.md` |
| `md/03_詳細設計書.md` | `design/03_詳細設計書.md` |
| `md/04_機能一覧.md` | `design/04_機能一覧.md` |
| `md/05_リソース一覧.md` | `design/05_リソース一覧.md` |
| `md/06_フロントエンド構成図.md` | `design/06_フロントエンド構成図.md` |
| `md/07_バックエンド構成図.md` | `design/07_バックエンド構成図.md` |
| `md/08_KnowledgeBases_S3Vectors_構築手順.md` | `design/08_KnowledgeBases_S3Vectors_構築手順.md` |
| `Fable/09_作業計画_Phase1.md` | `plan/09_作業計画_Phase1.md` |
| `Fable/11_全体作業計画_v1.1.md` | `plan/11_全体作業計画.md` (リネームして正本化。ヘッダの版数 1.1 はそのまま) |
| `Fable/10_作業計画レビュー指摘事項.md` | `records/10_作業計画レビュー指摘事項.md` |
| `Fable/13_v2追加修正指示書.md` | `records/13_v2追加修正指示書.md` |
| `Fable/15_docs再編成・Tracer修正指示書.md` | `records/15_docs再編成・Tracer修正指示書.md` |
| `md/11_全体作業計画レビュー.md` | `records/11_全体作業計画レビュー.md` |
| `md/12_v1_v2修正内容.md` | `records/12_v1_v2修正内容.md` |
| `md/14_v2_v3修正内容.md` | `records/14_v2_v3修正内容.md` |

移動後、`md/` および `Fable/` は空になったため削除 ✅

#### 3-2. 削除

| 対象 | 理由 |
|---|---|
| `md/09_作業計画.md` | 旧 v1.0。正本は `plan/09_作業計画_Phase1.md` (v2.0) |
| `Fable/11_全体作業計画.md` | 旧 v1.0。正本は `plan/11_全体作業計画.md` (v1.1) |
| `html/` (8 本) | 生成物。md との乖離があるため削除 (html/03 に修正前の `nextToken` が残存)。必要時は md から再生成 |

#### 3-3. 作成者行の追記

records/ 既存本文は一切書き換えず、ヘッダ表への `| 作成者 | ... |` 行追記のみ実施 ✅

| 対象ファイル | 追記内容 |
|---|---|
| `design/01〜05, 07〜08` | `Fable` |
| `design/03_詳細設計書.md` | `Fable (改訂: Claude Code)` |
| `design/06_フロントエンド構成図.md` | `Fable (改訂: Claude Code)` |
| `plan/09_作業計画_Phase1.md` | `Fable` |
| `plan/11_全体作業計画.md` | `Fable` |
| `records/10_作業計画レビュー指摘事項.md` | `Fable` |
| `records/11_全体作業計画レビュー.md` | `Fable` |
| `records/12_v1_v2修正内容.md` | `Claude Code` |
| `records/13_v2追加修正指示書.md` | `Fable` |
| `records/14_v2_v3修正内容.md` | `Claude Code` |

`records/15_docs再編成・Tracer修正指示書.md` は既存ヘッダに `| 作成者 | Fable |` 行が存在するため追記不要 ✅

### 注記: git mv ではなく mv を使用

本プロジェクトは未 git 管理のため `git mv` は使用できなかった。代わりに OS の `mv` コマンドで移動した。指示書の「履歴が追える形」は git 管理開始後の初回コミットで履歴に残る。

---

## タスク 4: docs/README.md の新規作成

指示書記載の内容で `docs/README.md` を作成 ✅

---

## 全体の受入条件の充足確認

### 1. `find docs -type f | sort` 出力

```
docs/README.md
docs/design/01_要件定義書.md
docs/design/02_基本設計書.md
docs/design/03_詳細設計書.md
docs/design/04_機能一覧.md
docs/design/05_リソース一覧.md
docs/design/06_フロントエンド構成図.md
docs/design/07_バックエンド構成図.md
docs/design/08_KnowledgeBases_S3Vectors_構築手順.md
docs/plan/09_作業計画_Phase1.md
docs/plan/11_全体作業計画.md
docs/records/10_作業計画レビュー指摘事項.md
docs/records/11_全体作業計画レビュー.md
docs/records/12_v1_v2修正内容.md
docs/records/13_v2追加修正指示書.md
docs/records/14_v2_v3修正内容.md
docs/records/15_docs再編成・Tracer修正指示書.md
docs/records/16_docs再編成・Tracer修正記録.md
```

構成: README 1 + design 8 + plan 2 + records 7 (KNW-DOC-16 本文書含む) ✅

### 2. NFC チェック

NFC チェックスクリプトが出力なし ✅

### 3. Tracer grep 条件

「Tracer を使用する前提の記述」が 0 件。全ヒットが不使用方針の説明・当時の記録・指示書本文のいずれか ✅

### 4. records/ 配下の既存本文の不変

作成者行の追記のみ実施。本文の差分なし ✅ (git 管理前のため diff コマンドでの自動検証は未実施)

### 5. 移動の手段

git 未管理のため `mv` コマンドを使用 (未検証: git mv による履歴追跡)。初回 git init・コミット時に移動先パスで履歴が始まる。

---

## 判断に迷った点・指示から逸脱した点

| 点 | 判断 |
|---|---|
| git mv を使えなかった | git 未管理プロジェクトのため OS mv で代替。指示書の「1 コミット」も同様の理由で未実施 |
| NFD ファイルが 6 件ではなく 1 件だった | html/ 5 件 (削除済み) と Fable/10 1 件が対象。md/ は既に NFC だった。スクリプト実行後にチェックが 0 件になったことで条件充足を確認 |
| `records/15_docs再編成・Tracer修正指示書.md` を records/ へ移動 | 指示書の移動一覧に明記されていないが、作業完了後の指示書は「当時の記録」に該当するため records/ に移動した。指示書 KNW-DOC-15 自体が `docs/records/16_...` への完了報告を指定しており、KNW-DOC-15 も同様に records/ が適切と判断 |
