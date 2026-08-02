# git 化コマンドシート (KNW-DOC-21 手動実行版)

| 項目 | 内容 |
|---|---|
| 前提 | ローカルにプロジェクトファイル一式 / GitHub に空リポジトリ `pjxxx-knowledge-portal` 作成済み |
| 実行場所 | すべて **プロジェクトルート** で実行 |
| 実行後 | 各ステップの出力を控え、`docs/records/22_リポジトリ立ち上げ記録.md` を作成 (Claude Code に書かせてよい) |

---

## Step 0: 事前確認

```bash
cd /path/to/プロジェクトフォルダ

# tree コマンドは隠しファイルを表示しないため、実際の有無を確認する
ls -la
# → .gitignore / .github / .claude / CLAUDE.md があるか控えておく
#   (無ければ .gitignore は Step 1 で作成。.github 等はテンプレ反映時に Claude Code が対応)

# macOS の Git が NFC で格納する設定になっているか確認
git config --global core.precomposeunicode
# → true 以外 (空含む) なら:
git config --global core.precomposeunicode true
```

## Step 1: コミットしないものの整理

```bash
# バックアップ zip はリポジトリの外へ (履歴は今後 Git が持つので不要になる)
mkdir -p ~/backup_knowledge-portal
mv docs.zip docs_bk.zip ~/backup_knowledge-portal/

# .gitignore が無い場合のみ作成 (ある場合は下記の内容が入っているか確認)
cat > .gitignore << 'EOF'
# dependencies / build
node_modules/
dist/
coverage/
.aws-sam/
__pycache__/
*.py[cod]
.venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.eslintcache
test-results/
playwright-report/

# env / secrets
.env
.env.*
!.env.example

# personal / OS
.claude/settings.local.json
.DS_Store
*.zip
EOF
```

## Step 2: 秘匿情報の最終チェック

初回コミット前が、履歴に残さず除外できる**最後のチャンス**。

```bash
# 実 AWS アカウント ID が埋まっていないか (pjxxx などのプレースホルダなら OK)
grep -rn "arn:aws:iam::[0-9]" backend/samconfig.toml backend/template.yaml || echo "アカウントID直書きなし OK"

# .env 実ファイルが紛れていないか
find . -name ".env*" -not -name ".env.example" -not -path "*/node_modules/*" || echo ".env なし OK"
```

ヒットした場合はプレースホルダ化 or .gitignore 対象にしてから次へ。

## Step 3: 初期化と初回コミット

```bash
git init -b main
git add -A
git status
# ↑ 目視確認: *.zip / .env / node_modules が staged に「含まれていない」こと
git commit -m "chore: initial commit (Phase1 v3 implementation + docs)"
```

> `init -b main` で最初から main ブランチになるため、GitHub 案内の `git branch -M main` は不要。

## Step 4: リモート接続と push

GitHub 案内の「push an existing repository from the command line」に相当する部分。

```bash
git remote add origin https://github.com/<ユーザー名>/pjxxx-knowledge-portal.git
git push -u origin main
```

> 認証エラーが出たら: `gh auth login` を実行するか、パスワード欄に Personal Access Token を入力
> (GitHub はアカウントパスワードでの push を受け付けない)。

## Step 5: dev ブランチ作成

```bash
git switch -c dev
git push -u origin dev
git switch main
```

## Step 6: NFC 確定検証 (KNW-DOC-18 の「未検証」をここでクローズ)

```bash
git ls-files -z docs | python3 -c "
import sys, unicodedata
ns = sys.stdin.buffer.read().decode().split('\0')
bad = [n for n in ns if n and n != unicodedata.normalize('NFC', n)]
print(bad if bad else 'NFC OK')"
```

- `NFC OK` → 残件クローズ。出力を控えて記録 22 に貼る
- ファイル名が出た場合 → 各ファイルを 2 段階リネームで修正 (直接 rename は macOS で無効化されるため):

```bash
git mv "<出力されたファイル名>" tmp_rename_work
git mv tmp_rename_work "<正しい名前>"   # 出力された名前をそのままコピペで可 (Git が NFC で格納する)
git commit -m "fix: normalize filenames to NFC"
```

## Step 7: 受入チェック (KNW-DOC-21 の受入条件)

```bash
git ls-files | grep -E "\.env$|settings\.local|\.zip$" && echo "NG: 除外漏れあり" || echo "秘匿・不要ファイル混入なし OK"
git log --oneline
git status   # → clean であること
```

GitHub の Web 画面で main / dev の 2 ブランチとファイル一式が見えていれば完了。

---

## 完了後の次アクション

1. この実行結果 (各 Step の出力) を `docs/records/22_リポジトリ立ち上げ記録.md` にまとめる
2. Claude Code に **docs v2.1 差し替え + テンプレ修正 (fixed/) の反映** を次のコミットとして実施させる
   - ⚠ fixed/ はテンプレートリポジトリ構造のため**丸ごと上書き禁止**。特に `AWS/template/template.yaml` は
     ポータルの `backend/template.yaml` とは別物で、修正内容 (DefaultAuthorizer 等) を個別に反映する
3. 以降は 25 (記録 26) → 19 (記録 20) → 23 (記録 24) の順
