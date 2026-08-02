# docs 残件修正記録 (完了報告)

| 項目 | 内容 |
|---|---|
| 文書番号 | KNW-DOC-18 |
| 作成者 | Claude Code |
| 対象 | KNW-DOC-16 検収で見つかった残件 2 件 |
| 指示元 | KNW-DOC-17 (docs 残件修正指示書) |
| 作業日 | 2026-07-14 |

---

## 残件 1: Git 内のファイル名 NFC 確認と修正

### 背景の再確認

KNW-DOC-15 Task 1 の Python NFC スクリプトは macOS (APFS) では「NFD→NFC が同一ファイルへの rename になり no-op になる」問題で実質的に機能しなかった可能性がある。`os.walk()` が返すファイル名は macOS が NFC に正規化して返すため、Python のチェックでは常に「NFC OK」と出てしまう。

### 実施内容

**git ls-files による確認**: 本プロジェクトは未 git 管理のため `git ls-files` コマンドは使用不可。指示書手順 1 は実施できず。

**代替対処 (2段階 mv)**: APFS での直接 NFD→NFC rename は no-op になるが、中間ファイル名を経由した 2段階 rename は有効であることを利用し、4 件すべてに対して実施した。

```python
import os, unicodedata

suspects = [
    "docs/design/06_フロントエンド構成図.md",
    "docs/design/07_バックエンド構成図.md",
    "docs/records/10_作業計画レビュー指摘事項.md",
    "docs/records/11_全体作業計画レビュー.md",
]

for path in suspects:
    dirn, base = os.path.split(path)
    nfc_base = unicodedata.normalize("NFC", base)
    tmp = os.path.join(dirn, "tmp_nfc_rename_work")
    dst = os.path.join(dirn, nfc_base)
    os.rename(path, tmp)   # step 1: 別名に移動 (no-op 回避)
    os.rename(tmp, dst)    # step 2: NFC 名に移動
```

実行結果: 4 件すべて `OK` (例外なし)

**Python NFC チェック (実行結果)**:

```
Python check: NFC OK
```

### 受入条件の充足確認

| 条件 | 結果 |
|---|---|
| `git ls-files -z docs | python3 ...` が `NFC OK` を出力する | **未検証** (git 未初期化のため実行不可) |
| 代替: Python の `os.walk()` + `unicodedata` チェックが出力なし | ✅ (出力なし = NFC OK) |

**注記**: macOS APFS では Python チェックは信頼性が低いため、`git init` 後に `git ls-files -z docs | python3 -c "..."` を実行して確認すること。2段階 mv により NFC 化が意図通り行われている可能性は高いが、確定的な検証は git が必要。

---

## 残件 2: records/11 の作成者行の訂正

### 実施内容

`docs/records/11_全体作業計画レビュー.md` の作成者行を訂正した。

| 変更前 | 変更後 |
|---|---|
| `\| 作成者 \| Fable \|` | `\| 作成者 \| Claude Code \|` |

**原因**: KNW-DOC-16 作業時、`docs/md/` 内のファイルを「md/ は Claude Code のフォルダ」と認識していたにも関わらず、11_全体作業計画レビュー.md の作成者を誤って Fable と記入した。docs/md/11_全体作業計画レビュー.md は Claude Code が KNW-DOC-11 (Fable 作) をレビューした文書であるため、作成者は Claude Code が正しい。

### 受入条件の充足確認

```
$ grep -n "作成者" docs/records/11_全体作業計画レビュー.md
6:| 作成者 | Claude Code |
```

✅ 受入条件充足。その他の行に差分なし (作成者行の訂正のみ)。

---

## 判断に迷った点

| 点 | 判断 |
|---|---|
| git ls-files が実行できない | 未 git 管理のため指示書の手順 1 を実行できない。2段階 mv を代替対処として実施し、結果を「未検証 (要 git init 後確認)」と明記した |
