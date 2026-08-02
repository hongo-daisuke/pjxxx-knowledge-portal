# github-actions-guide 6 章 Rulesets 改訂指示書 (Claude Code 向け)

| 項目 | 内容 |
|---|---|
| 文書番号 | KNW-DOC-23 |
| 作成者 | Fable |
| 対象 | `docs/github-actions-guide.md` (テンプレート由来ドキュメント) の 6 章・9-3・FAQ Q3 |
| 背景 | guide 6-2 が旧 Classic branch protection の UI 手順のままで、現行 GitHub UI (Rulesets 前面) と乖離していることが実設定作業で確定した (2026-07-15) |
| 実施タイミング | **急ぎではない**。KNW-DOC-19 (Phase 0-1) の完了報告後に着手 |
| 完了報告 | `docs/records/24_ガイドRulesets改訂記録.md` (KNW-DOC-24) |

> 注意: 本改訂はプロジェクト内の `github-actions-guide.md` に対して行う。テンプレートリポジトリ
> (cicd-template-learn) を別途 git 管理している場合は、同じ変更をテンプレート側へバックポートする
> こと (状況を完了報告に記載)。ファイルの所在は `find . -name "github-actions-guide.md"` で確認。

---

## 変更 1: 6-2 を Rulesets 手順に全面改訂

現行の 6-2「設定手順 (GitHub UI のステップバイステップ)」(Settings → Branches → Add branch protection rule 起点) を、以下の Rulesets 手順に置き換える。文体・見出しレベル・図解スタイルは既存ガイドに合わせて調整してよいが、**設定値と注意書きは変えないこと**。

### 差し替え後の 6-2 内容 (ドラフト)

```markdown
### 6-2. 設定手順 (Rulesets / GitHub UI のステップバイステップ)

> GitHub は現在、ブランチ保護の後継機能として Rulesets を提供しており、新規設定は
> Rulesets を推奨する。旧 Classic branch protection の手順は付録 (6-4) を参照。

#### Step 1: 設定画面を開く

1. リポジトリの **Settings** タブをクリック
2. 左サイドバー **Code and automation → Rules → Rulesets** をクリック
   (Branches 画面の「Add branch ruleset」ボタンからでも同じ画面に到達できる)
3. **New ruleset → New branch ruleset** を選択

#### Step 2: 基本設定

| 項目 | 設定値 |
|---|---|
| Ruleset Name | `protect-main-dev` (任意の名前で可) |
| Enforcement status | **Active** に変更 (⚠ 既定は Disabled。変更し忘れるとルールが一切効かない) |
| Bypass list | Add bypass → **Repository admin** を追加 (緊急マージ経路の確保。Rulesets は管理者も既定でルール対象になるため必須) |
| Target branches | Add target → Include by pattern で `main` と `dev` を追加 (個人作業ブランチ work/** は対象にしない) |

#### Step 3: Branch rules (有効にするのは次の 4 つのみ)

- ☑ **Restrict deletions** (既定で ON)
- ☑ **Block force pushes** (既定で ON)
- ☑ **Require a pull request before merging**
  - Required approvals: ソロ開発は **0** (自分の PR を自分で承認できないため、1 以上にすると詰む)。チーム開発は人数に応じて設定
- ☑ **Require status checks to pass**
  - Add checks で `Frontend CI Required` と `Backend CI Required` を追加 (ci-required ダミー成功ジョブの表示名)
  - ⚠ 検索候補には **一度でも実行されたチェックしか表示されない**。初回は「本ルール以外を設定して保存 → 検証 PR で CI を 1 回実行 → 本項目を追加」の順で設定する

その他の項目 (Require linear history / signed commits / deployments to succeed / code scanning 等) は本テンプレートの前提では **すべて OFF** のままとする。

#### Step 4: 作成と動作確認

1. **Create** をクリック
2. 検証用 PR を作成し、(a) CI 失敗時にマージ不可 (b) docs のみの変更でもダミー成功ジョブ green でマージ可 (c) main への直接 push が拒否される、の 3 点を確認する

#### 補足: プラン制限

個人アカウントの **Free プランでは、プライベートリポジトリに対して Rulesets / ブランチ保護が強制されない** (Pro 以上が必要)。Active 化後に必ず Step 4 の動作確認で実際にブロックされることを確かめること。
```

### 併せて追加する付録

- 現行 6-2 の Classic 手順を **「6-4. (付録) Classic branch protection での設定手順」** としてほぼそのまま移動する (削除しない — Classic を使う環境向けに残す)。冒頭に「新規設定は 6-2 の Rulesets を推奨」と 1 行付す

## 変更 2: 9-3 (1)「Branch Protection 迂回 (Admin)」の追随

現行は Classic の `Settings → Branches → Edit rule` 前提。Rulesets での同等手段を **主** とし、Classic 手順を従に書き換える:

- Rulesets の場合: (a) Bypass list に Repository admin が入っていれば、管理者はマージ時にバイパス可能 / (b) 一時的に Ruleset の Enforcement status を Disabled にする → 作業後に必ず Active へ戻す (戻し忘れ注意の警告を明記)

## 変更 3: FAQ Q3「Branch Protection 設定後にどうやって緊急マージ?」の追随

変更 2 と同内容に更新 (Rulesets 主・Classic 従)。

## 変更 4: 章内の用語統一

6 章の見出し・本文で「Branch Protection Rules の設定」を「ブランチ保護 (Rulesets) の設定」等、Rulesets が主であることが分かる表現に更新する。**ワークフロー yml 内のコメント (`Branch Protection 用ダミー成功ジョブ` 等) は変更しない** — 仕組みの呼称として通用しており、yml まで変えると差分が広がるため。

---

## 受入条件

1. 6-2 が Rulesets 手順になっており、上記ドラフトの設定値・警告 (Active 化忘れ / approvals 0 / checks 初回非表示 / Free プラン制限 / bypass 必須) がすべて含まれている
2. Classic 手順が付録 (6-4) として残っている
3. 9-3 (1) と FAQ Q3 が Rulesets 主で書き直されている
4. `grep -n "Add branch protection rule" docs/github-actions-guide.md` のヒットが付録 6-4 内のみ
5. ワークフロー yml に差分がない
