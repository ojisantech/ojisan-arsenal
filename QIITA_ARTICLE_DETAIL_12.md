# 【第12弾 詳細解説】複合機スキャン ➔ Samba ➔ Dify自動RAG登録編 - 「現場にWeb画面からPDFをアップロードさせようとするな」スキャンPDFを共有フォルダに放り込むだけでDifyに自動RAG登録されるPython監視パイプライン構築PoC

**対象読者**: DX推進担当、情シス、LAN内RAG導入者
**主要技術スタック**: Python `watchdog`, Samba (SMB), Dify Dataset API
**ライセンス**: [MIT License](https://github.com/ojisantech/ojisan-arsenal/blob/main/LICENSE)
**検証環境・位置づけ**: 個人自宅ラボ（ホームラボ／仮想環境）における公開情報・OSSベースの個人研究（PoC）


💡 **【検証環境・個人研究（PoC）に関する注記】**
本記事は、筆者個人の自宅検証環境（ホームラボ／仮想環境）において、公開情報およびOSS（オープンソースソフトウェア）を用いて独自に構築・検証した個人研究（PoC）の記録です。特定の企業・団体の実環境や業務上の非公開情報とは一切関係ありません。

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
Difyを使ってLAN内FAQやナレッジ検索用のRAG（Retrieval-Augmented Generation）ボットを作ったことのある方なら、必ずこの壁にぶつかったことがあるはずです。

**「エンジニアは便利だと思って作ったのに、現場の利用者が誰もPDFやマニュアルを追加してくれない」**

理由は極めてシンプルです。
現場の業務担当者にとって、**「Webブラウザを開いて、Difyにログインして、該当のナレッジベースを選んで、ファイルアップロードダイアログを開いて、ファイルをドラッグ＆ドロップして、チャンク設定を確認して保存ボタンを押す」** という工程は、面倒くさすぎて絶対に定着しないからです。

現場で日常的に行われている唯一の行為は、**「複合機で紙の書類をスキャンして、いつもの共有フォルダ（Samba / NAS）にポイッと保存すること」** だけです。

そこで、**「共有フォルダにPDFが放り込まれた瞬間、裏側のPythonが検知してDifyのナレッジAPIに自動登録し、完了したら処理済みフォルダへ移動させる全自動パイプライン」** を構築しました。

現場の作業フローは**1ミリも変えずに**、LAN内AIが勝手に最新ナレッジを学習し続けます。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

```mermaid
sequenceDiagram
    autonumber
    actor User as 🏢 現場担当者 / 事務
    participant Copier as 🖨️ LAN内複合機
    participant NAS as 📂 Samba共有フォルダ (/mnt/samba)
    participant Watcher as 🐍 Python監視デーモン (watchdog)
    participant Dify as 🧠 Dify ナレッジ基盤 (Dataset API)

    User->>Copier: 書類を置いて「スキャン」ボタン押下
    Copier->>NAS: PDFをネットワーク共有フォルダへ自動送信
    Note over NAS: 新規ファイル作成イベント発生

    Watcher->>NAS: watchdog がファイル作成を検知
    Watcher->>Watcher: 書き込み完了待機 (2秒)
    Watcher->>Dify: POST /v1/datasets/{id}/document/create_by_file (自動アップロード)

    Dify->>Dify: 高品質インデックス化・自動チャンク・ベクトル保存
    Dify-->>Watcher: HTTP 200 OK (登録完了)

    Watcher->>NAS: ファイルを /mnt/samba/processed/ へ自動退避
    Note over User: 現場は何の画面も開く必要なし！
```

### 内部動作メカニズムのステップ解説
1. **実装のキモ：Python `watchdog` による共有フォルダ監視**:
   ファイルシステムのイベント検知には、Pythonの定番ライブラリ **`watchdog`** を使用します。
2. **メインループの起動スクリプト**:
   デーモンとして常駐させ、フォルダ内を監視し続けます。
3. **Docker Compose で超軽量にコンテナ常駐化**:
   監視スクリプト自体は、わずか数十MBのメモリしか消費しないため、軽量なPython Alpineコンテナで常駐させます。

---

## 3. 実装詳細とパラメータ完全解説

本アーキテクチャの要となるコアコードおよび主要設定の要点抜粋です。

### コア実装スクリプト / 設定（抜粋）
```python
# コア実装ロジック（要点抜粋）
import os
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DIFY_API_URL = os.getenv("DIFY_API_URL", "http://localhost/v1")
DIFY_DATASET_API_KEY = os.getenv("DIFY_DATASET_API_KEY", "dataset-xxxxxxxxxxxx")
DATASET_ID = os.getenv("DATASET_ID", "your-dataset-uuid")
SAMBA_WATCH_DIR = os.getenv("SAMBA_WATCH_DIR", "/mnt/samba/knowledge")
PROCESSED_DIR = os.path.join(SAMBA_WATCH_DIR, "processed")

class SambaToDifyHandler(FileSystemEventHandler):
    def on_created(self, event):
        # ディレクトリ作成イベントは無視
        if event.is_directory:
            return

        file_path = event.src_path
        # 処理済みフォルダ内のファイルは無視
        if "processed" in file_path:
            return

        print(f"[+] New file detected: {file_path}")

        # 複合機からの書き込み完了を確実に待つ（ネットワークバッファ対策）
        time.sleep(2)

        # Difyへのアップロード実行
        self.upload_to_dify(file_path)

    def upload_to_dify(self, file_path):
        url = f"{DIFY_API_URL}/datasets/{DATASET_ID}/document/create_by_file"
        headers = {
            "Authorization": f"Bearer {DIFY_DATASET_API_KEY}"
        }

        filename = os.path.basename(file_path)
        print(f"[*] Uploading {filename} to Dify Dataset {DATASET_ID}...")

        try:
            with open(file_path, "rb") as f:
                files = {
                    "file": (filename, f, "application/pdf")
                }
                # Difyの高品質インデックス・自動チャンク化ルールを指定
                data = {
                    "data": '{"indexing_technique": "high_quality", "process_rule": {"mode": "automatic"}}'
                }

                response = requests.post(url, headers=headers, files=files, data=data, timeout=60)

            if response.status_code == 200:
                print(f"[SUCCESS] Successfully uploaded {filename} to Dify.")
                self.move_to_processed(file_path, filename)
            else:
                print(f"[ERROR] Failed to upload {filename}. Status: {response.status_code}, Msg: {response.text}")

        except Exception as e:
            print(f"[ERROR] Exception processing {filename}: {str(e)}")

    def move_to_processed(self, file_path, filename):
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        dest_path = os.path.join(PROCESSED_DIR, filename)
        os.rename(file_path, dest_path)
        print(f"[+] Moved {filename} -> {dest_path}")
```

### 主要パラメータ・設定値の技術的根拠
- **主要技術スタック（Python `watchdog`, Samba (SMB), Dify Dataset API）の選定と最小権限設計**:
  **複合機スキャン ➔ Samba ➔ Dify自動RAG登録編** - 「現場にWeb画面からPDFをアップロードさせようとするな」スキャンPDFを共有フォルダに放り込むだけでDifyに自動RAG登録されるPython監視パイプライン構築PoC の実現にあたり、外部の過剰な依存や特権常駐を排し、Python `watchdog`, Samba (SMB), Dify Dataset API を軸とした省フットプリントかつセキュアな実行境界を構成しています。
- **タイムアウト境界とフェイルソフト耐性**:
  ネットワーク遅延や対象機器の無応答時にもプロセス全体がブロッキングしないよう明示的なタイムアウトと例外隔離を設け、基幹業務への影響をゼロに抑えます。
- **べき等性（Idempotency）と監査トレーサビリティ（対象: DX推進担当、情シス、LAN内RAG導入者）**:
  同一処理を複数回実行しても状態が破綻しないべき等設計を採用し、実行結果・差分ログを確実に保全することで実務運用での再現性と安全性を担保します。
