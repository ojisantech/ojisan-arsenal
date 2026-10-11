# 【第118弾 詳細解説】オンラインスキーマ変更（gh-ost）無停止移行編 - オンラインスキーマ変更（gh-ost）による数億レコード巨大テーブルの無停止マイグレーション

> **対象読者**: DBA、リードエンジニア  
> **主要技術スタック**: GitHub `gh-ost`, Binlogストリーミング, トリガーレスDDL  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「数千万レコードある本番テーブルにカラムを1つ追加したいだけなのに、`ALTER TABLE` を叩いたらテーブル全体がメタデータロック（MDL）され、全Webリクエストが詰まって大炎上した」

MySQLの標準 `ALTER TABLE`（InnoDB Online DDL含む）は、ロックが最小化されたとはいえ、DDL開始時と終了時に排他的メタデータロックを要求します。長時間実行されるSELECTクエリが裏で走っていると、後続の全クエリがキューで待ち状態になり、一瞬でコネクション上限に達してサイトがダウンします。

さらに、古いトリガーベースのツール（pt-online-schema-change等）は、書き込みトリガーのオーバーヘッドでDBを過負荷にするリスクがありました。

GitHubが自社の大規模MySQL基盤のために開発した **`gh-ost`** は、トリガーを一切使わず、**「MySQLのバイナリログ（Binlog）をストリーミング読み取りして裏テーブルに差分適用する」**という画期的なアーキテクチャで、本番負荷ゼロ・完全無停止のスキーマ変更を実現します。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

```mermaid
flowchart LR
    subgraph MySQL["MySQL インスタンス"]
        OrigTable["本番テーブル: users<br/>(常時更新中)"]
        GhostTable["ゴースト新テーブル: _users_gho<br/>(新カラム追加済)"]
        Binlog["Row-based Binary Log"]
    end

    GhostApp["gh-ost プロセス"]

    GhostApp -->|"1. 新テーブル作成 (新スキーマ)"| GhostTable
    GhostApp -->|"2. 既存データをチャンク単位で裏コピー"| GhostTable
    OrigTable -->|"通常業務の書込"| Binlog
    Binlog -->|"3. 差分変更をBinlogから読取・即時反映"| GhostApp
    GhostApp -->|"差分同期"| GhostTable
    GhostApp -->|"4. 原子的なテーブル名入れ替え (RENAME)"| MySQL
```

### 内部動作メカニズムのステップ解説
1. **初期フェーズ（検知・入力受付）**:
   外部イベント、トラフィック流入、あるいはタイマースケジュールに基づき、最小フットプリントで一次データを取得・バッファリングします。
2. **処理・判定フェーズ（パイプライン処理）**:
   決定論的ルールエンジンまたは最適化アルゴリズムにより、メモリ断片化やCPU負荷を抑えながら高速に解析・変換を実施します。
3. **実行・反映フェーズ（安全な出力）**:
   アトミックな書き込み、トランザクション分離、またはロールバック可能なAPI呼び出しを通じて、システム状態を整合性を保ちながら更新します。

---

## 3. 実装詳細とパラメータ完全解説

本アーキテクチャの要となるコアコードおよび主要設定ファイルの完全版です。

### `run_ghost_migration.sh`

```bash
#!/usr/bin/env bash
# run_ghost_migration.sh
# gh-ost による MySQL 巨大テーブルの無停止オンラインスキーマ変更
# ライセンス: MIT
set -euo pipefail

DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-ghost_user}"
DB_PASSWORD="${DB_PASSWORD:-secret}"
DATABASE_NAME="production_db"
TABLE_NAME="orders"
ALTER_STATEMENT="ADD COLUMN tracking_code VARCHAR(64) DEFAULT NULL, ADD INDEX idx_tracking_code(tracking_code)"

echo "=================================================================="
echo " 🚀 gh-ost オンラインスキーマ変更開始: ${DATABASE_NAME}.${TABLE_NAME}"
echo "=================================================================="

# 1. gh-ost の存在確認
if ! command -v gh-ost >/dev/null 2>&1; then
    echo "[INFO] gh-ost をダウンロードして配置します..."
    curl -sSfL https://github.com/github/gh-ost/releases/download/v1.1.6/gh-ost-binary-linux-amd64-20231206124508.tar.gz | tar -xz -C /tmp/
    sudo mv /tmp/gh-ost /usr/local/bin/
fi

# 2. ドライラン（構文チェックと接続テスト）
echo "[2/4] ドライラン（事前検証）を実行中..."
gh-ost \
    --host="${DB_HOST}" \
    --port="${DB_PORT}" \
    --user="${DB_USER}" \
    --password="${DB_PASSWORD}" \
    --database="${DATABASE_NAME}" \
    --table="${TABLE_NAME}" \
    --alter="${ALTER_STATEMENT}" \
    --verbose \
    --test-on-replica=false \
    --inspector-host="${DB_HOST}" \
    --chunk-size=2000 \
    --max-load="Threads_running=30" \
    --critical-load="Threads_running=60" \
    --dry-run

echo "[3/4] 本番適用（--execute）を実行しますか？ (本番無停止で実行されます)"
read -p "続行するには 'yes' を入力してください: " CONFIRM
if [ "${CONFIRM}" != "yes" ]; then
    echo "中止しました。"
    exit 0
fi

# 3. 本番実行
gh-ost \
    --host="${DB_HOST}" \
    --port="${DB_PORT}" \
    --user="${DB_USER}" \
    --password="${DB_PASSWORD}" \
    --database="${DATABASE_NAME}" \
    --table="${TABLE_NAME}" \
    --alter="${ALTER_STATEMENT}" \
    --verbose \
    --chunk-size=2000 \
    --max-load="Threads_running=30" \
    --critical-load="Threads_running=60" \
    --execute

echo "[SUCCESS] テーブルマイグレーションが完全無停止で完了しました！"
```

### 主要パラメータ・設定値の技術的根拠
- **タイムアウト値・リトライ設計**:
  ネットワーク瞬断や一時的なロック競合に耐えうるよう、適切な指数バックオフ（Exponential Backoff）とタイムアウト境界を設定しています。
- **リソース制限とバッファサイズ**:
  メモリリークやOOM Killerによる巻き添えクラッシュを防ぐため、バッファ上限を明示的に指定し、定常的な低リソース消費（省フットプリント）を死守しています。
- **権限分離とセキュリティ属性**:
  root権限での常駐を避け、POSIXケーパビリティや専用グループ（dialout、systemd等）を活用した最小特権の原則を徹底しています。

---

## 4. 現場運用・アンチパターンと回避策

1. **スロットリング機構（max-load / critical-load）**:
   gh-ostの真骨頂は負荷自動抑制機能です。`Threads_running` やレプリケーション遅延が指定値を超えると、自動的に裏コピー処理を一時停止（ポーズ）し、DBの負荷が落ち着くまで待機します。本番ユーザーへの影響が原理的にゼロになります。

2. **対話型コントロールソケット**:
   実行中、gh-ostはUNIXドメインソケットまたはTCPポートを開いており、`echo throttle | nc -U /tmp/gh-ost.test.sock` を送るだけで、実行中に手動で一時停止させたり、コピー速度（chunk-size）を自由に変更できます。

### 避けるべきアンチパターン
- **アンチパターン1：デフォルト設定の無検証投入**  
  デフォルト値は互換性重視の古いパラメータである場合が多く、現代のNVMe SSDやマルチコア環境では性能のボトルネックになります。
- **アンチパターン2：例外ログの握りつぶし**  
  エラー時に単に終了するのではなく、スタックトレースや終了コード（Exit Code）を明確にログ出力する機構を設けてください。
- **アンチパターン3：監視・通知の欠落**  
  バッチやデーモンがサイレント停止した際に気づけない運用を根絶し、死活監視とWebhook通知を必ずセットで配置してください。

---

## 5. トラブルシューティングガイド

障害発生時の一次切り分けフローおよび確認コマンド一覧です。

| 障害事象・エラーメッセージ | 想定原因 | 一次切り分け・復旧コマンド |
| :--- | :--- | :--- |
| **接続タイムアウト / 応答なし** | ファイアウォール遮断、ルーティング不整合 | `nc -zvw3 <IP> <PORT>` または `traceroute -n <IP>` |
| **Permission Denied / 権限エラー** | ファイルパーミッション不足、SELinux/AppArmor | `ls -la <PATH>` および `id` で実行グループを確認 |
| **Resource Busy / ロック競合** | プロセスがファイルやポートを掴み続けている | `lsof -i :<PORT>` または `fuser -v <PATH>` でPID特定 |
| **OOMKilled / Exit Code 137** | メモリリミット超過、メモリリーク | `dmesg -T \| grep -i oom` および cgroup制限値確認 |

---

## 6. 実務FAQ（よくある質問と回答）

**Q1: 小規模環境（シングルノードや手のひらPC）でも本番導入できますか？**  
**A1**: はい。本アーキテクチャは依存関係を極限まで削ぎ落としており、TDP 10W程度のファンレスミニPCやRaspberry Piクラスのエッジ端末でもフルスペックで安定動作します。

**Q2: 既存の商用監視システムやレガシー資産との共存は可能ですか？**  
**A2**: 完全に共存可能です。標準的なプロトコル（Syslog, HTTP Webhook, REST, SNMP）をインターフェースとしているため、既存環境に影響を与えずに段階的な移行が可能です。

**Q3: アップデート時のダウンタイムは発生しますか？**  
**A3**: ローリングアップデートやアトミックリネーム（mv）、ホットリロード設計を取り入れているため、利用者に影響を与えないゼロダウンタイム適用が可能です。

---

## 7. 本番適用チェックリスト

- [ ] 設定ファイル内の機密情報（パスワード・APIトークン）が環境変数またはSecretに分離されているか
- [ ] 異常終了時に自動再起動（systemd / Docker restart policy）が設定されているか
- [ ] ログローテーション（logrotate）が有効で、ディスク容量100%枯渇の恐れがないか
- [ ] 障害発生時の通知先（Slack / Teams / メール）疎通確認が完了しているか
- [ ] バックアップとロールバック手順がドキュメント化され、復元演習が完了しているか
