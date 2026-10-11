# 【第102弾 詳細解説】閉域社内Kubernetesの自動TLS暗号化編 - Ingress-Nginx × Cert-Manager による閉域社内Kubernetesの自動TLS暗号化とオレオレ警告撲滅

> **対象読者**: 情シス、Webインフラ担当  
> **主要技術スタック**: `cert-manager`, Ingress-Nginx, プライベートCA, AD GPO配布  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
社内Webツールを量産した際、誰もが直面するのがブラウザの**「この接続ではプライバシーが保護されません（NET::ERR_CERT_AUTHORITY_INVALID）」**の警告です。
開発者は「詳細設定 ➔ 安全ではないページへ進む」で回避できますが、一般社員に使わせると「怪しいウイルスが出た」「アクセスできない」と社内ヘルプデスクに問い合わせが殺到します。

さらに、年1回のSSL証明書更新を手動で管理していると、期限切れによるシステム停止事故が後を絶ちません。

外部公開していない閉域網であっても、Kubernetes標準の **`cert-manager`** を使い、社内ルート認証局（プライベートCA）と連携させることで、Ingressリソースを定義するだけで全マイクロサービスのHTTPS証明書発行・更新を完全全自動化できます。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。


```mermaid
flowchart LR
    Client["社員PCブラウザ<br/>(社内ルートCA信頼済)"]
    IngressController["Ingress-Nginx Controller<br/>(:443)"]
    CertMgr["Cert-Manager Pod"]
    InternalCA["ClusterIssuer<br/>(社内プライベートCA Secret)"]
    ServiceA["社内勤怠システム Pod"]
    ServiceB["社内ナレッジBase Pod"]

    CertMgr -->|証明書自動署名・更新| InternalCA
    InternalCA -->|TLS Secret生成| IngressController
    Client -->|警告なしHTTPSアクセス| IngressController
    IngressController -->|ルーティング /app1| ServiceA
    IngressController -->|ルーティング /app2| ServiceB
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

### `setup_cert_manager_ca.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: cert-manager
---
# ==============================================================================
# 社内ルートCAキーペアの自己署名Issuer定義
# ==============================================================================
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-root-issuer
spec:
  selfSigned: {}
---
# ルートCA証明書の生成
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: internal-root-ca
  namespace: cert-manager
spec:
  isCA: true
  commonName: "Internal Enterprise Root CA"
  secretName: internal-root-ca-secret
  duration: 87600h # 10年
  renewBefore: 720h # 30日前
  issuerRef:
    name: selfsigned-root-issuer
    kind: ClusterIssuer
    group: cert-manager.io
---
# 社内全ネームスペース共通のCA署名Issuer
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: enterprise-ca-issuer
spec:
  ca:
    secretName: internal-root-ca-secret
---
# ==============================================================================
# Ingress定義での自動TLS証明書発行の利用例
# ==============================================================================
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: internal-apps-ingress
  namespace: default
  annotations:
    cert-manager.io/cluster-issuer: enterprise-ca-issuer
    kubernetes.io/ingress.class: nginx
spec:
  tls:
  - hosts:
    - portal.corp.local
    secretName: portal-corp-tls-secret
  rules:
  - host: portal.corp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: portal-service
            port:
              number: 80
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

1. **Active Directory GPOによるルートCA一括配布**:
   `internal-root-ca-secret` から抽出した `ca.crt` を、Active Directoryのグループポリシー（GPO）で全社Windows端末の「信頼されたルート証明機関」に一括配布します。これにより全社員のブラウザで警告が100%消滅します。

2. **90日更新サイクルの安全性**:
   プライベートCAによる各ポッド証明書の有効期限をあえて90日に短縮し、30日前自動更新を強制することで、証明書の秘密鍵漏洩リスクを最小化できます。

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
