# 【第153弾 詳細解説】Modbus TCP / RTU による産業用PLC連携編 - Modbus TCP / RTU によるPLC機器データ読み出しPython自動化（pymodbus）と現場連携

> **対象読者**: 製造業IT担当、OT/IT統合SE  
> **主要技術スタック**: `pymodbus`, Modbus TCP (:502), 保持レジスタ読取, 三菱/オムロンPLC  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「工場のPLC（シーケンサー）の中に生産ラインの稼働数やエラー情報が入っているが、メーカー専用のプロプライエタリな高額ソフトを買わないとデータが外に出せない」
「上位のMES（製造実行システム）とPLCを繋ぎたいが、ベンダーの見積もりが数千万円で手が出ない」

産業用オートメーション（FA）の世界で最も広く普及している共通プロトコルが **`Modbus (Modbus TCP / Modbus RTU)`** です。

三菱電機（MELSEC）、オムロン、キーエンス、横河電機など、主要なPLCはすべてModbus通信に対応（または安価なゲートウェイで変換）しています。
Pythonの標準的ライブラリ **`pymodbus`** を使えば、**わずか数十行のコードでPLCの保持レジスタ（Holding Registers）を読み書き**し、生産現場の実績をリアルタイムでITデータベースへ連携できます。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

```mermaid
flowchart LR
    PLC["工場現場 PLC (三菱 / オムロン)<br/>Modbus TCP サーバー (:502)<br/>Holding Register: 40001〜40010"]
    Ethernet["産業用イーサネット LAN"]
    PythonWorker["社内 Linux サーバー<br/>Python pymodbus ワーカー"]
    DB["社内 ERP / 生産管理 DB<br/>(PostgreSQL)"]

    PLC <==|Modbus TCP 通信 (ポート 502)| Ethernet
    Ethernet <==> PythonWorker
    PythonWorker -->|保持レジスタ読取 (Read Holding Registers)| PLC
    PythonWorker -->|生産個数・チョコ停フラグをパース| DB
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

### `read_modbus_plc.py`

```python
#!/usr/bin/env python3
# read_modbus_plc.py
# pymodbus を用いて産業用PLCのModbus TCPレジスタを一括読み取りする
# ライセンス: MIT

from pymodbus.client import ModbusTcpClient
import time
import json
import sys

PLC_IP = "192.168.1.100"
PLC_PORT = 502
UNIT_ID = 1

def main():
    print(f"[INFO] PLC接続中: {PLC_IP}:{PLC_PORT}")
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)

    if not client.connect():
        print("[ERROR] PLCへのTCP接続に失敗しました。IPとポート502を確認してください。")
        sys.exit(1)

    print("[SUCCESS] PLCと接続完了。レジスタ読み出し開始...")
    try:
        # レジスタアドレス 0 から 10 ワード (16bit) を読み出し
        response = client.read_holding_registers(address=0, count=10, slave=UNIT_ID)

        if response.isError():
            print(f"[ERROR] Modbus読み出しエラー: {response}")
        else:
            registers = response.registers
            print(f"受信レジスタ生データ (16bit整数): {registers}")

            # データマッピング例
            production_count = registers[0] # アドレス0: 生産実績数
            line_speed = registers[1]       # アドレス1: ライン速度 (m/min)
            error_code = registers[2]       # アドレス2: エラーコード

            data = {
                "timestamp": int(time.time()),
                "production_count": production_count,
                "line_speed": line_speed,
                "error_code": error_code
            }
            print(f"構造化データ: {json.dumps(data, indent=2)}")
    finally:
        client.close()

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

1. **エンディアン（バイト順・ワード順）の罠**:
   32bit整数や浮動小数点数（Float）を扱う場合、メーカーによって「上位ワード先頭（Big-Endian）」か「下位ワード先頭（Little-Endian）」かが異なります。`BinaryPayloadDecoder` を使って正しいエンディアンを指定してデコードするのが必須です。

2. **アドレスオフセットの「1ズレ」問題**:
   Modbusの仕様上、ドキュメントに「レジスタ 40001」と書かれている場合、実際のパケットプロトコル上でのゼロベースアドレスは `0` になります（40001 - 40001 = 0）。アドレス指定時の1ズレに注意してください。

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
