# Git & GitHub ベストプラクティス規約

## ブランチ戦略

### `main` ブランチ

- **直接プッシュ・コミット禁止**
- すべての変更は Pull Request 経由でのみマージする
- マージ前に最低1名のレビュー承認を必須とする

### ブランチ命名規則

| 種別                 | プレフィックス | 例                         |
| -------------------- | -------------- | -------------------------- |
| 新機能追加           | `feature/`     | `feature/add-book-search`  |
| バグ修正             | `fix/`         | `fix/login-error`          |
| 緊急ホットフィックス | `hotfix/`      | `hotfix/critical-auth-bug` |
| 開発統合ブランチ     | `develop`      | `develop`                  |
| リリース準備         | `release/`     | `release/v1.2.0`           |
| ドキュメント更新     | `docs/`        | `docs/update-readme`       |
| リファクタリング     | `refactor/`    | `refactor/clean-up-models` |

### ブランチフロー

```
main
 └── develop
       ├── feature/xxx   → develop へ PR
       ├── fix/xxx       → develop へ PR
       └── release/x.x.x → main + develop へ PR

hotfix/xxx → main + develop へ直接 PR（緊急時のみ）
```

## コミットメッセージ規約（Conventional Commits）

```
<type>(<scope>): <summary>

[body: 変更の詳細・背景（任意）]

[footer: Breaking Changes / Issue 参照（任意）]
```

### type 一覧

| type       | 用途                                 |
| ---------- | ------------------------------------ |
| `feat`     | 新機能追加                           |
| `fix`      | バグ修正                             |
| `docs`     | ドキュメントのみの変更               |
| `style`    | フォーマット修正（ロジック変更なし） |
| `refactor` | リファクタリング                     |
| `test`     | テストの追加・修正                   |
| `chore`    | ビルドや補助ツールの変更             |
| `ci`       | CI/CD 設定の変更                     |

### 例

```
feat(book-app): add keyword search to book list
fix(auth): handle empty password input gracefully
docs(readme): update installation steps for Windows
```

## Pull Request 規約

- タイトルはコミットメッセージと同形式 `type(scope): summary`
- 概要欄に **変更内容・理由・動作確認方法** を記載する
- 関連する Issue を `Closes #番号` で紐付ける
- WIP（作業中）の場合は Draft PR として作成する
- セルフレビューを行ってから reviewer を指定する

## Issue 規約

- バグ報告: `bug` ラベルを付与し、再現手順を明記する
- 機能要望: `enhancement` ラベルを付与する
- タスクは小さく分割し、1 Issue = 1 目的 を守る

## 一般ルール

- `main` / `develop` への force push は禁止
- マージ後は作業ブランチを削除する
- secrets・認証情報は絶対にコミットしない（`.gitignore` / GitHub Secrets を利用）
- 大きなバイナリファイルは Git LFS を使用する
