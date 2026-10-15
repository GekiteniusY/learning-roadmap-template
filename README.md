# learning-roadmap-template

学習テーマを「ステップの流れ図」と「ステップごとの理解チェックリスト」にまとめた、1枚の HTML を作るテンプレートです。

- ステップの流れ（SVG）と、ステップごと・全体の進み具合
- チェックボックス付きのチェックリスト（項目ごとに根拠へのリンク）
- チェック状態はブラウザの localStorage に保存（ページごとのキー）
- 出力は外部ファイル不要の HTML 1枚。Python 3.8+ だけで動きます

サンプル：[`examples/roadmap.sample.html`](examples/roadmap.sample.html)

## 使い方

```sh
cp roadmap.sample.json my-topic.json   # データを書く
python3 build.py my-topic.json -o roadmap.html
```

## データファイル（JSON）

| キー | 内容 |
|---|---|
| `title` | ページの見出し |
| `storage_key` | localStorage のキー。テーマごとに別の値にする（版を変えるときは `-v2` など） |
| `footer` | 根拠の出典など |
| `steps[]` | ステップ。並び順が Step 番号になる |
| `steps[].id` | 依存関係で使う ID |
| `steps[].title` / `sub` | 見出しと補足 |
| `steps[].short` / `node_sub` | 図の箱に出す短い名前と補足（省略時は `title` / `sub`） |
| `steps[].after` | 前提となるステップの ID。図の列はここから自動で決まる |
| `steps[].links[]` | 見出し下に並べる主な資料（`label`・`url`・`note`） |
| `steps[].items[]` | チェック項目（`text` と `refs[]`。`refs` は `label`・`url`・`title`、`url` 省略でコード表示） |
| `extra_edges[]` | 依存以外の補助の矢印（`from`・`to`・`label`・`dashed`） |

## 進め方

1. **ロードマップの下書き**：テーマを 5〜8 ステップに分け、順番と依存関係を決める（図にして相談すると早い）
2. **チェックリスト**：各ステップに具体的な自己確認項目を 6〜12 個。項目ごとに根拠（ドキュメント・コード）を付ける
3. **ビルド**：`python3 build.py ...`
4. **確認**：幅 1280px と 820px で表示し、図の崩れ・リンク・チェックの保存（再読み込みで残るか）を確かめる

## チェック項目の書き方

- 「〜を説明できる」「〜が分かる」「〜できる」で終える。「〜を読む」のような作業ではなく、到達状態を書く
- 1項目に1つのこと。「AとBの違い」のように比べる形は理解を確かめやすい
- 数字・名前・条件を入れて具体的に（例：「fast-forward と 3-way マージの違いを説明できる」）
- 根拠のない項目は作らない。出典を `refs` に付ける

## ライセンス

MIT
