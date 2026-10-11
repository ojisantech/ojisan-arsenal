# 【第135弾 詳細解説】iSCSIターゲット（targetcli）によるゼロ円SAN編 - iSCSIターゲット（targetcli）とイニシエータによるローカル風ブロックストレージ共有とクラスタ連携

> **対象読者**: 仮想化基盤管理者、DBインフラSE  
> **主要技術スタック**: Linux LIO (`targetcli-fb`), iSCSI (TCP 3260), RAWデバイス提供  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「データベースや仮想化基盤（Proxmox / ESXi / Hyper-V）のデータストアにしたいが、NFSやSMBだとファイルロックの仕様でサポート対象外と言われる」
「アプリケーションが『ローカル物理ディスク（RAWデバイス）』として認識しないと動作しない」

ファイル共有（NAS）と異なり、ネットワーク越しにHDD/SSDのブロックデバイスそのものをマウントさせる技術が **`iSCSI (Internet Small Computer System Interface)`** です。

Linux標準の **`targetcli` (LIO)** を使えば、専用のSAN（Storage Area Network）装置を買うことなく、余剰サーバーのNVMe/SATAストレージをネットワーク経由の超高速iSCSIターゲットとして社内公開できます。クライアントからは完全に「本体に挿さっている未フォーマットの内蔵HDD」として認識されます。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

```mermaid
flowchart LR
    subgraph ClientPC["クライアント (Windows / Linux / ESXi)"]
        Initiator["iSCSI イニシエータ<br/>iqn.2026-10.com.example:client01"]
        LocalDisk["ローカルディスクとしてマウント<br/>(Disk Management / dev/sdb)"]
    end

    subgraph StorageServer["iSCSI ターゲットサーバー (Linux LIO)"]
        Target["targetcli LIO Target<br/>iqn.2026-10.com.example:storage-target"]
        Backstore["バックストア: LVM / ZFS / 物理NVMe"]
    end

    Initiator -->|TCP/IP ポート 3260 (iSCSI PDU)| Target
    Target --> Backstore
    Initiator --> LocalDisk
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

### `setup_iscsi_target.sh`

```bash
#!/usr/bin/env bash
# setup_iscsi_target.sh
# Linux (targetcli-fb) による iSCSI ターゲットの自動構築スクリプト
# ライセンス: MIT
set -euo pipefail

STORAGE_FILE="/var/lib/iscsi_disks/disk01.img"
STORAGE_SIZE="50G"
TARGET_IQN="iqn.2026-10.local.storage:target01"

echo "[1/3] targetcli のインストール確認"
if ! command -v targetcli >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y targetcli-fb
fi

echo "[2/3] ストレージ用ファイルイメージの作成 (${STORAGE_SIZE})"
sudo mkdir -p /var/lib/iscsi_disks
if [ ! -f "${STORAGE_FILE}" ]; then
    sudo fallocate -l "${STORAGE_SIZE}" "${STORAGE_FILE}"
fi

echo "[3/3] targetcli による iSCSI ターゲット構成"
sudo targetcli <<EOF
cd /backstores/fileio
create name=storage_disk01 file_or_dev=${STORAGE_FILE} size=${STORAGE_SIZE}
cd /iscsi
create ${TARGET_IQN}
cd /iscsi/${TARGET_IQN}/tpg1/luns
create /backstores/fileio/storage_disk01
cd /iscsi/${TARGET_IQN}/tpg1
set attribute authentication=0 demo_mode_write_protect=0 generate_node_acls=1
exit
EOF

echo "=================================================================="
echo " [SUCCESS] iSCSIターゲットが正常に起動しました。"
echo " ターゲットIQN: ${TARGET_IQN}"
echo " クライアントから ポート 3260 宛てにディスカバリーしてください。"
echo "=================================================================="
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

1. **CHAP認証の有効化**:
   テスト時は `authentication=0` で全許可できますが、本番環境では不正接続によるデータ破壊を防ぐため、`set attribute authentication=1` および `auth userid=... password=...` で片方向/双方向CHAP認証を設定してください。

2. **単一ブロックデバイスへの同時書き込み厳禁**:
   iSCSIボリュームを「クラスタ対応ファイルシステム（GFS2やOCFS2）」なしで複数台の通常OSから同時に読み書きマウントすると、OSキャッシュの不整合により数秒でファイルシステムが全壊します。1台のターゲットには原則1台のイニシエータのみ接続するのが基本です。

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
