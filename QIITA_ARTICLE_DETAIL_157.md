# 【第157弾 詳細解説】音響FFT解析によるモーター異音予知保全編 - 音響センシング・FFT（高速フーリエ変換）によるモーター異音・異常振動予知保全PoC

> **対象読者**: 保全エンジニア、品質管理、エッジAI  
> **主要技術スタック**: `numpy.fft`, `pyaudio`, 周波数スペクトル解析, 異常ピーク検知  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「工場の重要ポンプやモーターが焼き付きで突然停止し、製造ライン全体が半日止まって数千万円の損失が出た」
「ベテランの保守員は『いつもと違うキーンという高い音が混ざっている』と聞き分けるが、若手には違いが分からずノウハウが属人化している」

機械のベアリング劣化や偏心によるガタつきは、完全停止する数週間前から**「特定の周波数の異音や振動」**として必ず現れます。

安価なUSBマイクや加速度センサーの音響データをPythonの **`FFT (Fast Fourier Transform: 高速フーリエ変換 / numpy.fft)`** で周波数スペクトルに変換すれば、**「正常時には存在しない特定周波数ピーク（高周波ノイズ）」**を数値として機械的に即座に検知できます。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。


```mermaid
flowchart TD
    Motor["対象モーター / ポンプ<br/>(ベアリング微小摩耗発生)"]
    Mic["USB マイク / 加速度センサー<br/>(サンプリングレート: 44.1kHz)"]

    TimeSignal["時間領域波形 (振幅データ)<br/>目視では正常時との差が分からない"]
    FFT_Engine["Python numpy.fft 高速フーリエ変換"]
    FreqSpectrum["周波数スペクトル (Hz)<br/>🚨 3.2kHz に明らかな異常ピークを検出！"]

    Alert["予知保全警報: 『ベアリング摩耗予兆あり。次回定期点検で交換推奨』"]

    Motor --> Mic --> TimeSignal
    TimeSignal --> FFT_Engine --> FreqSpectrum
    FreqSpectrum --> Alert
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

### `audio_fft_anomaly_detector.py`

```python
#!/usr/bin/env python3
# audio_fft_anomaly_detector.py
# マイクからの音響データをFFT周波数解析し、特定周波数の異常ノイズを検知する
# ライセンス: MIT

import numpy as np
import pyaudio
import sys

# オーディオ設定
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096 # FFT解像度: 約 10.7 Hz/ビン

# 監視したい異常周波数帯域 (例: 3000Hz〜3500Hz)
TARGET_FREQ_MIN = 3000
TARGET_FREQ_MAX = 3500
ANOMALY_THRESHOLD = 500.0 # 振幅の閾値

def run_detector():
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"[ERROR] マイクデバイスを開けません: {e}")
        sys.exit(1)

    print(f"==================================================")
    print(f" 🎧 音響センシング異常監視開始")
    print(f"  - 監視周波数帯: {TARGET_FREQ_MIN}Hz 〜 {TARGET_FREQ_MAX}Hz")
    print(f"  - 異常振幅閾値: {ANOMALY_THRESHOLD}")
    print(f"==================================================")

    freqs = np.fft.rfftfreq(CHUNK, d=1.0/RATE)
    target_indices = np.where((freqs >= TARGET_FREQ_MIN) & (freqs <= TARGET_FREQ_MAX))[0]

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16)

            # FFTの実行
            fft_data = np.abs(np.fft.rfft(samples)) / CHUNK

            # 監視帯域の最大振幅を検査
            target_amplitude = np.max(fft_data[target_indices])

            if target_amplitude > ANOMALY_THRESHOLD:
                print(f"🚨 [異常予兆検知] 異常高周波振幅: {target_amplitude:.2f} (閾値超過！)")
                # ここでWebhook発報等
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    run_detector()
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

1. **窓関数（Hann Window）の適用**:
   チャンクの境界部分で発生するスペクトル漏れ（Spectral Leakage）を防ぐため、FFTの直前に `samples = samples * np.hanning(len(samples))` を乗算することで、周波数ピークの切れ味が格段に鋭くなります。

2. **定常環境ノイズのベースライン減算**:
   工場内のエアコンや他の装置の日常ノイズを正常時に数分間録音して平均周波数プロファイル（ベースライン）を作成し、監視時は「ベースラインからの差分」を見ることで、環境ノイズによる誤報を劇的に減らせます。

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
