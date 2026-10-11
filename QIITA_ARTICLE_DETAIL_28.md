# 【第28弾 詳細解説】Docker Composeの物理分割とオーバーライド編 - 「AI機能付き」と「AIなしBase版」をどう作り分けるか？ Docker Composeの物理分割とオーバーライド設計で保守コストを半減させた話

> **対象読者**: Docker運用者、インフラ設計者  
> **主要技術スタック**: `docker-compose.base.yaml`, `docker-compose.llm.yaml`, `-f`  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
ソフトウェアを開発していると、必ず「エディション違い」を提供したくなる場面があります。

* **「軽量Base版」**: CPUのみ・メモリ2GBで動く、AI機能なしの高速資産スキャンツール
* **「LLM拡張版」**: ローカルAIモデル（Ollama）やRAGエンジンを同梱したフル機能版

これを実現しようとして、初心者がやってしまいがちな最大の失敗が **「Gitブランチを分けること（`branch: base` と `branch: llm-pro`）」** です。

ブランチを分けると、コア機能（バグ修正や画面改善）を修正するたびに双方向へのマージ作業（コンフリクト解消）が発生し、わずか数ヶ月で保守が破綻します。

絶対にブランチを分けてはいけません。  
**「コードベースは完全に単一（`main` ブランチのみ）」** を維持し、**Docker Composeの「物理分割」と「オーバーライド（`-f` オプション）」** を使ってデプロイ時に構成を切り替えるのがプロのインフラ設計です。

本記事では、2GB RAMで自立稼働する「Base版」と、AIアドオンを重ねる「LLM版」をスマートに両立させるDocker Compose設計を公開します。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

```mermaid
flowchart TD
    subgraph BaseEdition ["📦 1. docker-compose.base.yaml (基盤・軽量エディション)"]
        WebBase["asset-web (FastAPI / UI)"]
        ScannerBase["asset-scanner (エージェントレス探索)"]
        DBBase["mariadb / snipeit (資産台帳)"]
    end

    subgraph LLMAddon ["🧠 2. docker-compose.llm.yaml (AIアドオン・拡張エディション)"]
        OllamaNode["ollama (ローカル推論コンテナ)"]
        VectorDB["chromadb (ベクトルRAG)"]
        EnvInject["環境変数注入:<br/>LLM_ENABLED=true"]
    end

    BaseEdition --> ProductionBase["🚀 Base版 起動<br/>docker compose -f docker-compose.base.yaml up -d<br/>(必要メモリ: 2GB RAM / CPUのみ)"]
    
    BaseEdition === LLMAddon
    LLMAddon --> ProductionLLM["🚀 LLM拡張版 起動<br/>docker compose -f docker-compose.base.yaml -f docker-compose.llm.yaml up -d<br/>(必要メモリ: 8GB RAM)"]
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

### `1.`

```yaml
# docker-compose.base.yaml (軽量Base版)
version: '3.8'

services:
  db:
    image: mariadb:10.6
    container_name: asset-db
    environment:
      - MYSQL_DATABASE=snipeit
      - MYSQL_USER=snipeit
      - MYSQL_PASSWORD=secret
    volumes:
      - db_data:/var/lib/mysql

  snipeit:
    image: snipe/snipe-it:latest
    container_name: asset-snipeit
    depends_on:
      - db
    ports:
      - "8080:80"

  web:
    build:
      context: .
      dockerfile: web/Dockerfile.base
    container_name: asset-web
    ports:
      - "8000:8000"
    environment:
      - LLM_ENABLED=false # AI機能を無効化（決定論的ルールで稼働）
      - DATABASE_URL=sqlite:////app/data/scan_queue.db

  scanner:
    build:
      context: .
      dockerfile: scanner_scripts/Dockerfile.base
    container_name: asset-scanner
    environment:
      - LLM_ENABLED=false

volumes:
  db_data:
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

1. **段階的導入の徹底**: 検証環境での動作確認とログ採取を事前に行うこと。
2. **権限と監視の最小化**: 必要最小限の実行権限を割り当て、異常時のアラート通知を併設すること。

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
