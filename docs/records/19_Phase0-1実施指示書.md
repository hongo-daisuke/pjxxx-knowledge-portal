# Phase 0-1 実施指示書: CI/CD テンプレート実環境検証 (Claude Code + 手動作業)

| 項目 | 内容 |
|---|---|
| 文書番号 | KNW-DOC-19 |
| 作成者 | Fable |
| 対象 | plan/11 の Phase 0-1 (+ KNW-DOC-14 で「未検証」のまま残っている 2 件の消化) |
| 完了報告 | `docs/records/20_Phase0-1検証記録.md` (KNW-DOC-20)。**実行していない検証に ✅ を付けない。全ステージで実際のコマンド出力・件数を貼ること** |

> 前提: KNW-DOC-17 (残件修正) が完了していること。
> 本検証は Stage A → E の順に実施する。Stage D のみ AWS 側の前提 (OIDC ロール等) が必要で、
> 未整備の場合は **Stage D を「ブロック中」として報告し、A〜C・E だけで一旦完了報告を出してよい**。
> 「⌨️ 手動」の印がある手順は GitHub / AWS の画面操作が必要なため、Claude Code は手順を提示して人間に依頼すること。

---

## Stage A: ローカル検証 (AWS 不要)

KNW-DOC-14 の未検証 2 件はここで消化する。

### A-1. フロントエンド

```bash
cd frontend
rm -rf node_modules
npm ci                 # lockfile が無い/不整合ならここで失敗する → npm install で更新しコミット
npm run lint           # oxlint + eslint (jiti が無いと eslint が起動エラーになる)
npm run type-check     # スクリプトが存在する場合
npm run test:unit      # vitest 3 本 (useDocumentUpload / useDocumentStore / client)
npm run build:dev
```

**記録すること**: 各コマンドの成否、test:unit の「passed 件数 / skip 件数 (0 であること)」、失敗した場合はエラー全文と修正内容。

### A-2. バックエンド

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -r layer/library/requirements.txt
pytest -v              # skip 0 件・全 green (kb_filter の完全版テスト含む)
ruff check .           # 設定がある場合
mypy .                 # 設定がある場合
sam validate --lint    # template.yaml (cfn-lint 相当)
deactivate
```

**記録すること**: pytest の「passed / skipped (0 であること)」、sam validate の結果。

### Stage A 完了条件

- `npm ci` → `test:unit` がクリーン環境から一発 green (lockfile 更新があればコミット)
- `pytest` が skip 0 件で全 green
- → **KNW-DOC-14 の未検証 2 件をここで「検証済み」に昇格** (14 は書き換えず、本検証の記録 KNW-DOC-20 に結果を書く)

---

## Stage B: GitHub 設定の確認・整備 (⌨️ 手動中心)

Claude Code は現状を `gh` CLI で確認できる範囲で確認し、不足分の設定手順を人間に提示する。

| # | 項目 | 確認/設定内容 |
|---|---|---|
| B-1 | Branch Protection / Ruleset | main・dev への直接 push 禁止、PR 必須。**Required checks に paths-filter 用のダミー成功ジョブ名 (ci-required 等、ワークフロー実装の job 名) を指定** (個別ジョブ名を指定すると docs のみの変更で永久 pending になるため) |
| B-2 | Environments | `dev` / `prd` を作成。**prd に Required reviewers を設定** (自分を指定) |
| B-3 | Secrets / Variables | デプロイワークフローが参照する Secrets (フロント `.env` 生成用の値、AWS ロール ARN 等) を各 Environment に登録。ワークフロー yml の `secrets.` / `vars.` 参照箇所を grep して一覧化してから登録する |
| B-4 | 不要ワークフローの整理 | bastion / direct の 2 パターンのうち **本プロジェクトで使う方だけを残す** (どちらを使うかは人間が決定)。残した方のトリガーブランチ設定を確認 (`work/**` はコメントアウトのままが既定) |

**記録すること**: 設定した項目の一覧、B-3 で grep した Secrets 参照の一覧と登録状況。

---

## Stage C: CI 検証 (PR を実際に回す)

```bash
git switch -c work/ci-verification
# 変更内容: frontend と backend の両方に無害な変更を 1 つずつ入れる
# (例: それぞれの README または コメント 1 行。paths-filter が両方の CI を起動することを確認するため)
git push -u origin work/ci-verification
gh pr create --base dev --fill
```

| # | 確認項目 |
|---|---|
| C-1 | frontend-ci / backend-ci / pr-validation / sync-instructions-check が全て起動し green になる |
| C-2 | PR テンプレートが表示され、pr-validation のチェックボックス検証が機能する (チェック無しで fail → チェックして pass) |
| C-3 | **docs のみを変更した 2 本目の PR** を作成し、重い CI ジョブがスキップされつつ Required check (ダミー成功ジョブ) は green になり、マージ可能になることを確認 |
| C-4 | 規約同期の検証: `.claude/rules/` のファイルを 1 行変更して push → sync-instructions-check が **fail することを確認** → `./scripts/sync-ai-instructions.sh` を実行して同期 → green になることを確認 → 検証用変更を revert |

**記録すること**: 各 PR の URL (または番号)、各ワークフローの結果、C-4 の fail → green の遷移。

---

## Stage D: デプロイ検証 (AWS 前提が必要)

**前提** (未整備なら本 Stage はブロック中と報告): OIDC プロバイダ、環境別デプロイロール、SAM アーティファクトバケット (テンプレート付属の `docs/aws-iam-role-setup.md` / `docs/github-environments-setup.md` 参照)。

| # | 確認項目 |
|---|---|
| D-1 | Stage C の PR を dev にマージ → backend-deploy / frontend-deploy が起動し、dev 環境へデプロイ成功。SAM の `KnowledgeBaseId` / `DataSourceId` は KB 構築前 (Phase 0-5 前) のため **プレースホルダ値でよい** (IAM ポリシーの ARN は存在検証されない)。chat 機能の動作確認は Phase 0-5 完了後に行う |
| D-2 | フロントの S3 配信確認: FrontendApi の URL にアクセスし SPA が表示される。`bk/` に世代バックアップが作成されている |
| D-3 | **prd 承認ゲート**: main へのマージ (または workflow_dispatch) で prd デプロイを起動し、**Environments の承認待ちで停止することを確認 → 実際に 1 回承認 → デプロイ完了まで確認** (⌨️ 承認操作は手動) |
| D-4 | コミットメッセージに `[skip-deploy]` を含めた push でデプロイがスキップされることを確認 |

**記録すること**: 各 Run の URL、dev のスタック名、D-3 の承認スクリーンショットまたは Run ログの該当箇所。

---

## Stage E: AI 規約の読み込み検証

| # | 確認項目 |
|---|---|
| E-1 | Claude Code でリポジトリを開き `/memory` を実行 → CLAUDE.md と `.claude/rules/` の各ルールが読み込まれていることを確認 (⌨️ 出力を記録) |
| E-2 | VS Code の Copilot チャットで backend の Python ファイルに関する質問をし、**応答の References に `.github/instructions/*.instructions.md` が表示される** ことを確認 (⌨️ 手動)。表示されない場合はファイル名サフィックス (`.instructions.md`) と applyTo を再確認 |

---

## 全体の完了条件 (plan/11 Phase 0-1 と対応)

1. Stage A: ローカルで lint / test が全 green (14 の未検証 2 件消化)
2. Stage C: PR で CI 全ジョブ green、docs のみ PR がマージ可能
3. Stage D: dev 自動デプロイ成功 + **prd 承認ゲートを実際に 1 回通した** (ブロック中の場合はその旨と未達項目を明記)
4. Stage E: Claude Code / Copilot の規約読み込みを確認
5. KNW-DOC-20 に全ステージの実行結果 (コマンド出力・Run URL・件数) が記録されている

## 完了後の次アクション (参考)

- Stage D まで完了 → plan/11 の Phase 0-3 (ADR-001〜004 作成) → 0-5 (KB 構築、design/08 手順) へ
- Stage D がブロック → 0-4 (AWS 前提整備) を先に実施
