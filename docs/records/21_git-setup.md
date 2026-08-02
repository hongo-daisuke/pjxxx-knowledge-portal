# pjxxx-knowledge-portal git 化手順

| 項目 | 内容 |
|---|---|
| 対象 | KNW-DOC-21 (リポジトリ立ち上げ) の手動実行 |
| 前提 | ローカルにファイル一式あり / GitHub にリポジトリ作成済み (空) |
| 完了報告 | `docs/records/22_リポジトリ立ち上げ記録.md` |

> **重要: レビュー修正ファイルの差し替えは、この手順の「後」に行う。**
> 差し替え作業には `backend/template.yaml` を誤って上書きするリスクがあるため、
> 先に git 化して戻れる地点を作っておく。
> (KNW-DOC-21 の想定とは順序が逆だが、安全側の判断)

---

## Step 0: 事前確認

```bash
cd <プロジェクトルート>

# 1. NFC 設定 (macOS 必須)
git config --global core.precomposeunicode
# → true でなければ設定する
git config --global core.precomposeunicode true

# 2. 現状確認
pwd
ls -la
```

`ls -la` で以下を確認する。

| 確認項目 | 期待 |
|---|---|
| `.gitignore` | **存在するか**。無ければ Step 1 で作成 |
| `.github/` `.claude/` | 存在する (テンプレート由来) |
| `node_modules/` `.venv/` `.aws-sam/` | あっても良い (gitignore で除外する) |
| `docs.zip` `docs_bk.zip` | **コミットしない**。Step 1 で除外 |

---

## Step 1: .gitignore の確認・作成

既に存在する場合は中身を確認し、足りない行を追記する。無ければ以下で新規作成。

```bash
cat > .gitignore << 'EOF'
# ---- Node / フロントエンド ----
node_modules/
dist/
dist-ssr/
*.local
.eslintcache
coverage/

# ---- Playwright ----
playwright-report/
test-results/
blob-report/
playwright/.cache/

# ---- Python / バックエンド ----
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# ---- AWS SAM ----
.aws-sam/

# ---- 環境変数 (実ファイルは絶対にコミットしない) ----
.env
.env.*
!.env.example

# ---- エディタ / OS ----
.DS_Store
.idea/
.vscode/*
!.vscode/extensions.json
*.swp

# ---- Claude Code 個人設定 ----
.claude/settings.local.json

# ---- 作業用アーカイブ ----
*.zip
EOF
```

### 作業用 zip の扱い

`docs.zip` / `docs_bk.zip` はプロジェクトルートに置いたままだと紛らわしい。
`*.zip` で除外されるが、**プロジェクト外へ移動しておくのを推奨**。

```bash
mkdir -p ~/Desktop/knowledge-portal-backup
mv docs.zip docs_bk.zip ~/Desktop/knowledge-portal-backup/
```

---

## Step 2: git 初期化とステージング

```bash
git init -b main
git add -A
```

> `git init -b main` が使えない古い git の場合は `git init` の後に `git branch -M main`。

### ステージング内容の確認 (ここは飛ばさない)

```bash
# ファイル数
git ls-files | wc -l

# 一覧をざっと見る
git ls-files | head -80
```

**期待値の目安**: 200〜400 ファイル程度。
4桁が出たら `node_modules/` などが混入している → `.gitignore` を見直して
`git rm -r --cached .` → `git add -A` からやり直す。

---

## Step 3: 秘匿ファイルの混入チェック (最重要)

```bash
# 1. 環境変数・個人設定ファイル
git ls-files | grep -E "\.env$|\.env\.(dev|prd|development|production)|settings\.local|\.zip$"
# → 何も出力されなければ OK

# 2. samconfig.toml に実アカウント ID / 実 ARN が入っていないか
grep -nE "[0-9]{12}|arn:aws" backend/samconfig.toml
# → 12 桁の数字や実 ARN が出たらプレースホルダに書き換えてから続行

# 3. 念のため全体スキャン
git ls-files -z | xargs -0 grep -lE "AKIA[0-9A-Z]{16}|aws_secret_access_key" 2>/dev/null
# → 何も出力されなければ OK
```

> **1つでもヒットしたらコミットしない。** 該当ファイルを `.gitignore` に追加するか、
> 値をプレースホルダ化してから Step 2 のステージングをやり直す。

---

## Step 4: 初回コミット

```bash
git commit -m "chore: initial commit (template + docs + Phase1 v3 implementation)"
git log --oneline
```

---

## Step 5: GitHub へ push

GitHub が案内している「push an existing repository」のパターンを使う。

```bash
git remote add origin https://github.com/<OWNER>/pjxxx-knowledge-portal.git
git remote -v          # 登録内容の確認
git push -u origin main
```

`<OWNER>` は GitHub の画面に表示されている実際の値に置き換える。

### 認証について

- **HTTPS + Personal Access Token**: push 時にユーザー名とパスワードを聞かれたら、
  パスワード欄に PAT を入力する (GitHub のパスワードではない)
- **gh CLI を使う場合**: `gh auth login` で認証を済ませておけば push でつまずかない
- **SSH に切り替える場合**:
  `git remote set-url origin git@github.com:<OWNER>/pjxxx-knowledge-portal.git`

### リポジトリが private であることの確認

```bash
gh repo view <OWNER>/pjxxx-knowledge-portal --json visibility
```

`gh` が無ければ GitHub の画面で確認する。**public だったら即座に private に変更**すること。

---

## Step 6: dev ブランチの作成

```bash
git switch -c dev
git push -u origin dev
git switch main
git branch -a          # main / dev / remotes/origin/main / remotes/origin/dev
```

> Branch Protection / Environments / Secrets の設定は **KNW-DOC-19 Stage B** で行う。
> ここでは作らない。

---

## Step 7: NFC 確定検証 (KNW-DOC-18 残件 1 の消化)

```bash
git ls-files -z docs | python3 -c "
import sys, unicodedata
ns = sys.stdin.buffer.read().decode().split('\0')
bad = [n for n in ns if n and n != unicodedata.normalize('NFC', n)]
print(bad if bad else 'NFC OK')"
```

- **`NFC OK`** → KNW-DOC-18 残件 1 を確定クローズ。**この出力を記録 22 に貼る**
- **NFD が出た場合** → 下記の 2 段階 `git mv` で修正

```bash
# 例: docs/design/07_バックエンド構成図.md が NFD だった場合
git mv "docs/design/07_バックエンド構成図.md" "docs/design/_tmp_rename.md"
git mv "docs/design/_tmp_rename.md" "docs/design/07_バックエンド構成図.md"
# ↑ 2つ目のパスは NFC で入力すること (このファイルからコピペすれば NFC)
```

修正後に再チェックし、`NFC OK` になったらコミットして push。

```bash
git commit -m "fix: normalize file names to NFC"
git push
```

---

## 受入条件 (KNW-DOC-21)

| # | 条件 | 確認方法 |
|---|---|---|
| 1 | 初回コミットが存在し、GitHub に main / dev の 2 ブランチ | `git log --oneline` / GitHub 画面 |
| 2 | リポジトリが private | `gh repo view --json visibility` |
| 3 | 秘匿・個人ファイルが未混入 | Step 3 のコマンドが無出力 |
| 4 | NFC 検証が `NFC OK` | Step 7 の実出力を記録に貼る |
| 5 | `git status` がクリーン | `git status` |

---

## この後の流れ

git 化が終わってから、以下の順で進める。

### ① レビュー修正ファイルの差し替え (2 回目のコミット)

```bash
git switch -c chore/apply-review-fixes
```

差し替え作業をこのブランチで行い、`git diff` で意図しない変更が無いか確認してから
main にマージする。**特に `backend/template.yaml` に差分が出ていないことを確認**。

```bash
git status
git diff --stat
git diff --stat -- backend/template.yaml    # ← 何も出ないのが正しい
```

| 対象 | 操作 |
|---|---|
| `docs/` | `docs-fixed-v2.1/docs/` で丸ごと置き換え。**旧 `08_KnowledgeBases_S3Vectors_構築手順.md` を削除** |
| `.github/workflows/sync-instructions-check.yml` | `fixed/` の同名ファイルで丸ごと置き換え |
| 他のワークフロー | 差分のみ (permissions 追加 / configure-aws-credentials v4→v6 / upload-artifact v4→v6 / Playwright キャッシュ) |
| `frontend/package.json` | `lint` から `--fix` を除去し `lint:fix` に分離する部分のみ |
| `backend/template.yaml` | **触らない**。反映は KNW-DOC-25 で行う |

08 の削除は git 管理下なので以下で行う。

```bash
git rm "docs/design/08_KnowledgeBases_S3Vectors_構築手順.md"
```

### ② 記録 22 の作成

`docs/records/22_リポジトリ立ち上げ記録.md` に、実際のコマンド出力を貼って報告する。
**実行していない検証に ✅ を付けないこと。** 未実施は「未検証」と書く。

### ③ 以降

```
22 (記録) → 25 を渡す → 26 (記録) → 19 を渡す → 20 (記録) → 23 を渡す → 24 (記録)
```

---

## トラブル時

| 症状 | 対処 |
|---|---|
| `git add -A` でファイル数が異常に多い | `.gitignore` 不備。`git rm -r --cached .` → `.gitignore` 修正 → `git add -A` |
| push で `rejected` | GitHub 側で README 等を自動生成した可能性。`git pull --rebase origin main` してから push |
| push で認証エラー | HTTPS ならパスワード欄に PAT。または `gh auth login` |
| コミット後に秘匿ファイル混入に気付いた | **push 前なら** `git rm --cached <file>` → `.gitignore` 追加 → `git commit --amend`。**push 後なら**その値を無効化・ローテーションすることを優先する |
