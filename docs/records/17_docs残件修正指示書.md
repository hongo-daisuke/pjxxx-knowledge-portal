# docs 残件修正指示書 (Claude Code 向け)

| 項目 | 内容 |
|---|---|
| 文書番号 | KNW-DOC-17 |
| 作成者 | Fable |
| 対象 | KNW-DOC-16 検収で見つかった残件 2 件 |
| 完了報告 | `docs/records/18_docs残件修正記録.md` (KNW-DOC-18)。実行していない検証に ✅ を付けないこと |

> 本指示書自体も `docs/records/` にコミットすること。全体を 1 コミットで完結させる。

---

## 残件 1: Git 内のファイル名 NFC 確認と修正

### 背景

検収時の zip に NFD (濁点分解) のファイル名が 4 件残っていた (design/06, design/07, records/10, records/11レビュー)。KNW-DOC-16 では「NFC チェック出力なし」と報告されており食い違っている。原因は macOS (APFS) がファイル名の正規化を区別しないため、**NFD→NFC の rename が「同一ファイルへの rename」として何もせず成功を返す** ことにあると推定される。実害が出るのは Linux (CI) 側のため、**Git が格納している名前** を正とする。

### 手順

1. リポジトリルートで以下を実行し、Git 内の NFD ファイル名を検出する:

```bash
git ls-files -z docs | python3 -c "
import sys, unicodedata
ns = sys.stdin.buffer.read().decode().split('\0')
bad = [n for n in ns if n and n != unicodedata.normalize('NFC', n)]
print(bad if bad else 'NFC OK')"
```

2. `NFC OK` の場合 → 残件 1 は **対応不要**。完了報告に「Git 内は NFC 済み (zip の NFD は Mac ファイルシステム表示によるもの)」と実行結果を貼って記録する
3. ファイル名リストが出た場合 → 各ファイルを **一時名経由の 2 段階 git mv** で修正する (APFS では直接 rename が無効化されるため):

```bash
git mv "<NFDのファイル名>" tmp_rename_work
git mv tmp_rename_work "<NFC正規化した正しい名前>"
```

4. 修正後、手順 1 のチェックを再実行し `NFC OK` になることを確認する

### 受入条件

- 手順 1 のコマンド出力が `NFC OK` であること (**実際の実行結果を完了報告に貼る**)

---

## 残件 2: records/11 の作成者行の訂正

### 背景

`docs/records/11_全体作業計画レビュー.md` の作成者行が `| 作成者 | Fable |` になっているが、この文書は **Claude Code が Fable 作成の全体作業計画 (KNW-DOC-11) をレビューしたもの** であり、作成者は Claude Code が正しい。

### 手順

- 該当行を `| 作成者 | Claude Code |` に訂正する。**修正はこの 1 行のみ** (records の本文書き換え禁止ルールに対し、作成者行は追記枠のためその訂正は許容)

### 受入条件

- `grep -n "作成者" docs/records/11_全体作業計画レビュー.md` の出力が `| 作成者 | Claude Code |` であること
- 同ファイルのその他の行に差分がないこと (`git diff` で確認)
