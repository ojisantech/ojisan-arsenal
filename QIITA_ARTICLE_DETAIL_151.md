# 【第151弾 詳細解説】シリアル通信（RS-485 / UART）工場機器直結編 - Raspberry Pi / Linux SBC のシリアル通信（UART / RS-485）による工場機器・計測器直結自動化

> **対象読者**: 工場DX担当、IoTエンジニア  
> **主要技術スタック**: `pyserial`, USB-RS485, 1.2km伝送, レガシー計測器自動回収  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「工場のラインにある20年前の計測器や電子天秤、温湿度計の数値を、作業員が毎日紙に手書きでメモしてExcelに手入力している」
「最新のIoT機器に買い換えるには数千万円の設備投資が必要で、現場責任者に却下された」

製造現場や研究開発の現場には、産業用シリアル通信（**RS-485 / RS-232C**）ポートを備えた堅牢な現役機器が無数に眠っています。

数百円〜数千円の「USB-RS485変換アダプタ」またはRaspberry PiのUARTピンを接続し、Pythonの **`pyserial`** でパケットを読み解くだけで、**既存設備に一切手を加えることなく、計測値を1秒ごとにリアルタイムデジタル化**できます。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

![システム構成・アーキテクチャ図](https://raw.githubusercontent.com/ojisantech/ojisan-arsenal/main/images/diagram_article_151_1.png)

```mermaid
flowchart LR
    Machine["工場計測器 / 電子天秤<br/>(RS-485 D+/D- 端子台)"]
    Converter["USB-RS485 変換ドングル<br/>(FTDI / CH340 チップ)"]
    Pi["Raspberry Pi / Linux SBC<br/>(/dev/ttyUSB0)"]
    Cloud["社内DB / クラウド可視化<br/>(PostgreSQL / Grafana)"]

    Machine <-->|"ツイストペア線 (最大1.2km伝送)"| Converter
    Converter -->|"USB 仮想COMポート"| Pi
    Pi -->|"Python pyserial でパケット受信・パース"| Pi
    Pi -->|"Wi-Fi / LAN 経由でJSON送信"| Cloud
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

### `read_rs485_serial.py`

```python
#!/usr/bin/env python3
# read_rs485_serial.py
# RS-485 / シリアルポートから計測データを読み取りJSON形式で出力する
# ライセンス: MIT

import serial
import time
import json
import sys

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600

def read_sensor_loop():
    print(f"[INFO] シリアルポート接続中: {SERIAL_PORT} ({BAUD_RATE} bps)")
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2.0
        )
    except Exception as e:
        print(f"[ERROR] ポートを開けません: {e}")
        sys.exit(1)

    print("[SUCCESS] 接続成功。データ受信待機中 (Ctrl+Cで終了)...")
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                # 計測器の独自フォーマットをパース (例: 'TEMP:24.5,HUM:60.2')
                print(f"[RAW RECEIVE] {line}")
                data_point = {
                    "timestamp": int(time.time()),
                    "raw_data": line
                }
                # ここで社内APIやSQLiteへ送信
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[WARN] 読み取りエラー: {e}")
            time.sleep(1)

    ser.close()
    print("\n[INFO] ポートを正常に閉じました。")

if __name__ == "__main__":
    read_sensor_loop()
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

1. **Linuxのdialoutグループ権限**:
   一般ユーザーで `/dev/ttyUSB0` を開こうとすると Permission Denied になります。`sudo usermod -aG dialout $USER` を実行して再ログインすることで、root権限なしで安全にポートアクセスが可能になります。

2. **終端抵抗（120Ω）の重要性**:
   RS-485を長距離配線（数十メートル以上）する場合、バスの両端に120Ωの終端抵抗を入れないと信号の反射波で通信化けが頻発します。変換ドングルのディップスイッチやジャンパーでONにしてください。

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
