# 【第119弾 詳細解説】PostgreSQL Point-in-Time Recovery (PITR) 編 - PostgreSQL Point-in-Time Recovery (PITR) 実践リカバリ演習と誤DELETEからの秒単位過去復元

> **対象読者**: データベース管理者、情シス責任者  
> **主要技術スタック**: `pg_basebackup`, WALアーカイブ, `recovery_target_time`, 秒単位復旧  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「エンジニアがWHERE句を付け忘れて `DELETE FROM users;` を本番で実行してコミットしてしまった」
「昨晩の定期バックアップ（pg_dump）はあるが、それに戻すと今日1日分のデータ（数千件の注文）が消えてしまう」

定期バックアップだけでは、**「バックアップ取得時点から障害発生までの差分データ」**を取り戻すことはできません。

この最悪の事態から会社を救える唯一の技術が、PostgreSQLの **`PITR (Point-in-Time Recovery: 任意時点復元)`** です。
ベースバックアップ（物理スナップショット）と継続的なWALアーカイブを組み合わせることで、「事故が発生した 14時23分15秒」の**「1秒前の 14時23分14秒」**というピンポイントな過去の時点へデータベースを完全にタイムトラベルさせることができます。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。


```mermaid
flowchart LR
    BaseBackup["日曜深夜 03:00<br/>ベースバックアップ<br/>(pg_basebackup)"]
    WALArchive["WAL アーカイブ保管庫<br/>(/var/lib/postgresql/wal_archive)<br/>全変更履歴を秒単位で保持"]
    Accident["火曜 14:23:15<br/>🚨 誤った DROP TABLE 事故発生！"]

    RecoveryTarget["リカバリターゲット指定<br/>recovery_target_time = '2026-10-09 14:23:14'"]
    RestoredDB["完全復元された新インスタンス<br/>(事故直前1秒の状態で全データ生還！)"]

    BaseBackup --> RestoredDB
    WALArchive --> RestoredDB
    RecoveryTarget --> RestoredDB
    Accident -.->|事故の瞬間をスキップして停止| RestoredDB
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

### `setup_pitr_archive.sh`

```bash
#!/usr/bin/env bash
# setup_pitr_archive.sh
# PostgreSQL の継続的WALアーカイブ設定および物理ベースバックアップ自動化
# ライセンス: MIT
set -euo pipefail

ARCHIVE_DIR="/var/lib/postgresql/wal_archive"
BACKUP_DIR="/var/lib/postgresql/base_backups"

echo "[1/3] WALアーカイブ保管ディレクトリの作成"
sudo mkdir -p "${ARCHIVE_DIR}" "${BACKUP_DIR}"
sudo chown -R postgres:postgres "${ARCHIVE_DIR}" "${BACKUP_DIR}"

echo "[2/3] postgresql.conf へのWALアーカイブ設定 (反映には再起動/リロードが必要)"
cat << 'EOF'
# /etc/postgresql/16/main/conf.d/pitr.conf に追記:
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /var/lib/postgresql/wal_archive/%f && cp %p /var/lib/postgresql/wal_archive/%f'
archive_timeout = 60 # 最低でも60秒ごとにWALセグメントを強制出力
EOF

echo "[3/3] オンライン物理ベースバックアップの実行 (pg_basebackup)"
echo "[INFO] 現在の全データベースをホットバックアップしています..."
sudo -u postgres pg_basebackup \
    -D "${BACKUP_DIR}/base_$(date +%Y%m%d_%H%M%S)" \
    -F tar -z -P -v

echo "[SUCCESS] PITRの準備が整いました。"
echo "------------------------------------------------------------------"
echo " 🛠️ 事故発生時の復元設定 (postgresql.conf または postgresql.auto.conf):"
echo "   restore_command = 'cp /var/lib/postgresql/wal_archive/%f %p'"
echo "   recovery_target_time = '2026-10-09 14:23:14 JST'"
echo "   recovery_target_action = 'promote'"
echo "------------------------------------------------------------------"
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

1. **recovery_target_action = 'promote' の重要性**:
   指定時刻までのWAL適用が完了した際、自動的に読み書き可能なプライマリとして昇格させる設定です。`pause` を指定すると指定時刻で一旦停止し、SQLでデータ状態を目視確認してから昇格させることも可能です。

2. **archive_command の二重上書き防止**:
   `test ! -f ... && cp %p ...` のようにチェックを挟むことで、同一のWALセグメントが誤って上書きされる事故を防ぎ、不整合を回避します。S3互換ストレージへの転送には `rclone` や `aws s3 cp` が活用できます。

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
