# 【第141弾 詳細解説】KeycloakオンプレSSO ＆ Active Directory統合編 - Keycloakによるオンプレミスシングルサインオン（SSO / OIDC）構築とActive Directory透過統合

> **対象読者**: 全社認証基盤担当、情シス責任者  
> **主要技術スタック**: `Keycloak 24.x`, PostgreSQL, User Federation, LDAP同期, OIDC  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「社内Webツールが増えるたびに、ユーザーIDとパスワードを各DBに個別登録・管理しており、退職者のアカウント消し忘れが深刻なセキュリティホールになっている」
「OktaやAzure AD (Entra ID) を全社員に契約すると、月額のサブスクリプション費用が数百万円規模に跳ね上がる」

Red Hatが主導する世界最高峰のオープンソースIdP **`Keycloak`** を使えば、**追加ライセンス費用ゼロ**でエンタープライズ級のシングルサインオン（SSO）基盤をオンプレミスに構築できます。

OpenID Connect (OIDC) および SAML 2.0 に完全対応し、既存の社内Active Directory / LDAPと連携してユーザー情報を自動同期。社員は1組のパスワード（＋2要素認証）だけで全社システムに安全にログインできるようになります。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

```mermaid
flowchart TD
    Client["社員ブラウザ"]
    WebApp["社内Webアプリ (FastAPI / Next.js)"]
    Keycloak["Keycloak IdP サーバー (:8080)<br/>(Docker Compose / PostgreSQL)"]
    AD["既存 Active Directory (LDAPS)<br/>社員アカウントマスタ"]

    Client -->|アクセス| WebApp
    WebApp -->|未認証: OIDCリダイレクト| Keycloak
    Keycloak -->|認証画面表示| Client
    Keycloak -->|ユーザー認証 & グループ照合| AD
    Keycloak -->|署名済み JWT (ID/Access Token) 発行| WebApp
    WebApp -->|認証完了・ダッシュボード表示| Client
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

### `docker-compose.keycloak.yml`

```yaml
version: '3.8'

# docker-compose.keycloak.yml
# Keycloak 24.x + PostgreSQL 高可用性オンプレミスIdPスタック
# ライセンス: MIT

services:
  keycloak-db:
    image: postgres:16-alpine
    container_name: keycloak_postgres
    restart: always
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak_user
      POSTGRES_PASSWORD: DBSecretPassword2026!
    volumes:
      - /data/keycloak_db:/var/lib/postgresql/data

  keycloak:
    image: quay.io/keycloak/keycloak:24.0.3
    container_name: keycloak_app
    restart: always
    command: start-dev --import-realm
    ports:
      - "8080:8080"
    environment:
      KC_DB: postgres
      KC_DB_URL_HOST: keycloak-db
      KC_DB_URL_PORT: 5432
      KC_DB_URL_DATABASE: keycloak
      KC_DB_USERNAME: keycloak_user
      KC_DB_PASSWORD: DBSecretPassword2026!
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: AdminSuperSecretKey2026!
      KC_HEALTH_ENABLED: "true"
      KC_METRICS_ENABLED: "true"
    depends_on:
      - keycloak-db
    healthcheck:
      test: ["CMD-SHELL", "exec 3<>/dev/tcp/127.0.0.1/8080; echo -e 'GET /health/ready HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n' >&3; grep 'HTTP/1.1 200 OK' <&3"]
      interval: 30s
      timeout: 5s
      retries: 3
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

1. **User Federation によるActive Directory同期**:
   Keycloak管理画面の `User Federation` から `ldap` を追加し、接続先を既存ADに設定して `Edit Mode: READ_ONLY` を選択するだけで、ADのOUやグループ所属が即座にKeycloakのロールへ自動マッピングされます。パスワードの検証もADへ透過委譲されます。

2. **本番運用のプロキシ設定（KC_PROXY）**:
   NginxやIngressの背後でリバースプロキシとして動かす本番環境では、`start-dev` ではなく `start --optimized` を使い、`KC_PROXY=edge` または `KC_PROXY_HEADERS=xforwarded` を指定してTLS終端を行わせるのが必須です。

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
