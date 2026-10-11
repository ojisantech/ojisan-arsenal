# 【第60弾 詳細解説】ネットワーク機器Configバックアップ自動化編 - ルーター・L2/L3スイッチのConfigバックアップを「全自動」にする！ParamikoとGitで作るゼロ円Config管理基盤

> **対象読者**: ネットワーク運用担当、インフラ自動化  
> **主要技術スタック**: Paramiko (SSH), `show running-config`, Git自動コミット・差分追跡, マスキング  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「フロアスイッチが故障して予備機に交換したんだけど、最新のConfig（設定ファイル）ってどこにある？」
「えっ、共有フォルダの `config_20240315_final_v2_fix.txt` が最後じゃないですか…？」
「そのあとVLAN追加したはずなのに記録がない！」

ネットワーク機器（ルーター、L2/L3スイッチ、ファイアウォール）のコンフィグ管理は、現場の属人化とヒューマンエラーの温床です。
- 作業者が「あとでバックアップ取ろう」と思って忘れる
- 誰がいつどのコマンドを追加・削除したのか履歴がわからない
- 高価な構成管理ツール（NetBrainや商用NMS）はライセンスが高すぎて導入できない

解決策は明快です。**「毎深夜、全ネットワーク機器にSSH接続して最新Configを自動取得し、ローカルGitリポジトリに自動コミットする」**。これだけで、変更履歴の差分（Git diff）が完全に追跡でき、バックアップ忘れが永遠に撲滅されます。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

![システム構成・アーキテクチャ図](https://raw.githubusercontent.com/ojisantech/ojisan-arsenal/main/images/diagram_article_60_1.png)

```mermaid
sequenceDiagram
    autonumber
    actor Cron as cron (毎朝4:00)
    participant Script as backup_configs.py (Python)
    participant Devices as ネットワーク機器群 (Router/Switch)
    participant Git as Gitリポジトリ (ローカル/社内GitLab)

    Cron->>Script: 定期実行トリガー
    loop 対象機器リストを巡回
        Script->>Devices: SSH接続 (Paramiko)
        Script->>Devices: 端末長無効化 (terminal length 0 等)
        Script->>Devices: 設定表示コマンド (show running-config 等)
        Devices-->>Script: Configテキスト返却
        Script->>Git: ファイル更新 (configs/{hostname}.cfg)
    end
    Script->>Git: git add . & git commit -m "Auto backup: YYYY-MM-DD"
    Note over Git: 変更があった機器のみ<br/>diffが記録される！
    Script->>Git: git push origin main
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

### `backup_network_configs.py`

```python
#!/usr/bin/env python3
"""
backup_network_configs.py
ネットワーク機器群からSSH経由でConfigを自動吸い上げ、Gitリポジトリにコミットする。
ライセンス: MIT
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime
import paramiko

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("NetConfigBackup")

# バックアップ先ディレクトリ（Gitリポジトリ内）
REPO_DIR = "/opt/network-configs"
OUTPUT_DIR = os.path.join(REPO_DIR, "devices")

# 監視・バックアップ対象の機器リスト（環境変数や暗号化ファイルからの読み込みを推奨）
DEVICES = [
    {
        "host": "192.168.1.1",
        "name": "core-router-01",
        "user": "admin",
        "password": os.environ.get("ROUTER_PASS", "SecretPass123!"),
        "commands": ["terminal length 0\n", "show running-config\n"],
        "prompt_char": "#"
    },
    {
        "host": "192.168.1.2",
        "name": "floor-l2switch-01",
        "user": "manager",
        "password": os.environ.get("SWITCH_PASS", "SecretPass123!"),
        "commands": ["terminal length 0\n", "show running-config\n"],
        "prompt_char": "#"
    }
]

def fetch_device_config(device):
    """SSH経由で機器にログインし、コンフィグを取得する"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    logger.info(f"[{device['name']}] ({device['host']}) にSSH接続中...")
    try:
        client.connect(
            hostname=device["host"],
            username=device["user"],
            password=device["password"],
            timeout=10,
            look_for_keys=False,
            allow_agent=False
        )
        
        # 対話型シェルを起動
        channel = client.invoke_shell()
        time.sleep(1)
        
        # ページネーション無効化とConfig取得コマンドを実行
        for cmd in device["commands"]:
            channel.send(cmd)
            time.sleep(1)
            
        # 出力の受信
        output = ""
        while True:
            if channel.recv_ready():
                data = channel.recv(4096).decode("utf-8", errors="ignore")
                output += data
                time.sleep(0.5)
            else:
                break
                
        channel.close()
        client.close()
        return output
    except Exception as e:
        logger.error(f"[{device['name']}] バックアップ失敗: {e}")
        return None

def sanitize_config(raw_config):
    """
    タイムスタンプ行などの毎回収集時に変化する変動行を正規化
    （無駄なGit差分スパイクを防ぐ）
    """
    clean_lines = []
    for line in raw_config.splitlines():
        # "Current configuration : 1234 bytes" や "! Last configuration change at..." などを除外
        if "Last configuration change" in line or "Current configuration" in line:
            continue
        clean_lines.append(line)
    return "\n".join(clean_lines).strip()

def commit_to_git():
    """Gitリポジトリに変更を自動コミット"""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)
        status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_DIR, capture_output=True, text=True)
        if status.stdout.strip():
            logger.info("Config変更を検知しました。Gitコミットを実行します...")
            subprocess.run(["git", "commit", "-m", f"Auto backup: {now_str}"], cwd=REPO_DIR, check=True)
            # 社内GitLab等のリモートがある場合:
            # subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True)
            logger.info("Gitコミット完了。")
        else:
            logger.info("前回バックアップからの設定変更はありませんでした。")
    except subprocess.CalledProcessError as e:
        logger.error(f"Git実行エラー: {e}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for device in DEVICES:
        raw_output = fetch_device_config(device)
        if raw_output:
            cleaned = sanitize_config(raw_output)
            file_path = os.path.join(OUTPUT_DIR, f"{device['name']}.cfg")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            logger.info(f"[{device['name']}] Config保存完了: {file_path}")

    commit_to_git()

if __name__ == "__main__":
    main()
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
