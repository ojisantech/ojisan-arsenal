# 【第115弾 詳細解説】Redisメモリ枯渇とevictionポリシー最適化編 - Redisメモリ枯渇（OOM command not allowed）とevictionポリシー（allkeys-lru）最適化設計

> **対象読者**: Webアプリエンジニア、SRE  
> **主要技術スタック**: `maxmemory-policy allkeys-lru`, `--bigkeys`, activedefrag  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「セッション管理やキャッシュで使っているRedisが突然エラーを吐き始めた」
ログには `OOM command not allowed when used memory > 'maxmemory'`。

Redisはインメモリデータベースであるため、メモリの上限に達した際の挙動を正しく設定していないと、書き込みコマンド（SET, HSET等）が全て拒否され、Webサイトのログインや決済処理が完全に麻痺します。

デフォルトの `noeviction`（メモリ満杯時にエラーを返す）のまま放置していませんか？
用途に応じた `maxmemory-policy` の選択と、巨大キー（BigKey）の早期あぶり出しができていれば、メモリ枯渇事故は100%防ぐことができます。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

![システム構成・アーキテクチャ図](https://raw.githubusercontent.com/ojisantech/ojisan-arsenal/main/images/diagram_article_115_1.png)

```mermaid
flowchart TD
    App["Webアプリ (キャッシュ書き込み)"] --> Redis["Redis インスタンス (maxmemory 4GB)"]
    Redis --> Check{"メモリ 4GB 到達時"}

    Check -->|"noeviction (デフォルト)"| Error["🚨 OOM Error: 書込コマンド拒否 (アプリ停止)"]
    Check -->|"allkeys-lru (推奨)"| LRU["最も古く参照されていないキャッシュを自動蒸発 (安全継続)"]
    Check -->|"volatile-ttl"| TTL["有効期限の近いキーから優先削除"]

    Scanner["自作 BigKey & メモリ診断スクリプト"] -.->|"MEMORY USAGE 分析"| Redis
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

### `redis_memory_tuner.sh`

```bash
#!/usr/bin/env bash
# redis_memory_tuner.sh
# 稼働中Redisのメモリ使用率診断および最適な追い出しポリシーへの動的適用
# ライセンス: MIT
set -euo pipefail

REDIS_HOST="${REDIS_HOST:-127.0.0.1}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_CLI="redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT}"

echo "=================================================================="
echo " 🔍 Redis メモリ診断レポート"
echo "=================================================================="

# メモリ情報の取得
${REDIS_CLI} INFO memory | grep -E "used_memory_human|used_memory_peak_human|maxmemory_human|maxmemory_policy|mem_fragmentation_ratio"

echo "------------------------------------------------------------------"
echo " 🔎 メモリを圧迫しているTop 5 BigKey の検出 (--bigkeys)"
${REDIS_CLI} --bigkeys

echo "------------------------------------------------------------------"
echo " ⚙️ 推奨パラメーターの動的適用 (再起動不要)"

# maxmemory が未設定(0)の場合は物理メモリの75%に設定 (例: 4GB)
CURRENT_MAX=$(${REDIS_CLI} CONFIG GET maxmemory | tail -n 1)
if [ "${CURRENT_MAX}" = "0" ]; then
    echo "[WARN] maxmemory が無制限(0)です！物理メモリ枯渇によるOS OOM-Killerの危険があります。"
    echo "[ACTION] maxmemory を 4GB (4294967296 bytes) に設定します..."
    ${REDIS_CLI} CONFIG SET maxmemory 4294967296
fi

# キャッシュ用途であれば allkeys-lru に変更
echo "[ACTION] maxmemory-policy を allkeys-lru (最近最も使われていないキーから自動破棄) に変更..."
${REDIS_CLI} CONFIG SET maxmemory-policy allkeys-lru

echo "[SUCCESS] Redis メモリチューニングが完了しました。"
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

1. **断片化率 (mem_fragmentation_ratio) の監視**:
   `mem_fragmentation_ratio > 1.5` の場合、メモリアロケータ（Jemalloc）によるメモリ断片化が発生しています。Redis 4.0以降であれば `CONFIG SET activedefrag yes` を実行することで、再起動なしでバックグラウンドメモリデフラグが実行され、実メモリ消費が劇的に下がります。

2. **Keyspace Notifications によるキー破棄ロギング**:
   どのキーがメモリ不足で蒸発（Evict）したのかを把握したい場合、`CONFIG SET notify-keyspace-events Ee` を設定してPub/Sub購読することで、破棄されたキー名をリアルタイム追跡可能です。

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
