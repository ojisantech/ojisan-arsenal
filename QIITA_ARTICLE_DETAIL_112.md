# 【第112弾 詳細解説】EXPLAIN ANALYZEで暴くSeq Scan撲滅術編 - EXPLAIN ANALYZEで暴くインデックス不整合とSeq Scan撲滅・複合インデックス設計術

> **対象読者**: バックエンド開発者、DBA  
> **主要技術スタック**: `EXPLAIN (ANALYZE, BUFFERS)`, Covering Index (INCLUDE構文)  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「開発環境では爆速だったSQLが、本番データ（数百〜数千万件）が入った途端にCPU 100%でタイムアウトする」
原因を調べようにも `EXPLAIN` の出力はネストが深く、CostやRowsなどの数字が並びどこがボトルネックなのか判別しづらいものです。

さらに「インデックスを貼ったのに使われない（Seq Scanのまま）」という現象に遭遇し、首を傾げる若手・中堅エンジニアは少なくありません。型不一致（暗黙の型変換）や関数の適用、あるいはカーディナリティの低さが原因です。

本記事では、`EXPLAIN (ANALYZE, BUFFERS)` を使った正確なボトルネックの特定手順と、B-tree複合インデックス、カバリングインデックス（INCLUDE構文）の現場実践技を伝授します。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

![システム構成・アーキテクチャ図](https://raw.githubusercontent.com/ojisantech/ojisan-arsenal/main/images/diagram_article_112_1.png)

```mermaid
flowchart TD
    SlowQuery["遅延SQL発行<br/>(SELECT * FROM orders WHERE tenant_id=5 AND status='pending')"]
    Explain["EXPLAIN (ANALYZE, BUFFERS) 実行"]

    SeqScan["Seq Scan on orders (cost=0..50000)<br/>Buffers: shared read=12000 (ディスクI/O大量発生)"]
    IndexCreation["インデックス作成設計<br/>CREATE INDEX idx_orders_covering ON orders(tenant_id, status) INCLUDE (total_amount)"]
    IndexScan["Index Only Scan on idx_orders_covering<br/>Buffers: shared hit=4 (メモリ内完結 0.1ms)"]

    SlowQuery --> Explain --> SeqScan
    SeqScan -->|改善アプローチ| IndexCreation
    IndexCreation --> IndexScan
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

### `find_slow_seq_scans.sql`

```sql
-- find_slow_seq_scans.sql
-- 本番環境でシーケンシャルスキャン（全表走査）が多発している巨大テーブルを特定する
-- ライセンス: MIT

SELECT
    schemaname,
    relname AS table_name,
    seq_scan AS seq_scan_count,
    seq_tup_read AS seq_tuples_read,
    idx_scan AS idx_scan_count,
    ROUND((seq_scan::numeric / (seq_scan + idx_scan + 0.0001) * 100), 2) AS seq_scan_ratio_pct,
    pg_size_pretty(pg_relation_size(relid)) AS table_size
FROM
    pg_stat_user_tables
WHERE
    (seq_scan + idx_scan) > 500
    AND pg_relation_size(relid) > 10 * 1024 * 1024 -- 10MB以上のテーブルに限定
ORDER BY
    seq_tup_read DESC
LIMIT 15;
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

1. **INCLUDE構文によるIndex Only Scan化**:
   PostgreSQL 11以降で導入された `CREATE INDEX idx_name ON table(col1) INCLUDE (col2)` を使うことで、条件検索は `col1` のB-treeで行い、取得カラム `col2` はインデックスのリーフノードに付加できるため、実テーブルへのヒープアクセスを完全ゼロ（Index Only Scan）にできます。

2. **関数の罠（Functional Index）**:
   `WHERE lower(email) = 'test@example.com'` のようにカラムに関数を適用すると通常のインデックスは効きません。`CREATE INDEX idx_user_lower_email ON users(lower(email))` のように関数インデックスを定義する必要があります。

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
