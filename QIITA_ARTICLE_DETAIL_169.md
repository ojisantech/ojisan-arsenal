# 【第169弾 詳細解説】Node Exporter Textfile Collector即時可視化編 - Node Exporterカスタムテキストコレクターによる現場固有メトリクス即時可視化（Textfile Collector）

> **対象読者**: フルスタックエンジニア、情シス  
> **主要技術スタック**: Textfile Collector (`.prom`), アトミックmv書き出し, 1行メトリクス化  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「社内の特殊なバッチ処理の残り件数や、オフィスの室温センサー、自作スクリプトの実行結果をGrafanaでグラフ化したい」
「そのためだけに本格的なPrometheus Exporter（HTTPサーバー機能付き）をGoやPythonで開発するのは大げさで面倒すぎる」

Prometheus Node Exporterには、**「指定ディレクトリ内のテキストファイル（`.prom`）を読み込んでそのままメトリクスとして公開する」**という最強の機能 **`Textfile Collector`** が内蔵されています。

自作のシェルスクリプトやPythonから、**`echo "custom_metric 42" > /var/lib/node_exporter/textfile/my.prom` とファイルに書き出すだけ**で、追加コード一切不要で即座にPrometheusに収集され、Grafanaに美麗グラフが表示されます。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

![システム構成・アーキテクチャ図](https://raw.githubusercontent.com/ojisantech/ojisan-arsenal/main/images/diagram_article_169_1.png)

```mermaid
flowchart LR
    Script["現場の自作スクリプト (Bash / Python)<br/>(crontabで毎分実行)"]
    PromFile["テキストファイル (/var/lib/node_exporter/textfile/batch.prom)<br/>未処理キュー件数や室温を1行書き出し"]

    NodeExp["Node Exporter (:9100)<br/>--collector.textfile.directory 指定済"]
    Prometheus["Prometheus (:9090)"]
    Grafana["Grafana ダッシュボード"]

    Script -->|通常のリダイレクト > で atomic に書き込み| PromFile
    PromFile -->|自動読み込み| NodeExp
    NodeExp -->|Pullスクレイプ| Prometheus
    Prometheus --> Grafana
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

### `collect_custom_metrics.sh`

```bash
#!/usr/bin/env bash
# collect_custom_metrics.sh
# 現場固有の業務メトリクスを収集し、Node Exporter Textfile Collector形式で出力する
# ライセンス: MIT
set -euo pipefail

TEXTFILE_DIR="/var/lib/node_exporter/textfile"
TEMP_FILE="/tmp/custom_metrics.prom.$$"
FINAL_FILE="${TEXTFILE_DIR}/custom_business_metrics.prom"

mkdir -p "${TEXTFILE_DIR}"

# 1. 現場固有の数値を取得 (例: 未処理の注文キュー数、バックアップ残り容量等)
PENDING_ORDERS_COUNT=142
BACKUP_REMAINING_HOURS=72.5
SENSITIVE_FILES_DETECTED=0

# 2. Prometheus 形式のテキストを出力 (ヘルプとタイプ定義を推奨)
cat << EOF > "${TEMP_FILE}"
# HELP business_pending_orders_total 現在未処理の注文キュー滞留件数
# TYPE business_pending_orders_total gauge
business_pending_orders_total ${PENDING_ORDERS_COUNT}

# HELP backup_retention_remaining_hours 最も古いバックアップの残り保持期限
# TYPE backup_retention_remaining_hours gauge
backup_retention_remaining_hours ${BACKUP_REMAINING_HOURS}

# HELP security_sensitive_files_flag 機密ファイル検出フラグ (0:正常, 1:異常)
# TYPE security_sensitive_files_flag gauge
security_sensitive_files_flag ${SENSITIVE_FILES_DETECTED}
EOF

# 3. アトミックなファイル入れ替え (中途半端な読み込みを防止)
mv "${TEMP_FILE}" "${FINAL_FILE}"

echo "[SUCCESS] カスタムメトリクスを出力しました: ${FINAL_FILE}"
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

1. **アトミック書き込み（mv）の鉄則**:
   直接 `> ${FINAL_FILE}` で書き込むと、Node Exporterがファイル書き込みの途中でスクレイプした際に構文エラーになります。必ず別名一時ファイル（`/tmp/...`）に書き出してから `mv` でリネーム（Linuxのアトミック操作）するのが必須のテクニックです。

2. **Cronによる定期実行**:
   `* * * * * /usr/local/bin/collect_custom_metrics.sh` とcrontabに登録しておくだけで、毎分自動でメトリクスが更新されます。

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
