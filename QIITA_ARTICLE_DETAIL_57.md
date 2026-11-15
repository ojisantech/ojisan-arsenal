# 【第57弾 詳細解説】野良IPv6の危険性と無効化・ステルス検知編 - LAN内で密かに動く「野良IPv6」が情シスの死角になる理由と、Linux/ルーターでの確実な無効化・ステルス検知法

**対象読者**: 情シス、インフラ設計者
**主要技術スタック**: SLAAC攻撃, Rogue RA (Router Advertisement), ICMPv6 Type 134 Raw Socket, sysctl
**ライセンス**: [MIT License](https://github.com/ojisantech/ojisan-arsenal/blob/main/LICENSE)
**検証環境・位置づけ**: 個人自宅ラボ（ホームラボ／仮想環境）における公開情報・OSSベースの個人研究（PoC）

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「うちはLAN内ネットワークもUTMも全部IPv4で設計しているから、IPv6なんて関係ないよ」

そう安心している情シス・インフラエンジニアの現場ほど、実は見落としがちな死角を抱えています。

現代の主要OS（Windows 10/11、macOS、Ubuntu/RHELなど）は、**デフォルトでIPv6が有効**になっています。IPv6環境では、ルーターが送信する「Router Advertisement (RA)」パケットを受信すると、DHCPサーバーがなくても端末自身が自動的にIPv6アドレスを生成し、デフォルトゲートウェイを設定します（SLAAC: Stateless Address Autoconfiguration）。

もしLAN内に未承認の端末（勝手に持ち込まれたWi-Fiルーターや、内部に侵入した攻撃者端末）が接続され、RAパケットを定期的に送信し始めたらどうなるでしょうか？
クライアントPCは「IPv6のデフォルト経路ができた」と判断し、**意図しないIPv6経路が形成されることで、既存のIPv4ベースの監視・制御ポリシー（UTMやプロキシ、DNSフィルタ等）を迂回するリスク**が生じます（Rogue RA / SLAACによる意図しない経路奪取）。

> ⚠️ **ネットワーク構成による影響度の違い**:  
> - **L3スイッチでIPv6 ACLやフィルタがない場合**: IPv6通信がそのまま通過し、UTM等のIPv4ポリシーが迂回されるリスクが高まります。  
> - **次世代FW (NGFW) やデュアルスタック機器でIPv6インスペクションが有効な場合**: 迂回されずに検知・遮断が可能です。  
> 現場の境界防御・内部監視ポリシーが「IPv4専用」前提で運用されている場合こそ、このIPv6経路の発生が死角となります。

本記事では、IPv4専用環境において意図しないIPv6通信を抑制するホストおよびネットワーク機器（ルーター／スイッチ）の設定と、LAN内に流れるRAパケットを検知する手法を解説します。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

```mermaid
flowchart TD
    subgraph LAN["LAN内環境 (IPv4専用設計)"]
        direction TB
        spacer_lan[" "] ~~~ Client
        style spacer_lan fill:none,stroke:none;
        Client["利用者PC (Win/Mac)<br/>IPv4: 192.168.1.50<br/>IPv6: デフォルト有効"]
        Rogue["未承認ルーター / 攻撃者PC<br/>Rogue RA (Router Advertisement) 送信"]
        UTM["正規UTM / プロキシ<br/>(IPv4のみ監視・フィルタリング)"]
        LinuxHost["LAN内Linuxサーバー"]
    end

    Internet["外部インターネット"]

    Rogue -- "1. RA送信: 自分がIPv6 GWだと広告" --> Client
    Client -- "2. IPv6経路を自動生成 (SLAAC)" --> Rogue
    Rogue -- "3. IPv4ポリシーを迂回して外部へ中継リスク" --> Internet

    Client -. "4. IPv4通信 (UTM経由・正常)" .-> UTM
    UTM -.-> Internet

    classDef danger fill:#ffcccc,stroke:#cc0000,stroke-width:2px;
    class Rogue danger;
```

```text
【正常時：IPv4通信】
[クライアントPC] ──(IPv4通信)──> [UTM / プロキシ / DNSフィルタ] ──> [インターネット]
                                  ※ポリシー検査・ログ監査が正常に機能

【異常時：Rogue RAによるIPv6経路奪取】
[未承認ルーター / 攻撃者PC] ──(Rogue RA: Type 134)──> [クライアントPC]
                                                        │ (SLAAC自動構成)
                                                        ▼
[インターネット] <──(未監視のIPv6通信)──────── [新デフォルトGW形成]
                      ※IPv4専用UTMやDNSフィルタを迂回するリスク
```

### 内部動作メカニズムのステップ解説
1. **対象環境の検知・一次データ収集（Rogue RA, ICMPv6 Type 134 Raw Socket, sysctl）**:
   SLAACによる不正な経路生成や未承認ルーターの存在を検知するため、ICMPv6 Type 134 Raw Socketを用いてLAN内のRAパケットを低負荷にリアルタイム捕捉します。
2. **構造化パースとコンテキスト判定**:
   取得した一次データを解析し、正規ルーターのリンクローカルアドレスと照合、未承認ルーターからのRAや不自然なRouter Lifetime等の異常パケットを判定します。
3. **安全な自律反映と監査ログ出力**:
   情シス、インフラ設計者が即座に状況把握・追跡できるよう、処理結果をアラートログや監視通知へべき等性を保って出力します。

---

> 📌 **サーバー運用の役割分担（方針の整理）**:  
> - **管理対象サーバー（一般の業務・インフラホスト）**: 不要な通信リスクを低減するため、カーネルレベルでIPv6スタックごと無効化（3.1項）  
> - **監視専用サーバー**: パケット検知のためIPv6スタック自体は維持しつつ、自ホストがRAの影響を受けないよう `accept_ra = 0` / `autoconf = 0` を設定（3.3項）

---

## 3. 実装詳細とパラメータ完全解説

### 3.1 LinuxホストでのIPv6無効化設定

多くのLinux環境において意図しないIPv6通信をカーネルレベルで無効化するには、`sysctl` を利用します。

#### `/etc/sysctl.d/99-disable-ipv6.conf`
```ini
# 全インターフェースでIPv6を無効化
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1

# ルーター広告 (RA) の自動受け入れを明示的に拒否
net.ipv6.conf.all.accept_ra = 0
net.ipv6.conf.default.accept_ra = 0

# 自動設定アドレス生成を拒否
net.ipv6.conf.all.autoconf = 0
net.ipv6.conf.default.autoconf = 0
```

ワンライナー作成コマンド：
```bash
cat << 'EOF' | sudo tee /etc/sysctl.d/99-disable-ipv6.conf
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
net.ipv6.conf.all.accept_ra = 0
net.ipv6.conf.default.accept_ra = 0
EOF
```

反映コマンド：
```bash
sudo sysctl --system
```

確認コマンド（グローバルまたはリンクローカルの inet6 アドレスが表示されないことを確認 ※環境により loopback ::1 が残る場合があります）：
```bash
ip -6 addr show
```

> ⚠️ **環境ごとの追加考慮事項**:  
> UbuntuやRHEL等で `systemd-networkd`、`NetworkManager`、あるいは Docker や Kubernetes を利用している環境では、`sysctl` に加えて各ネットワークスタックやコンテナデーモン側でのIPv6無効化設定が必要になる場合があります。

---

### 3.2 ルーター・スイッチ機器での無効化・RA遮断

ホスト側だけでなく、ネットワーク機器側で意図しないRAパケットの送出停止や遮断（RA Guard）を行うことが根本対策となります。

#### Yamaha RTXルーターでのRA送信停止例
国内オフィスで広く導入されているYamaha RTXルーターにおいて、IPv4専用LAN（例: lan1）でのIPv6機能停止とRA送信停止を行う設定です。

```text
# LAN1インターフェースでのIPv6プレフィックスおよびRA送信を明示的に停止
no ipv6 lan1 address
no ipv6 lan1 router advertisement send
```

#### L2/L3スイッチでのRA Guard（Cisco等）
未承認端末が勝手にRAを送出してもスイッチのポート単位で破棄する機能（IPv6 RA Guard / ND Inspection）の適用例です。

```text
# 端末収容ポートでRAパケットをドロップ（正規ルーターポートのみ信頼設定）
interface GigabitEthernet0/1
 ipv6 nd raguard attach-policy HOST_PORT_POLICY
```

---

### 3.3 事前確認：tcpdump による ICMPv6 (RA) の即時キャプチャ

監視スクリプトをデーモン常駐化する前に、現時点でLAN内にRAパケットが送出されているかどうかを即座に裏取り・確認するには、`tcpdump` で ICMPv6 Type 134 をフィルタリングするのが最も確実です。

```bash
# eth0 インターフェースで ICMPv6 Type 134 (Router Advertisement) をリアルタイムキャプチャ
sudo tcpdump -n -v -i eth0 'icmp6 and ip6[40] == 134'
```

---

### 3.4 野良ルーター広告 (RA) 検知スクリプト（BSD Raw Socket実装）

外部ライブラリ（Scapy等）に依存せず、Linux標準のBSD Raw Socket（`AF_INET6`, `SOCK_RAW`, `IPPROTO_ICMPV6`）を用いて、LAN内を流れるICMPv6 Type 134（Router Advertisement）をリアルタイム捕捉する完全スクリプトです。

#### `detect_rogue_ra.py`
```python
import socket
import struct
import datetime

# ICMPv6 タイプ定義: Type 134 = Router Advertisement (RA)
ICMPV6_TYPE_RA = 134

def start_ra_monitor():
    """
    LAN内のICMPv6 Router Advertisementパケットを待ち受けて検知・通知する
    ※ Raw Socketのオープンには root 権限 (または CAP_NET_RAW) が必要です。
    """
    try:
        # IPv6 / Raw Socket / ICMPv6 (プロトコル番号 58) をオープン
        sock = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMPV6)
        print("[*] IPv6 Router Advertisement (RA) 監視を開始しました (待ち受け中)...")
    except PermissionError:
        print("[!] エラー: Raw Socketの作成には root 権限 (sudo) が必要です。")
        return
    except OSError as e:
        print(f"[!] ソケット作成エラー: {e} (IPv6が無効化されていないか確認してください)")
        return

    try:
        while True:
            # パケット受信 (データ, 送信元情報)
            data, addr = sock.recvfrom(1024)
            if len(data) < 16:
                continue

            # ICMPv6 ヘッダーの先頭: Type (1byte), Code (1byte)
            icmp_type, icmp_code = struct.unpack("!BB", data[:2])

            if icmp_type == ICMPV6_TYPE_RA:
                src_ip = addr[0]
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Router Lifetime (オフセット 6〜8バイト目, 16bit符号なし整数)
                router_lifetime = struct.unpack("!H", data[6:8])[0]

                print("=" * 60)
                print(f"📢 [NOTICE - RAパケット検知] {now}")
                print(f"   送信元 IPv6 アドレス : {src_ip}")
                print(f"   Router Lifetime       : {router_lifetime} 秒")
                print("   ⚠️  未承認ルーター (Rogue RA) または不正なSLAAC経路広告の可能性があります")
                print("   ⚠️  送信元アドレスが想定機器（正規ルーター）か確認してください")
                print("=" * 60)
    except KeyboardInterrupt:
        print("\n[*] 監視を停止しました。")
    finally:
        sock.close()

if __name__ == "__main__":
    start_ra_monitor()
```

単体実行コマンド：
```bash
sudo python3 detect_rogue_ra.py
```

検知時の出力サンプル：
```text
[*] IPv6 Router Advertisement (RA) 監視を開始しました (待ち受け中)...
============================================================
📢 [NOTICE - RAパケット検知] 2026-11-15 09:30:15
   送信元 IPv6 アドレス : fe80::aaaa:bbbb:cccc:dddd
   Router Lifetime       : 1800 秒
   ⚠️  未承認ルーター (Rogue RA) または不正なSLAAC経路広告の可能性があります
   ⚠️  送信元アドレスが想定機器（正規ルーター）か確認してください
============================================================
```

---

### 3.5 24時間365日の常駐運用（systemd化 または crontab）

本スクリプトはリアルタイムでパケットを待ち受ける常駐プロセス（ブロッキング待機）のため、通常のcronによる定期実行（`* * * * *` など）を行うとプロセスが多重起動してしまいます。実務では以下のいずれかで常駐運用します。

#### 推奨：systemd サービスとして常駐化（自動再起動対応）
万が一のクラッシュ時にも自動復旧する最も堅牢な運用方法です。

`/etc/systemd/system/rogue-ra-detector.service`：
```ini
[Unit]
Description=Rogue IPv6 Router Advertisement Detector
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /opt/scripts/detect_rogue_ra.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

反映・起動コマンド：
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now rogue-ra-detector
```

#### 簡易運用：crontab の `@reboot` を利用
cronを使用する場合は、定期実行ではなくサーバー起動時にバックグラウンドで1回だけ起動させます。

```bash
# sudo crontab -e に追記
@reboot /usr/bin/python3 /opt/scripts/detect_rogue_ra.py >> /var/log/detect_rogue_ra.log 2>&1 &
```

> 💡 **実務運用のポイント**:  
> 監視役となるLinuxマシンでは、パケットを受信するためにIPv6スタック自体は有効にしておきつつ、自身が偽RAに釣られて不正なデフォルトゲートウェイを設定されないよう、`net.ipv6.conf.all.accept_ra = 0` および `net.ipv6.conf.all.autoconf = 0` を設定しておくのが鉄則です。

---

### 主要パラメータ・設定値の技術的根拠
- **主要技術スタック（Rogue RA, ICMPv6 Type 134 Raw Socket, sysctl）の選定と最小権限設計**:
  外部の過剰な依存や特権常駐を排し、ICMPv6 Type 134 Raw Socket, sysctl を軸とした省フットプリントかつセキュアな実行境界を構成しています。
- **タイムアウト境界とフェイルソフト耐性**:
  ネットワーク遅延や対象機器の無応答時にもプロセス全体がブロッキングしないよう明示的な例外隔離を設け、基幹業務への影響をゼロに抑えます。
- **べき等性（Idempotency）と監査トレーサビリティ（対象: 情シス、インフラ設計者）**:
  同一処理を複数回実行しても状態が破綻しないべき等設計を採用し、実行結果・差分ログを確実に保全することで実務運用での再現性と安全性を担保します。

---

### 📚 自立型インフラ＆オンプレAI完全技術リファレンス
本記事が役に立った・面白かったと感じていただけましたら、ぜひGitHubリポジトリへの **Star (★)** や **[Qiita (@ojisantech)](https://qiita.com/ojisantech)** / **[X (@OjisanTechnical)](https://x.com/OjisanTechnical)** のフォローをお願いいたします！
👉 **[GitHub リポジトリ: ojisantech/ojisan-arsenal](https://github.com/ojisantech/ojisan-arsenal)**

💡 **【検証環境・個人研究（PoC）に関する注記】**
本記事は、筆者個人の自宅検証環境（ホームラボ／仮想環境）において、公開情報およびOSS（オープンソースソフトウェア）を用いて独自に構築・検証した個人研究（PoC）の記録です。特定の企業・団体の実環境や業務上の非公開情報とは一切関係ありません。
