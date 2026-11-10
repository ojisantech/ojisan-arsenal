# 【第44弾 詳細解説】PXEネットワークブート無人インストール編 - パソコンと追加NICでPXEネットワークブート環境構築 USBメモリ不要、LAN経由でOSを一発自動インストールする

> **対象読者**: キッティング担当、情シス、製造SE、インフラエンジニア  
> **主要技術スタック**: VirtualBox (USB 3.0 Passthrough), `dnsmasq` (DHCP/TFTP), `nginx` (HTTP), GRUB (`grubnetx64`), Ubuntu `autoinstall` (cloud-init), Docker Compose  
> **ライセンス**: [MIT License](https://github.com/ojisantech/ojisan-arsenal/blob/main/LICENSE)  
> **検証環境・位置づけ**: 個人自宅ラボ（ホームラボ／仮想環境）における公開情報・OSSベースの個人研究（PoC）  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
LAN内PC端末入れ替えや、ホワイトボックスサーバー、ミニPCを10台、20台とキッティングする際、多くのエンジニアがこの「不毛な単純作業」で丸一日を潰します。

1. **USBメモリにUbuntuのISOを焼く**
2. **PCのUSBポートに挿す**
3. **キーボードを繋いでF12を連打してブートメニューを出す**
4. **インストーラーの質問（言語、タイムゾーン、ユーザー名、パーティション）に手動で答える**
5. **終わったらUSBを抜いて、次のPCへ……**

台数が増えれば増えるほど、USBメモリの抜き差しと待ち時間で疲弊し、どこかの端末で設定ミス（タイポ）が発生します。

本職のインフラエンジニアは、USBメモリを使いません。  
**「LANケーブルを挿して電源を入れたら、自動的にネットワーク経由でインストーラーが降ってきて、ユーザー入力ゼロでOSインストールが完結するPXE（Preboot eXecution Environment）ネットワークブート」** を使います。

本記事では、手元のWindowsノートPC上のVirtualBox（Ubuntu VM）を活用し、**`dnsmasq` ＋ `nginx`（Docker）＋ `autoinstall (cloud-init)`** を組み合わせた完全無人PXEキッティング環境の構築手順と、現場で必ずハマる「TFTP不達問題」の完全解決策を解説します。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

```mermaid
sequenceDiagram
    autonumber
    actor Tech as 👷 作業員 (LANケーブル直結＆電源ON)
    participant Client as 🖥️ キッティング対象PC (UEFI PXE)
    participant DNS as 📡 pxe-dnsmasq (DHCP / TFTP)
    participant HTTP as 🌐 pxe-http (Nginx :80)

    Tech->>Client: LAN直結＆電源ON (キーボード操作不要)
    Client->>DNS: DHCP Discover (Option 60: PXEClient)
    DNS-->>Client: DHCP Offer (IP: 10.254.254.x, next-server: 10.254.254.1, bootfile: bootx64.efi)
    
    Client->>DNS: TFTP GET: bootx64.efi (Shimローダー)
    DNS-->>Client: bootx64.efi 転送
    Client->>DNS: TFTP GET: grubx64.efi (ネットワーク対応GRUB) & grub.cfg
    DNS-->>Client: GRUBバイナリ & メニュー定義転送
    
    Note over Client: ⚡ GRUBメニュー起動！ 低速TFTPから高速HTTPへ昇格
    Client->>HTTP: HTTP GET: /casper/vmlinuz & /casper/initrd
    HTTP-->>Client: カーネル＆initrd 高速転送
    Client->>HTTP: HTTP GET: /ubuntu.iso
    HTTP-->>Client: Live Server ISOストリーミング
    Client->>HTTP: HTTP GET: /cloud-init/user-data & meta-data
    HTTP-->>Client: autoinstall 自動応答YAML転送
    
    Note over Client: ⚡ 完全無人インストール自動実行！<br/>パーティション作成、初期ユーザー、SSH導入
    Client-->>Client: 完了後、自動シャットダウン / 再起動
    Note over Tech: 🎉 キッティング完了！
```

### 内部動作メカニズムのステップ解説

1. **完全閉域直結（`10.254.254.0/24`）による野良DHCPの完全防止**:
   社内LANでPXEサーバーを立てると、既存のDHCPと競合して業務端末の通信を破壊する「野良DHCP障害」を起こします。本設計では増設したUSB-C LANアダプターに対象PCをLAN直結し、`10.254.254.0/24` の完全閉域網を敷くことで、社内ネットワークへの影響を物理的にゼロに抑えます。

2. **【現場実証】数時間を溶かした「DHCPは通るのにTFTPだけ死ぬ」問題とUSBパススルー突破**:
   Windowsホスト上のVirtualBoxで「ブリッジアダプター」を使用して直結PXE環境を組むと、極めて厄介な現象が発生します。
   * **現象**: クライアントPCはDHCP Discoverを送り、`10.254.254.x` のIPは正常に取得できる。しかし直後のTFTP接続要求（UDP 69番）がサーバーに届かず、`TFTP open timeout` で数分間フリーズしたのちSSD起動に落ちる。
   * **苦闘の軌跡**: Windows Defender無効化、プロミスキャスモード変更、LANケーブル交換、dnsmasqのTFTP設定見直しなどを幾度繰り返してもパケットは1つも届かず、数時間以上が完全に空費される。
   * **原因の真相**: Windowsホスト側の VirtualBox NDIS6 Bridged Networking Driver が、USB-C LANアダプター経由の低レイヤUDPパケット（TFTP）を途中で遮断・ドロップしていた。
   * **根本解決策**: 仮想ブリッジを完全無効化し、VirtualBoxの **USB 3.0 (xHCI) フィルター** でUSB-C LANアダプターをLinux VMに直接パススルー。Windowsのネットワークスタックを100%バイパスすることで、TFTP通信が確実に開通する。

3. **Linuxカーネルでの命名規則（`enx<MACアドレス>`）への追従とコンテナ再起動**:
   USBパススルーへ切り替えると、仮想NIC名（`enp0s8`等）が消滅し、Predictable Network Interface Names に従い **`enx<MACアドレス>`（例：`enx806d97194b46`）** として認識されます。
   Netplan（`/etc/netplan/99-static-ip.yaml`）および `dnsmasq.conf` の `interface` 句を直ちに物理NIC名へ更新し、`docker compose up -d --force-recreate` でコンテナを再バインドすることで、TFTP/HTTP配信が即座に起動します。

4. **ネットワーク対応GRUB (`grubnetx64.efi.signed`) の採用**:
   Ubuntu ISO直下の `grubx64.efi` はローカルCD/USB専用でネットワークドライバを持ちません。ISO内のdebパッケージから抽出した `grubnetx64.efi.signed` をTFTPに配置することで、GRUB起動後にHTTPプロトコルへ昇格し、GBクラスのISOイメージを爆速ストリーミングします。

---

## 3. 実装詳細とパラメータ完全解説

本アーキテクチャの要となるコアコードおよび主要設定の要点抜粋です。

### コア実装スクリプト / 設定（抜粋）

#### 1. Netplan 設定 (`/etc/netplan/99-static-ip.yaml`)
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enx806d97194b46:   # USBパススルーされたキッティング専用NIC
      dhcp4: no
      addresses:
        - 10.254.254.1/24
      # 閉域網のためデフォルトゲートウェイ・DNSは設定しない
```

#### 2. dnsmasq 設定 (`dnsmasq/dnsmasq.conf`)
```ini
port=0
interface=enx806d97194b46
bind-interfaces

# DHCPリース範囲
dhcp-range=10.254.254.50,10.254.254.150,12h
dhcp-option=3
dhcp-option=6

# TFTP有効化
enable-tftp
tftp-root=/srv/tftp

# クライアントアーキテクチャ自動判別 (UEFI x86_64 / BIOS)
dhcp-match=set:efi-x86_64,option:client-arch,7
dhcp-match=set:efi-x86_64,option:client-arch,9
dhcp-match=set:bios,option:client-arch,0

dhcp-boot=tag:efi-x86_64,bootx64.efi
dhcp-boot=tag:bios,pxelinux.0

log-dhcp
```

#### 3. GRUB設定 (`tftp/grub.cfg`)
```text
set default="0"
set timeout=5

menuentry "Ubuntu 24.04 Auto Install (HTTP)" {
    set gfxpayload=keep
    linux (http,10.254.254.1)/casper/vmlinuz ip=dhcp url=http://10.254.254.1/ubuntu.iso autoinstall ds=nocloud-net\;s=http://10.254.254.1/cloud-init/ ---
    initrd (http,10.254.254.1)/casper/initrd
}
```

#### 4. autoinstall 設定 (`html/cloud-init/user-data`)
```yaml
#cloud-config
autoinstall:
  version: 1
  locale: ja_JP.UTF-8
  keyboard:
    layout: jp
  identity:
    hostname: pxe-client
    username: ubuntu
    password: "$6$salt$yjWjuAFfgUnLR2vKIfOlt1kj5vCHf82eTnwff.EaHThL13zSmfxL6elnOnOlLJqhWKI7Iej7KLWS/WW8myUeF1" # 平文: ubuntu
  ssh:
    install-server: yes
    allow-pw: yes
  storage:
    layout:
      name: direct
```

---

## 4. トラブルシューティング対応表と現場アンチパターン

| 現象・エラー | 原因 | 解決策 |
|---|---|---|
| **DHCP取得後に `TFTP open timeout` でPXE停止** | WindowsホストのNDISブリッジがUDP 69番をブロック | VirtualBoxのブリッジをやめ、USB 3.0 (xHCI) フィルターでUSB-C LANアダプターを直接Linuxゲストへパススルーする |
| **`dnsmasq: unknown interface` でコンテナ停止** | USBパススルーによりNIC名が `enp0s8` から `enx...` に変化した | `ip link` で確認した `enx<MACアドレス>` 名に `netplan` と `dnsmasq.conf` を書き換えて適用 |
| **`bootx64.efi` 後にGRUBメニューが出ずSSD起動** | ISO直下の `grubx64.efi` はローカルCD/USB専用 | `pool/main/g/grub2-signed/...` 内の `grubnetx64.efi.signed` を抽出して配置 |
| **`Unknown command` または autoinstall が起動しない** | GRUB設定のセミコロン `;` がコマンド区切りと誤認された | `ds=nocloud-net\;s=http://...` のようにバックスラッシュでエスケープ |

---

### 📚 自立型インフラ＆オンプレAI完全技術リファレンス
本記事が役に立った・面白かったと感じていただけましたら、ぜひGitHubリポジトリへの **Star (★)** や **[Qiita (@ojisantech)](https://qiita.com/ojisantech)** / **[X (@OjisanTechnical)](https://x.com/OjisanTechnical)** のフォローをお願いいたします！  
👉 **[GitHub リポジトリ: ojisantech/ojisan-arsenal](https://github.com/ojisantech/ojisan-arsenal)**

> 💡 **【検証環境・個人研究（PoC）に関する注記】**  
> 本記事は、筆者個人の自宅検証環境（ホームラボ／仮想環境）において、公開情報およびOSS（オープンソースソフトウェア）を用いて独自に構築・検証した個人研究（PoC）の記録です。特定の企業・団体の実環境や業務上の非公開情報とは一切関係ありません。
