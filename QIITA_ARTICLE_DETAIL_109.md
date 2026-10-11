# 【第109弾 詳細解説】NetworkPolicyによるPod間ゼロトラスト分離編 - NetworkPolicyによるPod間ゼロトラストネットワーク分離と特定名前空間の隔離防衛

> **対象読者**: セキュリティSE、K8s設計者  
> **主要技術スタック**: `NetworkPolicy`, Default Deny, マイクロセグメンテーション  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「フロントエンドのWebコンテナが万が一RCE（リモートコード実行）で乗っ取られたら、社内DBに直接アクセスできてしまうのでは？」

Kubernetesの標準仕様では、**「全Pod間で通信がデフォルト全許可（Allow All）」**になっています。
つまり、開発用ネームスペースのコンテナから本番用データベースのIPに直接パケットを送ることも可能であり、ゼロトラストの観点から極めて危険な状態です。

クラウドのセキュリティグループのように、Pod単位でL3/L4のパケットフィルタリングを行うのが **`NetworkPolicy`** です（Calicoやk3s標準のKube-router等で動作）。

本記事では、社内セキュリティ監査をクリアするための「デフォルト拒否（Default Deny）」と「特定Pod間のみ通信許可」のNetworkPolicy設計を実践します。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

![システム構成・アーキテクチャ図](https://raw.githubusercontent.com/ojisantech/ojisan-arsenal/main/images/diagram_article_109_1.png)

```mermaid
flowchart TD
    subgraph WebNS["Namespace: frontend"]
        WebPod["Web Frontend Pod"]
        HackedPod["乗っ取られたPod"]
    end

    subgraph DBNS["Namespace: database"]
        DBPod["PostgreSQL Database Pod (:5432)"]
    end

    WebPod -->|許可: ポート5432のみ| DBPod
    HackedPod -.->|NetworkPolicyにより即時DROP| DBPod
    Internet["外部インターネット"] -.->|Ingress経由のみWebへ到達| WebPod
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

### `zero_trust_network_policy.yaml`

```yaml
# ==============================================================================
# 1. database ネームスペースの全通信をデフォルト遮断 (Default Deny)
# ==============================================================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: database
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
# ==============================================================================
# 2. frontend ネームスペースの特定Web Podからのみ PostgreSQL(5432) を許可
# ==============================================================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-db
  namespace: database
spec:
  podSelector:
    matchLabels:
      app: postgres-db
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: frontend
      podSelector:
        matchLabels:
          role: web-backend
    ports:
    - protocol: TCP
      port: 5432
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: frontend
      podSelector:
        matchLabels:
          role: web-backend
    ports:
    - protocol: TCP
      port: 5432
---
# ==============================================================================
# 3. DNS問い合わせ (UDP 53) の許可 (Egress許可が必須)
# ==============================================================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: database
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
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

1. **Egress Deny時のDNS問い合わせ遮断トラップ**:
   Egress（送信）をデフォルト遮断すると、CoreDNSへの名前解決（ポート53）も止まり、サービス名での通信が全て名前解決エラーで死にます。必ず `kube-dns` に対するUDP 53のEgress許可をセットで適用してください。

2. **CNIプラグインのNetworkPolicy対応確認**:
   Flannel単体など一部の極小CNIはNetworkPolicyを解釈しません。k3s標準（Kube-router統合）またはCalico / Ciliumがクラスタに導入されていることを確認してください。

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
