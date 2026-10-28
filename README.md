# 🛠️ ojisan-arsenal（おじさんの武器庫）
> **全14層・200パターンの自立型インフラ＆オンプレミスAI完全技術リファレンス**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

> 💡 **【検証環境・個人研究（PoC）に関する注記】**  
> 本記事（および本リポジトリ内の全ドキュメント）は、筆者個人の自宅検証環境（ホームラボ／仮想環境）において、公開情報およびOSS（オープンソースソフトウェア）を用いて独自に構築・検証した個人研究（PoC）の記録です。特定の企業・団体の実環境や業務上の非公開情報とは一切関係ありません。

---

## ⚖️ ライセンス ＆ 🛡️ 免責事項 ＆ 📋 サポートポリシー

### ⚖️ ライセンス（License）
本リポジトリで提供されるドキュメント、アーキテクチャ図、およびコード抜粋・スニペットは **[MIT License](./LICENSE)** の下で公開されています。商用・非商用問わず自由にご利用・ご参照いただけますが、著作権表示および許諾表示の保持が必要です。

### 🛡️ 免責事項（Disclaimer）
1. **自宅検証環境（ホームラボ）における個人研究・公開情報ベースの明示**: 本リポジトリおよび関連技術記事（Qiita等）に掲載されているアーキテクチャ図、処理フロー、コード抜粋、設計情報、および検証結果は、すべて作成者個人の独立した自宅検証環境（ホームラボ／仮想環境）において、公開情報およびOSS（オープンソースソフトウェア）のみを用いて独自に構築・検証した個人研究（PoC）の記録です。特定の企業・所属組織・取引先の実環境や業務上の非公開情報とは一切関係ありません。
2. **PoC・概念実証・学習目的の限定**: 本リポジトリに掲載されているアーキテクチャ図、処理フロー、コード抜粋、設計情報、およびトラブルシューティング手順は、技術検証・概念実証（PoC）および学習・設計検討のための参考情報です。そのまま本番環境で即時稼働することを意図した完全な製品コード・完成品スクリプトではありません。
3. **コード抜粋・途中版コードの性質**: 本リポジトリのコードは、アーキテクチャやアルゴリズムの要点解説を目的とした部分的な抜粋やPoC（開発途上・概念実証）レベルのスニペットを含んでいます。完全な例外処理、網羅的な入力バリデーション、環境依存の安全対策等が省略されている場合があります。実環境へ適用・実装される際は、各組織のセキュリティ基準および運用ポリシーに基づき、ご自身の責任において十分な設計・実装・テストを行ってください。
4. **自己責任の原則**: 本リポジトリの掲載情報、図、処理フロー、コード抜粋等を参考にしたこと、あるいはこれらを元に作成・実行・運用されたプログラムによって生じたいかなるシステム障害、データ消失、業務中断、セキュリティインシデント、法的紛争等について、リポジトリ作成者および関係者は一切の責任を負いません。必ず隔離された検証環境で十分に動作検証と影響評価を行ってください。
5. **不正行為・無許可探査の禁止**: 本リポジトリに含まれるネットワーク探索、パケット解析、脆弱性診断、ペネトレーションテスト等のフローや解説は、防御および障害調査・運用自動化の技術的理解を目的としたものです。明示的な許可のない第三者ネットワークや機器に対するポートスキャンや探査は法（不正アクセス禁止法等）に触れる恐れがあります。必ず自己管理下の自宅ラボまたは正式な許可を得た検証環境でのみ実施してください。

### 📋 サポートポリシー（Support Policy）
* **Issue / Pull Request**: ドキュメントの誤記修正、アーキテクチャやフローの改善提案に関するPR・Issueは歓迎いたします。
* **個別サポートの非提供**: 無償での完成版スクリプト作成、個別環境構築支援、個社固有のトラブルシューティングやカスタマイズ依頼には対応しておりません。
* **有償相談・技術顧問**: 個社環境への導入支援、現場DXアーキテクチャ設計、セキュリティ監査、内製化支援等のご相談につきましては、別途お問い合わせください。

---

## 💡 本武器庫（ojisan-arsenal）の設計思想と提供価値
本リポジトリでは、ソースコードの完全公開による意図しない悪用や運用上の安全性を考慮し、完成品スクリプトの丸ごと公開は行いません。その代わりに、**システムアーキテクチャ図、処理フロー、中核ロジックのコード抜粋、および概念実証（PoC）用の設計スニペット**に絞って掲載しています。

> **「単なるコードのコピペではなく、アーキテクチャの骨格と泥臭いトラブルシューティングの文脈を残す」**  
> **「キラキラしたAIも好きですが最後に人を救うのは `SSH` と `grep` だと信じています」**

### ☕ 著者プロフィール（Author Profile）
コーヒーと黒い画面とファンレスミニPCを愛するインフラ＆セキュリティ好きのおじさん。キラキラしたAIも好きですが最後に人を救うのはSSHとgrepだと信じています。休日に自宅検証ラボで枯れた技術とLLM/OSSを組み合わせ「高額SaaSに頼らない自立型インフラ」を組む個人研究(PoC)を無償公開中。※全て自宅ラボでの個人研究であり特定の企業・実業務とは一切無関係です。

* 🛠️ **個人研究リファレンス集（おじさんの武器庫）**：https://github.com/ojisantech/ojisan-arsenal

---

本リポジトリは、一般的なIT運用課題（誤検知、手打ちパッチ、エクセル台帳、SaaS過剰課金）を、枯れた技術（Bash, SQLite, Linux, Docker）と最新の自立型AI（ローカルLLM）の組み合わせで解決する**「アーキテクチャ図・処理フロー・要点コード抜粋・トラブルシューティング・実務FAQ」**を自宅検証ラボ（ホームラボ）で体系化した**全200弾の自立型技術リファレンス集（おじさんの武器庫）**です。

各ドラフト記事のサマリーから一歩踏み込み、アーキテクチャ理解、耐障害性担保、トラブルシューティングを完結させるための個人研究・技術検証ドキュメントです。

> 💡 **【現在順次アップデート中】**  
> 本リポジトリの全200弾の詳細技術リファレンス（アーキテクチャ図、処理フロー、要点コード抜粋等）は、Qiita連載予定に合わせて現在順次整理・コミットを進めています。各テーマの設計思想や解説ドキュメントを順次拡充していきますので、ぜひ **Star (★)** を押してお待ちください！

---

## 📚 詳細技術リファレンス一覧（全200弾）
### 🛡️ シリーズ A：インフラ・IT資産管理・セキュリティ自動化
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第1弾** | [`QIITA_ARTICLE_DETAIL_1.md`](./QIITA_ARTICLE_DETAIL_1.md) | **手打ちパッチ誤検知ゼロ化編**<br/>なぜ脆弱性診断ツールは「手打ちパッチ」で誤検知を連発するのか？ BashとSQLiteで過剰アラートをゼロにする超軽量プローブを作った話【個人検証PoC】 | セキュリティ担当、情シス、運用保守SE | アーキテクチャ図・処理フロー<br/>SQLite, Bash (要点抜粋) |
| **第2弾** | [`QIITA_ARTICLE_DETAIL_2.md`](./QIITA_ARTICLE_DETAIL_2.md) | **エージェントレス遠隔パッチ適用編**<br/>「パッチを当てるためだけに1台ずつログインするな」常駐エージェントなし（WinRM/SSH）でリモートパッチ適用から台帳更新まで完結させる設計と自宅ラボ検証PoC | インフラSE、情シス自動化担当 | 処理フロー・コード抜粋<br/>WinRM, SSH (要点抜粋) |
| **第3弾** | [`QIITA_ARTICLE_DETAIL_3.md`](./QIITA_ARTICLE_DETAIL_3.md) | **IT資産の発見と管理（エージェントレス）編**<br/>「ExcelのIT資産台帳、最後に更新したの誰？」に終止符を打つ。エージェントレスで端末を自動発見してOSS資産台帳（Snipe-IT）に即時同期する自宅ラボ構築PoC | 1人情シス、SE、IT資産管理者 | Python (要点抜粋)<br/>Snipe-IT REST API |
| **第4弾** | [`QIITA_ARTICLE_DETAIL_4.md`](./QIITA_ARTICLE_DETAIL_4.md) | **ローカルLLM脆弱性発見・是正要約編**<br/>機密データをクラウドに出せない閉域LAN想定で、ローカルLLMにIT機器の脆弱性を発見させてみた（GPU不要・CPUオンプレ稼働の自宅ラボPoC） | AI活用検討SE、セキュリティ責任者 | `ollama` (`qwen2.5:1.5b`)<br/>FastAPI |
| **第5弾** | [`QIITA_ARTICLE_DETAIL_5.md`](./QIITA_ARTICLE_DETAIL_5.md) | **Bluetooth/BLE電波探査（空間シャドーIT）編**<br/>「LANもWi-Fiも繋いでないから安全」は大間違い。Bluetooth/BLE電波を探査して見えない空間シャドーITを可視化する自宅ラボ検証PoC | 物理セキュリティ、監査部門、IoT推進者 | Linux BlueZ (`bluetoothctl`)<br/>RSSI距離推定 |
| **第6弾** | [`QIITA_ARTICLE_DETAIL_6.md`](./QIITA_ARTICLE_DETAIL_6.md) | **100%実機トポロジー ＆ ワンクリック遠隔接続編**<br/>「仮想ゴミノードで画面が埋まる…」にサヨナラ。HTML5 Canvasで実機100%の7大分類トポロジーを描画し、ワンクリックでRDP/SSH接続するハブを作った話【個人検証PoC】 | インフラエンジニア、運用監視担当 | HTML5 Canvas<br/>.rdp動的生成, TCP Socket |
| **第7弾** | [`QIITA_ARTICLE_DETAIL_7.md`](./QIITA_ARTICLE_DETAIL_7.md) | **OSSライセンス監査・GPL汚染回避編**<br/>自作ツールを商用化しようとしたら「python-nmap (GPL-3.0)」でコード全公開の危機に。GPL汚染を根絶してクリーンな構成に仕上げた個人検証記録 | 個人開発者、スタートアップ、技術法務 | `subprocess` + `ElementTree`<br/>AGPL/LGPL隔離 |
| **第8弾** | [`QIITA_ARTICLE_DETAIL_8.md`](./QIITA_ARTICLE_DETAIL_8.md) | **エージェントレス思想 ＆ マスターキー防衛編**<br/>「全LAN内PC端末に常駐エージェントを入れる」は本当に安全か？ CrowdStrike障害以降に再考するエージェントレス型資産管理のメリデメとマスターキー防衛 | セキュリティアーキテクト、CIO、情シス責任者 | WinRM, SSH公開鍵認証<br/>認証付き暗号（Fernet / AES-256-GCM） |
| **第9弾** | [`QIITA_ARTICLE_DETAIL_9.md`](./QIITA_ARTICLE_DETAIL_9.md) | **Windows 11怪奇現象 ＆ WinRM現場トラブル編**<br/>Windows 11 なのに「Win32_OperatingSystem」が Windows 10 と返してくる怪奇現象。自宅ラボでWinRMエージェントレス管理を実装してハマった5つの罠と解決策 | Windowsインフラ管理者、ヘルプデスクSE | PowerShell, WMI BuildNumber<br/>UACリモート制限解除 |
| **第10弾** | [`QIITA_ARTICLE_DETAIL_10.md`](./QIITA_ARTICLE_DETAIL_10.md) | **20系統脆弱性フィード ＆ ローカルキャッシュ編**<br/>NVDのAPI上限・遅延に泣かない。CISA KEV・EPSS・国内JVN・OSベンダーOVALなど「20系統の脆弱性フィード」をローカルで超高速突合する設計 | セキュリティエンジニア、SOC、診断士 | CISA KEV, FIRST EPSS<br/>OVAL, SQLiteキャッシュ |
| **第11弾** | `QIITA_ARTICLE_DETAIL_11.md` *(順次公開)* | **Intel N100ミニPC 自立型アプライアンス編**<br/>原価3万円のIntel N100ミニPCで「LANに挿すだけで自立稼働する資産管理アプライアンス（PoC）」を自宅ラボで作ってみた（TDP 10W・ファンレス・2.5GbE Dual） | ホームラボ愛好家、自作派、ハードウェアSE | Intel N100, Ubuntu 24.04<br/>USBクローニング, Docker |

---

### 🐟 シリーズ B：現場DX・オンプレミスAI・エッジ運用
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第12弾** | [`QIITA_ARTICLE_DETAIL_12.md`](./QIITA_ARTICLE_DETAIL_12.md) | **複合機スキャン ➔ Samba ➔ Dify自動RAG登録編**<br/>「現場にWeb画面からPDFをアップロードさせようとするな」スキャンPDFを共有フォルダに放り込むだけでDifyに自動RAG登録されるPython監視パイプライン構築PoC | DX推進担当、情シス、LAN内RAG導入者 | Python `watchdog`<br/>Samba (SMB), Dify Dataset API |
| **第13弾** | [`QIITA_ARTICLE_DETAIL_13.md`](./QIITA_ARTICLE_DETAIL_13.md) | **水濡れ現場向け Web Speech API × Dify音声UI編**<br/>手が濡れてても手袋しててもOK。水濡れ現場想定で「声で質問して声で答える」Dify音声対話UIをWeb Speech APIだけで作った話（個人検証PoC） | フロントエンド開発者、工場・現場DX担当 | Web Speech API<br/>Vanilla JS, Dify Chat API |
| **第14弾** | `QIITA_ARTICLE_DETAIL_14.md` *(順次公開)* | **自作AI基盤CPU爆死 ➔ Dify分離アーキテクチャ編**<br/>自作AI基盤（FastAPI + Whisper + Voicevox + Qdrant）がCPU 100%スパイクで爆死した話。自宅ラボ検証で安定稼働した「Difyバックエンド ＋ Nginx軽量UI」分離アーキテクチャの結論 | AIエンジニア、インフラエンジニア | Dify オフロード<br/>Nginx, Docker Compose |
| **第15弾** | `QIITA_ARTICLE_DETAIL_15.md` *(順次公開)* | **Tailscaleによる100台エッジAI無料保守編**<br/>ルーターのポート開放も固定IPも不要。100拠点のオンプレエッジAIサーバーをTailscale（ZTNA）で安全にリモート保守する設計と無料枠活用法 | IoT/エッジエンジニア、MSP、フィールドSE | Tailscale (WireGuard / ZTNA)<br/>DERP, Tailscale SSH |
| **第16弾** | `QIITA_ARTICLE_DETAIL_16.md` *(順次公開)* | **カメラ × Vision LLM による現物伝票の構造化編**<br/>紙の現物伝票をスマホで撮るだけ。Vision LLMで仕入れ品目・数量を瞬時にJSON構造化するプロンプトと現場BPMN設計 | アナログ現場DX、物流・市場担当SE | Vision LLM (マルチモーダル)<br/>Base64, JSON Schema |
| **第17弾** | `QIITA_ARTICLE_DETAIL_17.md` *(順次公開)* | **職人の暗黙知・ボイスナレッジ化編**<br/>「あのベテランにしか分からない」をなくす。現場でボソッと呟いたノウハウ音声をAIが自動で構造化・ベクトル蓄積する業務フロー | 業務継承・ナレッジマネジメント | 音声認識 (STT)<br/>LLM正規化, VectorDB (RAG) |

---

### 📡 シリーズ C：ネットワーク深層探索・シャドーIT検知
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第18弾** | `QIITA_ARTICLE_DETAIL_18.md` *(順次公開)* | **ゼロコンフィグ機器探索（mDNS / SSDP）編**<br/>IPアドレスが分からなくても見つけ出せる。mDNSとSSDPでLAN内のスマート家電・プリンタ・Macを一網打尽にするPython探索術【自宅ラボ検証】 | ネットワークエンジニア、情シス | mDNS (Bonjour / 5353)<br/>SSDP (UPnP / 1900), zeroconf |
| **第19弾** | [`QIITA_ARTICLE_DETAIL_19.md`](./QIITA_ARTICLE_DETAIL_19.md) | **モバイル・私用スマホの受動特定編**<br/>スマホ（iPhone/Android）のWi-Fi接続をどう見分けるか？ 受信パケットからOSを判別するエージェントレス判定ロジック【自宅ラボ検証PoC】 | セキュリティ担当、ネットワーク管理者 | 初期TTL (64/128)<br/>User-Agent, DHCP Option 55 |
| **第20弾** | `QIITA_ARTICLE_DETAIL_20.md` *(順次公開)* | **未知端末の即時アラート（超軽量通知）編**<br/>見知らぬMACアドレスが現れた瞬間、1秒で画面に警報を飛ばす。SQLite×ポーリングで作る超軽量リアルタイム検知パイプライン | フルスタックエンジニア、情シス | SQLite `notifications`<br/>MAC正規化, ショートポーリング |

---

### 🤖 シリーズ D：AI品質管理・ガードレール・CPU最適化
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第21弾** | `QIITA_ARTICLE_DETAIL_21.md` *(順次公開)* | **LLMハルシネーション自動テスト（CI/CD）編**<br/>LAN内AIボットの「嘘（ハルシネーション）」を許さない。CI/CDで回す事実整合性ベンチマークテスト自動化スイート（TC01〜TC10） | QAエンジニア、プロンプト開発者 | Python (`pytest`)<br/>Keyword Match, CI/CD |
| **第22弾** | `QIITA_ARTICLE_DETAIL_22.md` *(順次公開)* | **決定論的Guardrail（検閲・安全機構）編**<br/>LAN内機密や不適切発言をLLMに喋らせない。プロンプトインジェクションを防ぐ「決定論的Guardrailバリデーター」の実装 | AIセキュリティ、コンプライアンス担当 | 正規表現パターンマッチ<br/>入出力インターセプター |
| **第23弾** | `QIITA_ARTICLE_DETAIL_23.md` *(順次公開)* | **CPU環境でのローカルLLM最適化編**<br/>GPUなしの普通のCPUサーバーで「Qwen2.5-1.5B」をサクサク動かす。Ollamaと量子化モデルのメモリチューニングと高速化設定 | オンプレミスAI導入担当、エッジ開発者 | Ollama, Qwen2.5:1.5b (Q4)<br/>Modelfile, CPU制限 |

---

### 🖥️ シリーズ E：現場UI・マルチOS運用・システム堅牢化
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第24弾** | `QIITA_ARTICLE_DETAIL_24.md` *(順次公開)* | **Excelライクなテーブル操作（Vanilla JS）編**<br/>「Excelの操作感じゃないと嫌だ」と言われたWeb画面。HTML Tableで列幅ドラッグ伸縮（最小10px）とリアルタイムPing疎通を自作した話 | Webフロントエンド開発者、SE | Pure JavaScript (Vanilla)<br/>CSS Table Layout, TCP Socket |
| **第25弾** | `QIITA_ARTICLE_DETAIL_25.md` *(順次公開)* | **ソフトウェア資産管理（SAM）と野良アプリ発見編**<br/>野良アプリの勝手インストールをあぶり出す。WindowsとLinuxからインストール済み全アプリをエージェントレス抽出し台帳化するスクリプト | SAM管理者、情シス、セキュリティ担当 | PowerShell (Uninstallキー)<br/>SSH (dpkg / rpm) |
| **第26弾** | `QIITA_ARTICLE_DETAIL_26.md` *(順次公開)* | **Linux & macOS の遠隔サイレントパッチ編**<br/>Windowsだけじゃない。Ubuntuの「apt-get」とmacOSの「softwareupdate」をSSH越しに安全にリモート適用・結果回収する自動化 | Linux/Macインフラ管理者 | Paramiko (SSH), `apt-get`<br/>`softwareupdate`, 再起動検知 |
| **第27弾** | `QIITA_ARTICLE_DETAIL_27.md` *(順次公開)* | **AI不在時フェイルソフト設計編**<br/>重たいLLMコンテナが突然落ちてもシステムを止めない。AI不在時に決定論的ルールエンジンへ瞬時にフォールバックする耐障害性設計 | システムアーキテクト、SRE | 決定論的辞書ルール<br/>ヘルスチェック, 自動フォールバック |
| **第28弾** | `QIITA_ARTICLE_DETAIL_28.md` *(順次公開)* | **Docker Composeの物理分割とオーバーライド編**<br/>「AI機能付き」と「AIなしBase版」をどう作り分けるか？ Docker Composeの物理分割とオーバーライド設計で保守コストを半減させた話 | Docker運用者、インフラ設計者 | `docker-compose.base.yaml`<br/>`docker-compose.llm.yaml`, `-f` |
| **第29弾** | `QIITA_ARTICLE_DETAIL_29.md` *(順次公開)* | **VSCode Remote-SSH 快適リモート開発環境編**<br/>低スペックな手元PCからオンプレDocker環境へ。VSCode Remote-SSHで快適にマルチコンテナをフルスタック開発する環境構築術 | 全エンジニア、リモートワーカー | VSCode Remote - SSH<br/>ポート自動フォワード, Dev Containers |

---

### 🛠️ シリーズ G：インフラ現場トラブル・泥臭い深層トラブルシュート編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第31弾** | `QIITA_ARTICLE_DETAIL_31.md` *(順次公開)* | **DNSキャッシュの罠とFlush自動化編**<br/>DNSキャッシュの罠。TTLが切れているのに名前解決が変わらないLinux/Windowsの闇とFlush自動化 | インフラエンジニア、情シス、Webマスター | `resolvectl flush-caches`<br/>`Clear-DnsClientCache`, Chrome |
| **第32弾** | `QIITA_ARTICLE_DETAIL_32.md` *(順次公開)* | **MTU/MSS不整合によるパケット消失編**<br/>MTU/MSS不整合によるパケット消失。Pingは通るのにWebやSSHが開かない怪奇現象の調査手順 | ネットワークエンジニア、VPN運用者 | DFビットPing, TCP MSS Clamping<br/>`iptables`, `netsh` |
| **第33弾** | `QIITA_ARTICLE_DETAIL_33.md` *(順次公開)* | **ディスク容量100%と「df vs du」問題編**<br/>ディスク容量100%の真犯人。消したはずのログをプロセスが掴み続けて容量が減らない「df vs du」問題 | SRE、Linux運用保守担当 | `lsof +L1`, `/proc/<PID>/fd`<br/>`truncate -s 0` |
| **第34弾** | `QIITA_ARTICLE_DETAIL_34.md` *(順次公開)* | **NTP時刻ズレと認証死防衛編**<br/>NTP時刻ズレが引き起こす認証死。KerberosやSSLが全滅する前に仕込むchrony設定と監視 | インフラ設計者、Active Directory管理者 | `chrony` (`makestep`), RTC<br/>時刻オフセット監視スクリプト |
| **第35弾** | `QIITA_ARTICLE_DETAIL_35.md` *(順次公開)* | **ルーティングループとARPストーム復旧編**<br/>ルーティングループとARPストーム。LANケーブルのタコ足配線でネットワークが死ぬメカニズムと復旧・防止設計【検証解説】 | SE、ネットワーク保守担当 | L2ループ, ブロードキャストストーム<br/>Loop Guard, STP, BPDU Guard |
| **第36弾** | `QIITA_ARTICLE_DETAIL_36.md` *(順次公開)* | **ゾンビプロセス大量発生と正しい掃除法編**<br/>ゾンビプロセス大量発生。親プロセスが死んでinit/systemdに養子入りしたプロセスの正しい掃除法 | Linuxシステムエンジニア、アプリ開発者 | `[defunct]`, PID枯渇<br/>PPID特定, `systemd` (PID 1) 供養 |
| **第37弾** | `QIITA_ARTICLE_DETAIL_37.md` *(順次公開)* | **Linuxカーネルパニック防止とOOM Killer調律編**<br/>Linuxカーネルパニックを防ぐ。OOM Killerの優先度調整（oom_score_adj）とスワップ調律で重要サービスを死守する設計 | インフラエンジニア、DBA、SRE | `oom_score_adj` (-1000/1000)<br/>`vm.swappiness=10`, Docker Compose |
| **第38弾** | `QIITA_ARTICLE_DETAIL_38.md` *(順次公開)* | **ステートフルFWの罠と非対称ルーティング解消編**<br/>ファイアウォールのステートフルインスペクションの罠。非対称ルーティングで戻りパケットが消える問題の解決手順 | ネットワーク設計者、セキュリティ担当 | 非対称ルーティング, RPF (`rp_filter`)<br/>ポリシーベースルーティング (`ip rule`) |
| **第39弾** | `QIITA_ARTICLE_DETAIL_39.md` *(順次公開)* | **logrotateの落とし穴とHUPシグナル編**<br/>logrotateの落とし穴。HUPシグナル送り忘れでログファイルが肥大化し続ける事故の防衛 | インフラエンジニア、運用自動化担当 | `postrotate` (`kill -HUP`), `delaycompress`<br/>`copytruncate` (自作アプリ救済) |
| **第40弾** | `QIITA_ARTICLE_DETAIL_40.md` *(順次公開)* | **SSL/TLS証明書更新忘れ防止と外形監視編**<br/>SSL/TLS証明書更新忘れの時限爆弾。Let's Encrypt自動更新スクリプトと更新失敗アラートの鉄壁設計 | Webマスター、セキュリティ担当、情シス | Certbot `--deploy-hook`, OpenSSL<br/>30日前Slack通知スクリプト |

---

### 🖥️ シリーズ H：ハードウェア・ホワイトボックス・BMC/オンプレ深層編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第41弾** | `QIITA_ARTICLE_DETAIL_41.md` *(順次公開)* | **ファンレスPCの熱設計とサーマル対策編**<br/>手のひらファンレスPCを24時間サーバーにする熱設計とサーマルスロットリング対策 | 自宅サーバー愛好家、エッジ開発者 | 縦置き自然対流, 5V静音ファン<br/>`intel-rapl` TDP制限, 温度監視 |
| **第42弾** | `QIITA_ARTICLE_DETAIL_42.md` *(順次公開)* | **IPMI/BMCリモート電源制御と自動復旧編**<br/>IPMI / BMC を使ったリモート電源制御。OSがハングしてもWebから物理リセットする技術 | データセンター保守、インフラ運用SE | `ipmitool` (RMCP+), Serial-over-LAN<br/>Python死活監視自動物理リセット |
| **第43弾** | `QIITA_ARTICLE_DETAIL_43.md` *(順次公開)* | **SSD寿命監視とsmartctl自動警告編**<br/>SSDの突然死を防ぐ。smartctlでNVMe/SATAの残り寿命とTBWを自動監視・通知するスクリプト | ストレージ管理者、SRE | `smartctl` (JSON), Percentage Used<br/>TBW換算, Slack通知スクリプト |
| **第44弾** | `QIITA_ARTICLE_DETAIL_44.md` *(順次公開)* | **PXEネットワークブート無人インストール編**<br/>PXEネットワークブート環境構築。USBメモリ不要、LAN経由でOSを一発自動インストールする技術 | キッティング担当、情シス、製造SE | ProxyDHCP (`dnsmasq`), iPXE<br/>Ubuntu `autoinstall` (cloud-init) |
| **第45弾** | `QIITA_ARTICLE_DETAIL_45.md` *(順次公開)* | **2.5GbEデュアルLANのLACPボンディング編**<br/>2.5GbEデュアルLANのチーミング。LACPボンディングで帯域倍増（5Gbps）と冗長化を両立するnetplan設定 | ネットワークエンジニア、サーバー管理者 | IEEE 802.3ad (Mode 4), `netplan`<br/>無瞬断フェイルオーバー, LACP |
| **第46弾** | `QIITA_ARTICLE_DETAIL_46.md` *(順次公開)* | **UPS・NUT連動安全シャットダウン編**<br/>UPS（無停電電源装置）とNUT連動。停電時に複数台のLinux/Windowsを安全自動シャットダウンする設計 | ファシリティSE、インフラ運用担当 | NUT (`upsd` / `upsmon`), USB HID<br/>WinNUT-Client, 停電ブロードキャスト |
| **第47弾** | `QIITA_ARTICLE_DETAIL_47.md` *(順次公開)* | **Wake-on-LAN深夜一斉起動とエコ運用編**<br/>Wake-on-LAN（WoL）による深夜一斉起動。パッチ適用後に自動電源OFFする「電気代ゼロ」メンテナンス術 | 情シス、SE、運用自動化担当 | Magic Packet (UDP 9), Python<br/>高速スタートアップ無効化, WinRM |
| **第48弾** | `QIITA_ARTICLE_DETAIL_48.md` *(順次公開)* | **ファンレスPCのCPU TDP手動調律編**<br/>ファンレスPCのクロックダウンを防ぐ。Linux上からのCPU TDP（電力枠）手動調律で「低発熱・高持続」を実現する技 | ハードウェアSE、Linuxカーネル調律 | PL1/PL2手動キャップ (`8W`)<br/>`cpupower` schedutil, systemd |
| **第49弾** | `QIITA_ARTICLE_DETAIL_49.md` *(順次公開)* | **型落ちサーバーの延命術とNVMe PCIe化編**<br/>型落ちサーバーの延命術。メモリ増設とNVMe PCIe変換アダプタで爆速ストレージ化する現場技 | 低予算インフラSE、自作サーバー派 | PCIe to M.2変換, Clover EFI<br/>/boot分離ブートチェーン, 3500MB/s |
| **第50弾** | `QIITA_ARTICLE_DETAIL_50.md` *(順次公開)* | **ホワイトボックス量産と自動命名の極意編**<br/>ホワイトボックスサーバー量産の極意。Clonezilla自動化とMACアドレス別ホスト名自動命名で1日100台出荷する技術 | ハードウェア製品開発、製造キッティング | Clonezilla非対話バッチ, 一般化<br/>MACアドレス下位6桁動的命名, SSH再生成 |

---

### 🌐 シリーズ I：ネットワーク監視・プロトコル深掘り・ゼロ円インフラ編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第51弾** | `QIITA_ARTICLE_DETAIL_51.md` *(順次公開)* | **SNMP v2c/v3 スイッチポート帯域監視編**<br/>Zabbix不要！PythonだけでLAN内スイッチの全ポート帯域・パケットエラーをSNMP監視して異常時にWebhook通知する軽量スクリプト | ネットワーク運用者、SE | pysnmp, SNMP v2c/v3, 64bitカウンタ<br/>ポートエラー検知, Webhook通知 |
| **第52弾** | `QIITA_ARTICLE_DETAIL_52.md` *(順次公開)* | **NetFlow v5 トラフィック解析・通信内訳可視化編**<br/>誰がLAN内の帯域を食い潰しているのか？NetFlow/IPFIXをPythonで受信して「犯人端末」と宛先を暴く軽量コレクター自作 | ネットワークSE、情シス | NetFlow v5, UDP 2055, Python raw socket<br/>Top Talkers集計, 帯域圧迫特定 |
| **第53弾** | `QIITA_ARTICLE_DETAIL_53.md` *(順次公開)* | **rsyslog × SQLite 軽量中央ログ収集基盤編**<br/>ELKスタックは重すぎる！rsyslogとSQLiteで作る「メモリ50MB」のネットワーク機器ログ集約＆全文検索基盤 | 低予算インフラSE、中小情シス | rsyslog (`ompgsql` / テンプレート), SQLite3<br/>Syslog UDP 514, WALモード, FTS5 |
| **第54弾** | `QIITA_ARTICLE_DETAIL_54.md` *(順次公開)* | **TCP SYN-ACK RTT ジッター計測編**<br/>Pingだけでは見抜けない！TCP SYN-ACK往復時間（RTT）で拠点間VPNの「本当の品質」とジッターを常時ロギングする | VPN運用担当、クラウドインフラSE | TCP Handshake RTT, Python socket<br/>ジッター・分散計算, 外形品質監視 |
| **第55弾** | `QIITA_ARTICLE_DETAIL_55.md` *(順次公開)* | **Wi-Fi 2.4G/5G 電波干渉調査編**<br/>LAN内のWi-Fiが遅い原因を突き止める！Linuxのiw/wavemonで近隣APの電波干渉・チャンネル重複を可視化する調査術 | LAN内環境管理者、情シス | `iw dev scan`, 2.4GHz/5GHz チャンネル設計<br/>Beacon RSSI解析, ステルスSSID |
| **第56弾** | `QIITA_ARTICLE_DETAIL_56.md` *(順次公開)* | **ARPポイズニング（なりすまし）監視編**<br/>LAN内に忍び寄るMITM攻撃を許さない！Pythonで作る軽量ARPポイズニング（なりすまし）監視ツール | セキュリティ担当、ネットワークSE | `/proc/net/arp`, IP-MAC整合性監視<br/>MITM検知, 静的ARP固定化防衛 |
| **第57弾** | `QIITA_ARTICLE_DETAIL_57.md` *(順次公開)* | **野良IPv6の危険性と無効化・ステルス検知編**<br/>LAN内で密かに動く「野良IPv6」が情シスの死角になる理由と、Linux/ルーターでの確実な無効化・ステルス検知法 | 情シス、インフラ設計者 | SLAAC攻撃, 偽RA (Router Advertisement)<br/>ICMPv6 Type 134 Raw Socket, sysctl |
| **第58弾** | `QIITA_ARTICLE_DETAIL_58.md` *(順次公開)* | **ポートミラーリング（SPAN）パケット常時キャプチャ編**<br/>スイッチのポートミラーリング（SPAN）とLinuxで作る！月額0円の常時パケットキャプチャ＆ローテーション監視基盤 | トラブルシューター、SRE | SPANポート, プロミスキャスモード<br/>`tcpdump` リングバッファ (`-C -W`), Wireshark |
| **第59弾** | `QIITA_ARTICLE_DETAIL_59.md` *(順次公開)* | **CoreDNS 悪意ドメイン一括ブロック・シンクホール編**<br/>LAN内DNSをCoreDNS/dnsmasqで防御壁に！悪意あるドメイン・広告・C2サーバーを一括ブロックするRPZ/シンクホール構築 | セキュリティSE、DNS管理者 | CoreDNS (`hosts` プラグイン), Docker<br/>DNSシンクホール (0.0.0.0), C2遮断 |
| **第60弾** | `QIITA_ARTICLE_DETAIL_60.md` *(順次公開)* | **ネットワーク機器Configバックアップ自動化編**<br/>ルーター・L2/L3スイッチのConfigバックアップを「全自動」にする！ParamikoとGitで作るゼロ円Config管理基盤 | ネットワーク運用担当、インフラ自動化 | Paramiko (SSH), `show running-config`<br/>Git自動コミット・差分追跡, マスキング |

---

### 🤖 シリーズ J：現場DX・Dify/RAG・Vision/音声応用・BPMN編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第61弾** | `QIITA_ARTICLE_DETAIL_61.md` *(順次公開)* | **非構造化日報の構造化JSON抽出編**<br/>現場の非構造化「日報・作業報告書」をDifyワークフローで瞬時に構造化JSON・要約抽出する設計 | 情シス、業務DX推進者、SE | Dify ワークフロー, LLM JSON Mode<br/>Code Node (Python), スキーマ検証 |
| **第62弾** | `QIITA_ARTICLE_DETAIL_62.md` *(順次公開)* | **複数マニュアル横断RAGのチャンキング設計編**<br/>「PDFが多すぎて見つからない」を解決する！LAN内複数業務マニュアル横断RAGのチャンキング・メタデータ設計 | AIエンジニア、RAG設計者 | 見出し階層チャンカー, メタデータ注入<br/>ハイブリッド検索 (BM25 + Dense) |
| **第63弾** | `QIITA_ARTICLE_DETAIL_63.md` *(順次公開)* | **Visionモデルによる外観検査・不良判定PoC編**<br/>Visionモデル（LLaVA / GPT-4o-mini）で現場の「外観検査・不良品判定」を自動化する低コストPoC | 製造現場SE、品質管理、エッジAI | OpenCV, Vision API, Few-Shot画像比較<br/>USBカメラ, 欠陥・ネジ抜け検知 |
| **第64弾** | `QIITA_ARTICLE_DETAIL_64.md` *(順次公開)* | **LINE WORKS/Teams × Dify自動一次受け編**<br/>LINE WORKS / Teams Webhook × DifyでLAN内ヘルプデスク問い合わせを自動一次受けする構築手順 | 情シス、SE、コーポレートIT | Teams/LINE Webhook, FastAPI中継<br/>Dify Chat API, LAN内FAQ自動応答 |
| **第65弾** | `QIITA_ARTICLE_DETAIL_65.md` *(順次公開)* | **スマホカメラバーコード読み取り＆DB突合編**<br/>スマホカメラの写真からバーコード・QRコードを読み取り商品マスタDBと突合する軽量エッジWebアプリ | 物流・倉庫DX、店舗SE | HTML5 getUserMedia, ZXing-js<br/>FastAPI, SQLiteマスタ即時照合 |
| **第66弾** | `QIITA_ARTICLE_DETAIL_66.md` *(順次公開)* | **ローカルWhisper音声ハンズフリー棚卸し編**<br/>音声入力（Whisper）で倉庫・工場の「ハンズフリー在庫棚卸し」を実現するローカルPythonパイプライン | 倉庫・製造業SE、現場作業員 | faster-whisper, Silero VAD, initial_prompt<br/>完全オフラインSTT, 音声在庫パース |
| **第67弾** | `QIITA_ARTICLE_DETAIL_67.md` *(順次公開)* | **帳票の受領印・チェック漏れ自動検知編**<br/>帳票・伝票の「手書き受領印・チェック漏れ」をOpenCVとVision APIで自動検知・仕分けする技術 | バックLAN内DX、経理・総務SE | OpenCV HSV色空間 (朱色抽出)<br/>捺印枠クロップ, 0.01秒高速仕分け |
| **第68弾** | `QIITA_ARTICLE_DETAIL_68.md` *(順次公開)* | **Difyセルフホスト自動日次ダンプ・リカバリ編**<br/>Difyセルフホスト運用の要！PostgreSQL / Vector DBの自動日次ダンプと無瞬断リカバリ検証 | Dify運用者、インフラエンジニア、SRE | pg_dump (-F c), Qdrant Snapshot API<br/>ストレージtar.gz, 世代管理cron |
| **第69弾** | `QIITA_ARTICLE_DETAIL_69.md` *(順次公開)* | **完全オフライン埋め込み基盤 (bge-m3 × ChromaDB)編**<br/>外部持ち出し厳禁データのための完全オフライン・ローカルEmbedding基盤（bge-m3 × ChromaDB） | セキュリティ重視企業、AI基盤SE | BAAI/bge-m3 (8192トークン長)<br/>ChromaDB, エアギャップ環境RAG |
| **第70弾** | `QIITA_ARTICLE_DETAIL_70.md` *(順次公開)* | **朝礼安全注意事項・ヒヤリハット自動配信編**<br/>朝礼の「今日のヒヤリハット・安全衛生注意事項」を過去事例DBから毎日自動生成するリマインダーボット | 労働安全管理者、現場リーダー | SQLite過去事故事例, 季節・天候連動<br/>1分間スピーチ生成, Teams/Slack配信 |

---

### 🛡️ シリーズ K：セキュリティ監査・権限統制・コンプライアンス編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第71弾** | `QIITA_ARTICLE_DETAIL_71.md` *(順次公開)* | **Active Directory休眠アカウント監査編**<br/>Active Directoryの「退職者・休眠アカウント」をPython LDAPで一括あぶり出し無効化する監査術 | AD管理者、情シス、セキュリティ監査 | `ldap3`, LDAPS, `lastLogonTimestamp`<br/>90日休眠判定, CSV自動出力, 無効化 |
| **第72弾** | `QIITA_ARTICLE_DETAIL_72.md` *(順次公開)* | **共有フォルダ・Git平文クレデンシャル監査編**<br/>LAN内ファイルサーバー／Gitリポジトリから平文パスワードや秘密鍵を血眼で洗い出すTruffleHog/自作Grep | セキュリティSE、DevSecOps | シャノン・エントロピー解析, 正規表現<br/>RSA秘密鍵, APIトークン即時検知 |
| **第73弾** | `QIITA_ARTICLE_DETAIL_73.md` *(順次公開)* | **共有フォルダ過剰権限 (Everyone) 撲滅編**<br/>Windows共有フォルダ（Samba/SMB）の「Everyoneフルコントロール」過剰権限を撲滅するPowerShell/Python監査 | Windows Server管理者、情シス | PowerShell `Get-Acl`, NTFSアクセス権<br/>Everyone/Users過剰権限検出, `icacls` |
| **第74弾** | `QIITA_ARTICLE_DETAIL_74.md` *(順次公開)* | **USBメモリ接続履歴フォレンジック調査編**<br/>USBメモリ接続履歴をWindowsイベントログ（Event ID 2003/24577等）から抽出して不正持ち出しを追跡する | フォレンジック担当、情シス、監査室 | レジストリ `USBSTOR`, Event ID 2003/2100<br/>シリアル番号特定, タイムライン復元 |
| **第75弾** | `QIITA_ARTICLE_DETAIL_75.md` *(順次公開)* | **プロキシログ統計解析・深夜データ流出検知編**<br/>プロキシ・SquidログをPythonで解析して「新設怪しいドメイン」「深夜の大量データ送信」を検知する | ネットワーク監視、セキュリティ担当 | Squid `access.log`, 深夜大容量POST<br/>DGAランダムドメインエントロピー検知 |
| **第76弾** | `QIITA_ARTICLE_DETAIL_76.md` *(順次公開)* | **sudoers設定不備とGTFOBins昇格監査編**<br/>Linuxの `sudoers` 設定不備による権限昇格の罠！情シスがチェックすべきNOPASSWDとワイルドカード監査 | Linux管理者、セキュリティエンジニア | GTFOBins (`vim`, `less`, `find` 昇格)<br/>`NOPASSWD: ALL` 検知, `sudoedit` |
| **第77弾** | `QIITA_ARTICLE_DETAIL_77.md` *(順次公開)* | **PAMパスワード複雑性強制＆ロックアウト編**<br/>PAM設定で仕留める！Linuxサーバーのパスワード複雑性強制（pam_pwquality）とアカウントロックアウト（pam_faillock） | インフラセキュリティ、Linux保守SE | `pam_pwquality` (12文字+4種文字)<br/>`pam_faillock` (5回連続失敗15分凍結) |
| **第78弾** | `QIITA_ARTICLE_DETAIL_78.md` *(順次公開)* | **ポートノッキング (knockd) ステルスSSH編**<br/>開けっ放しSSHポートを撲滅！ポートノッキング（knockd）でステルス管理インターフェースを作る | サーバー管理者、エッジ運用者 | `knockd`, iptables動的ルール挿入<br/>合言葉ポートノック, 30秒自動再閉鎖 |
| **第79弾** | `QIITA_ARTICLE_DETAIL_79.md` *(順次公開)* | **SSH Google Authenticator 二要素認証 (TOTP)編**<br/>LAN内LinuxサーバーへのSSHログインにGoogle Authenticator二要素認証（2FA/TOTP）を義務化する | Linuxセキュリティ管理者、SRE | `libpam-google-authenticator`, TOTP<br/>公開鍵＋6桁ワンタイムパスワード義務化 |
| **第80弾** | `QIITA_ARTICLE_DETAIL_80.md` *(順次公開)* | **Python ReportLab 美麗監査PDF自動生成編**<br/>月次の「LAN内セキュリティ監査レポート」をPython ReportLabで自動PDF生成して経営層にドヤ顔提出する技術 | 情シスリーダー、セキュリティ責任者 | ReportLab Platypus, 日本語フォント<br/>エグゼクティブサマリ表, 月次cron自動化 |

---

### ⚡ シリーズ L：開発効率化・GitOps・Dockerコンテナ極限運用編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第81弾** | `QIITA_ARTICLE_DETAIL_81.md` *(順次公開)* | **Watchtowerコンテナ自動更新の安全設計編**<br/>Watchtowerによるコンテナ自動更新の光と影！本番事故を防ぐ通知・除外ラベル設定 | 自宅サーバー派、Docker運用者 | Watchtower, Label filter (`enable=false`)<br/>Shoutrrr Webhook通知, 自動クリーンアップ |
| **第82弾** | `QIITA_ARTICLE_DETAIL_82.md` *(順次公開)* | **Multi-stage build Docker極限軽量化編**<br/>Dockerfile Multi-stage build極限軽量化！1GB超のPython/Nodeイメージを50MB以下に絞り込むテクニック | Web開発者、コンテナ基盤エンジニア | Multi-stage build, Python-slim/alpine<br/>仮想環境コピー, 95%サイズ削減, 非root化 |
| **第83弾** | `QIITA_ARTICLE_DETAIL_83.md` *(順次公開)* | **LAN内閉域網プライベートDocker Registry編**<br/>LAN内閉域網に立てるプライベートDocker Registry（distribution/registry）とTLS自己署名証明書の配布術 | 閉域網インフラSE、製造業IT | Docker公式 `registry:2`, htpasswd<br/>SAN付き自己署名証明書, `/etc/docker/certs.d` |
| **第84弾** | `QIITA_ARTICLE_DETAIL_84.md` *(順次公開)* | **Docker HEALTHCHECK＆autoheal自律再起動編**<br/>コンテナの「死活監視」をDocker compose HEALTHCHECKだけで完結させる！ゾンビコンテナの自律再起動設計 | SRE、システム保守エンジニア | Docker `HEALTHCHECK`, `autoheal`<br/>unhealthy自動再起動, デッドロック救済 |
| **第85弾** | `QIITA_ARTICLE_DETAIL_85.md` *(順次公開)* | **Docker Named Volume無停止バックアップ編**<br/>Docker Named Volumeのデータ消失を防ぐ！コンテナ停止なしで日次バックアップ・S3互換退避するシェルスクリプト | データベース管理者、インフラ運用担当 | 使い捨てAlpineコンテナ, `:ro` マウント<br/>`tar.gz` 圧縮, 世代管理, `-v` 事故防止 |
| **第86弾** | `QIITA_ARTICLE_DETAIL_86.md` *(順次公開)* | **GitHub Actionsインフラ自動Lint＆テスト編**<br/>GitHub Actionsによるインフラコード自動Lint＆単体テスト環境構築（ShellCheck, yamllint, pytest） | DevSecOps、インフラ自動化SE | GitHub Actions, ShellCheck, yamllint<br/>pytest, PRゲートキーパー自動検証 |
| **第87弾** | `QIITA_ARTICLE_DETAIL_87.md` *(順次公開)* | **オレオレスクリプト統一Makefileタスクランナー編**<br/>現場のオレオレスクリプトを「Makefile」で統一する！引数・ヘルプ・環境変数管理のベストプラクティス | チームリーダー、SE、全開発者 | GNU Make, 自己文書化 (`make help`)<br/>`.env` 自動インクルード, `.PHONY` |
| **第88弾** | `QIITA_ARTICLE_DETAIL_88.md` *(順次公開)* | **git-crypt環境変数 (.env) 透過暗号化編**<br/>git-cryptでLAN内機密・環境変数（.env）を透過的暗号化して安全にGit管理する運用術 | セキュリティSE、バックエンド開発者 | `git-crypt`, Git smudge/clean filter<br/>AES-256暗号化, `.gitattributes`, GPG |
| **第89弾** | `QIITA_ARTICLE_DETAIL_89.md` *(順次公開)* | **SQLite「database is locked」撲滅WALチューニング編**<br/>SQLiteの「データベースがロックされています（database is locked）」を撲滅するWALモードと並行書き込みチューニング | Python開発者、Webアプリエンジニア | `PRAGMA journal_mode = WAL`, `busy_timeout`<br/>並行書き込み競合解消, 64MBキャッシュ |
| **第90弾** | `QIITA_ARTICLE_DETAIL_90.md` *(順次公開)* | **FastAPIイベントループ凍結事故防衛編**<br/>FastAPI / asyncioで「うっかりブロッキング処理」を書いてサーバー全体が詰まる罠とThreadPoolExecutor救済策 | Pythonエンジニア、FastAPI開発者 | `async def` vs `def`, イベントループ<br/>`asyncio.to_thread`, スレッドプール退避 |

---

### 🚀 シリーズ M：エンジニア生存戦略・知財防衛・個人ビジネス編（完結編）
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術・戦略 |
| :---: | :--- | :--- | :--- | :--- |
| **第91弾** | `QIITA_ARTICLE_DETAIL_91.md` *(順次公開)* | **GitHub/Git設定・アカウント完全物理分離編**<br/>業務環境との混同・誤コミットを物理的に防ぐ！個人開発・技術発信のための「GitHub/Git設定・アカウント完全分離術」 | 副業エンジニア、OSS活動者 | `includeIf`, `~/.ssh/config` ホストエイリアス<br/>GPG署名分離, pre-commit業務ドメインブロック |
| **第92弾** | `QIITA_ARTICLE_DETAIL_92.md` *(順次公開)* | **J-PlatPat先行特許調査・侵害回避出願編**<br/>J-PlatPatで先行技術を完全調査！エンジニアが自作アイデアの特許侵害を避けて独自特許を出願する戦略 | 個人開発者、知財・起業志望者 | J-PlatPat無料調査, FI/Fターム<br/>クレーム構成要件充足論, 減免制度活用 |
| **第93弾** | `QIITA_ARTICLE_DETAIL_93.md` *(順次公開)* | **副業・兼業申請書設計と合意形成ロジック編**<br/>企業の副業・兼業申請をスムーズに通すための申請書設計と合意形成ロジック（法務・労務の確認ポイント） | 大企業エンジニア、SE | 競業避止・労務管理・知財漏洩対策<br/>「デジタル著作物」申請設計 |
| **第94弾** | `QIITA_ARTICLE_DETAIL_94.md` *(順次公開)* | **住民税「普通徴収」確定申告・鉄壁防衛編**<br/>住民税の特別徴収による本業・個人事業の混同を防ぐ！「普通徴収」選択と確定申告の実務ガイド | 副業サラリーマン、個人事業主 | 確定申告第二表「自分で納付」<br/>雑所得/事業所得, 自治体税務課念押し確認 |
| **第95弾** | `QIITA_ARTICLE_DETAIL_95.md` *(順次公開)* | **オープンコアモデル・Ed25519ライセンス編**<br/>「無料公開した自作ツール」を持続可能なOSSへ導くオープンコアモデルとライセンス設計 | プロダクトビルダー、OSS作者 | オープンコア境界線設計, Ed25519公開鍵署名<br/>完全オフラインライセンスキー改ざん検証 |
| **第96弾** | `QIITA_ARTICLE_DETAIL_96.md` *(順次公開)* | **Stripe/BOOTHデジタルツール無人販売編**<br/>Gumroad / BOOTH / Stripeで作る！デジタルツール・スクリプトの完全無人販売パイプライン | 個人開発者、デジタル物販派 | Stripe Payment Links, FastAPI Webhook<br/>自動ライセンス発行・即時納品メール送信 |
| **第97弾** | `QIITA_ARTICLE_DETAIL_97.md` *(順次公開)* | **QiitaからGitHubスター・ファン化誘導編**<br/>Qiitaの技術記事からGitHubスター・個人プロダクトへ自然に誘導する「読者をファンにする記事構成」 | 技術ブロガー、エンジニア発信者 | 黄金の5段構成 (ペイン共感・Mermaid・コード)<br/>好感を持たれる自然なCTA導線テンプレート |
| **第98弾** | `QIITA_ARTICLE_DETAIL_98.md` *(順次公開)* | **40代50代シニアエンジニア資産化戦略編**<br/>40代・50代エンジニアのための「定年・役職定年を見据えた個人ブランディングと技術ポートフォリオ」 | ベテランエンジニア、シニア層 | 役職定年対策, 泥臭いトラブル知見の資産化<br/>生きたGitHubポートフォリオ, 顧問・マイクロSaaS |
| **第99弾** | `QIITA_ARTICLE_DETAIL_99.md` *(順次公開)* | **段階的キャッシュフロー設計・二段階安全起業編**<br/>段階的なキャッシュフロー設計でリスクを最小化する！エンジニアのための堅実な独立・起業準備 | 起業志望エンジニア、独立準備中 | 労使折半社保の盾, 翌年住民税シミュレーション<br/>生活防衛資金2年分, 3大Goサイン基準 |
| **第100弾** | `QIITA_ARTICLE_DETAIL_100.md` *(順次公開)* | **【100本記念総括】エンジニア生涯生存ロードマップ**<br/>【100本記念総括】現場インフラエンジニアから自立型プロダクトビルダーへ！全技術・全戦略ロードマップ | 全エンジニア、OjisanTech氏、現場の全同志 | 7層アーキテクチャ総括, 現場知見結晶<br/>月額0円実装力, 自立型プロダクトビルダー宣言 |

---

### 🌟 シリーズ F：ベテランエンジニアのキャリア・生存戦略（特別編）
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要テーマ |
| :---: | :--- | :--- | :--- | :--- |
| **第30弾** | `QIITA_ARTICLE_DETAIL_30.md` *(順次公開)* | **大企業エンジニアのハイブリッド・キャリア戦略編**<br/>組織に依存せず、無謀な独立もしない。インフラエンジニアが本業の基盤を守りながら着実に個人プロダクトを育てる「ハイブリッド・キャリア戦略」 | 30代〜50代エンジニア、大企業勤務者、自作開発者 | キャリア論、知財防衛、副業規程<br/>二段階起業、個人ブランディング |

---

### ☸️ シリーズ N：Kubernetes・コンテナオーケストレーション現場実務・軽量クラスタ運用編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第101弾** | `QIITA_ARTICLE_DETAIL_101.md` *(順次公開)* | **手のひらミニPCで組む軽量Kubernetes（k3s）クラスタ編**<br/>手のひらミニPCで組む軽量Kubernetes（k3s）クラスタとMetalLBによるゼロ円L2ロードバランサー運用 | インフラエンジニア、K8s入門者 | `k3s`, `MetalLB`<br/>L2 ARP, LoadBalancer VIP |
| **第102弾** | `QIITA_ARTICLE_DETAIL_102.md` *(順次公開)* | **閉域LAN内Kubernetesの自動TLS暗号化編**<br/>Ingress-Nginx × Cert-Manager による閉域LAN内Kubernetesの自動TLS暗号化とオレオレ警告撲滅 | 情シス、Webインフラ担当 | `cert-manager`, Ingress-Nginx<br/>プライベートCA, AD GPO配布 |
| **第103弾** | `QIITA_ARTICLE_DETAIL_103.md` *(順次公開)* | **低コスト分散ブロックストレージ（Longhorn）編**<br/>Longhornによる低コスト分散ブロックストレージ構築とPod移動に追従する永続化（PV/PVC）設計 | ストレージ担当、K8s運用SE | `Longhorn`, iSCSI<br/>同期レプリケーション, CSI |
| **第104弾** | `QIITA_ARTICLE_DETAIL_104.md` *(順次公開)* | **Resource Limits/Requests設計 ＆ OOMKilled監視編**<br/>Kubernetes Resource Limits/Requests設計とOOMKilled（Exit Code 137）早期警報パイプライン | SRE、バックエンド開発者 | `kubernetes` Watch API<br/>QoS (Guaranteed/Burstable), Slack |
| **第105弾** | `QIITA_ARTICLE_DETAIL_105.md` *(順次公開)* | **HPAオートスケール ＆ メトリクスサーバー調律編**<br/>HPA (Horizontal Pod Autoscaler) とメトリクスサーバー軽量チューニングによる突発アクセス自動追従 | インフラSE、Web運用担当 | `metrics-server`, HPA v2<br/>stabilizationWindow, CPU 60% |
| **第106弾** | `QIITA_ARTICLE_DETAIL_106.md` *(順次公開)* | **CLI極限運用・自作kubectlプラグイン編**<br/>CLI極限運用・自作kubectlプラグイン（Krew / Bash）によるインフラ保守工数70%削減術 | 全Kubernetes運用者 | `kubectl-*` プラグイン<br/>再起動Podランキング抽出 |
| **第107弾** | `QIITA_ARTICLE_DETAIL_107.md` *(順次公開)* | **ConfigMap/Secretホットリロード自動化編**<br/>ConfigMap / Secretのホットリロード自動化とReloaderによるPod無停止ゼロダウンタイム反映 | DevSecOps、CI/CD担当 | `stakater/reloader`<br/>maxUnavailable: 0, ローリング更新 |
| **第108弾** | `QIITA_ARTICLE_DETAIL_108.md` *(順次公開)* | **DaemonSet全ノード一斉Syslog・Fluent Bit編**<br/>DaemonSetによる全ノード一斉Syslog・カーネルメッセージ収集とFluent Bit軽量パイプライン | ログ基盤SE、SRE | `Fluent Bit` (C言語製 30MB)<br/>DaemonSet, `/var/log/containers` |
| **第109弾** | `QIITA_ARTICLE_DETAIL_109.md` *(順次公開)* | **NetworkPolicyによるPod間ゼロトラスト分離編**<br/>NetworkPolicyによるPod間ゼロトラストネットワーク分離と特定名前空間の隔離防衛 | セキュリティSE、K8s設計者 | `NetworkPolicy`<br/>Default Deny, マイクロセグメンテーション |
| **第110弾** | `QIITA_ARTICLE_DETAIL_110.md` *(順次公開)* | **VeleroによるK8s丸ごとバックアップ＆DR移行編**<br/>VeleroによるK8sクラスタ丸ごとバックアップ＆異種ノード・オンプレ/クラウド間移行自動化 | BCP担当、インフラ運用リーダー | `Velero`, MinIO (S3)<br/>PVスナップショット, ワンコマンド復元 |

---

### 🗄️ シリーズ O：データベース深層チューニング・障害復旧・高可用性編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第111弾** | `QIITA_ARTICLE_DETAIL_111.md` *(順次公開)* | **PostgreSQL autovacuum凍結事故とXID周回脱出編**<br/>PostgreSQL autovacuum凍結事故とトランザクションID（XID）周回危機からの脱出実務 | DBA、PostgreSQL管理者 | `pg_database` (datfrozenxid)<br/>`vacuum_cost_limit`, VACUUM FREEZE |
| **第112弾** | `QIITA_ARTICLE_DETAIL_112.md` *(順次公開)* | **EXPLAIN ANALYZEで暴くSeq Scan撲滅術編**<br/>EXPLAIN ANALYZEで暴くインデックス不整合とSeq Scan撲滅・複合インデックス設計術 | バックエンド開発者、DBA | `EXPLAIN (ANALYZE, BUFFERS)`<br/>Covering Index (INCLUDE構文) |
| **第113弾** | `QIITA_ARTICLE_DETAIL_113.md` *(順次公開)* | **PgBouncerによるコネクション枯渇解消編**<br/>PgBouncerによるコネクション枯渇（Too many clients）解消とセッションプーリング極限設定 | システムアーキテクト、SRE | `PgBouncer`, Transaction Pooling<br/>1万接続収容, PAUSE/RESUME |
| **第114弾** | `QIITA_ARTICLE_DETAIL_114.md` *(順次公開)* | **WALレプリ遅延監視 ＆ Patroni自動フェイルオーバー編**<br/>WALストリーミングレプリケーション遅延監視とPatroniによる自動フェイルオーバー基盤 | インフラエンジニア、高可用性設計者 | `pg_stat_replication`, `etcd`<br/>`Patroni`, スプリットブレイン回避 |
| **第115弾** | `QIITA_ARTICLE_DETAIL_115.md` *(順次公開)* | **Redisメモリ枯渇とevictionポリシー最適化編**<br/>Redisメモリ枯渇（OOM command not allowed）とevictionポリシー（allkeys-lru）最適化設計 | Webアプリエンジニア、SRE | `maxmemory-policy allkeys-lru`<br/>`--bigkeys`, activedefrag |
| **第116弾** | `QIITA_ARTICLE_DETAIL_116.md` *(順次公開)* | **Redis永続化とfork遅延（CoW）対策編**<br/>Redis永続化（RDB vs AOF）によるディスクI/Oスパイク回避とfork遅延（Copy-on-Write）対策 | インフラエンジニア、Linux調律 | THP無効化 (`never`), `overcommit_memory=1`<br/>`no-appendfsync-on-rewrite` |
| **第117弾** | `QIITA_ARTICLE_DETAIL_117.md` *(順次公開)* | **MySQLスロークエリログ ＆ pt-query-digest編**<br/>MySQLスロークエリログとpt-query-digestによるボトルネックSQLの自動特定・可視化 | MySQL運用者、バックエンド開発者 | `pt-query-digest`, Percona Toolkit<br/>スロークエリ統計ランキング解析 |
| **第118弾** | `QIITA_ARTICLE_DETAIL_118.md` *(順次公開)* | **オンラインスキーマ変更（gh-ost）無停止移行編**<br/>オンラインスキーマ変更（gh-ost）による数億レコード巨大テーブルの無停止マイグレーション | DBA、リードエンジニア | GitHub `gh-ost`<br/>Binlogストリーミング, トリガーレスDDL |
| **第119弾** | `QIITA_ARTICLE_DETAIL_119.md` *(順次公開)* | **PostgreSQL Point-in-Time Recovery (PITR) 編**<br/>PostgreSQL Point-in-Time Recovery (PITR) 実践リカバリ演習と誤DELETEからの秒単位過去復元 | データベース管理者、情シス責任者 | `pg_basebackup`, WALアーカイブ<br/>`recovery_target_time`, 秒単位復旧 |
| **第120弾** | `QIITA_ARTICLE_DETAIL_120.md` *(順次公開)* | **SQLiteからPostgreSQLへのゼロダウンタイム移行編**<br/>SQLiteからPostgreSQLへのゼロダウンタイム・スキーマ変換＆データ移行パイプライン | フルスタック開発者、内製化推進者 | `pgloader`, 型自動キャスト<br/>シーケンス自動同期, 並行ロック解消 |

---

### 🐧 シリーズ P：Linuxカーネル・eBPF・OS深層パフォーマンス分析編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第121弾** | `QIITA_ARTICLE_DETAIL_121.md` *(順次公開)* | **eBPF/BCCによる短命プロセス追跡編**<br/>eBPF/BCCで暴く謎の高負荷！カーネル空間で短命プロセス（Short-lived process）の挙動を追跡する | SRE、Linuxトラブルシューター | `eBPF`, BCC (`execsnoop`)<br/>`kprobe:sys_execve`, カーネルフック |
| **第122弾** | `QIITA_ARTICLE_DETAIL_122.md` *(順次公開)* | **Linux CPU分析（perf / FlameGraph）完全ガイド編**<br/>Linux CPUボトルネック分析（perf / FlameGraph）完全ガイドとボトルネック関数のあぶり出し | パフォーマンスエンジニア、SRE | Linux `perf`, `FlameGraph`<br/>コールスタックサンプリング, SVG可視化 |
| **第123弾** | `QIITA_ARTICLE_DETAIL_123.md` *(順次公開)* | **/proc /sys 直読み超軽量メトリクス収集編**<br/>/proc と /sys を直接読み解く超軽量自作メトリクス収集Pythonエージェント（外部依存ゼロ） | 閉域網SE、組み込みエンジニア | `/proc/stat`, `/proc/meminfo`<br/>外部ライブラリゼロ (10MB常駐) |
| **第124弾** | `QIITA_ARTICLE_DETAIL_124.md` *(順次公開)* | **ファイルシステム最適化（noatime/nodiratime）編**<br/>Linuxファイルシステム（ext4 vs XFS）のマウントオプション最適化（noatime/nodiratime）とWrite性能爆上げ | ストレージ管理者、Linux SE | `noatime,nodiratime`, `/etc/fstab`<br/>不要Writeゼロ化, SSD寿命延伸 |
| **第125弾** | `QIITA_ARTICLE_DETAIL_125.md` *(順次公開)* | **vm.dirty_ratio 調律とI/Oフリーズ防止編**<br/>vm.dirty_ratio とディスク遅延！カーネルフラッシュ調律でWrite性能爆上げとI/Oフリーズ防止 | インフラエンジニア、カーネル調律 | `vm.dirty_background_ratio=5`<br/>`vm.dirty_ratio=10`, 突発I/O停止根絶 |
| **第126弾** | `QIITA_ARTICLE_DETAIL_126.md` *(順次公開)* | **iptables vs nftables パケット処理超高速化編**<br/>iptables vs nftables マイグレーションとパケットフィルタリング超高速化の現場実践 | ネットワークSE、セキュリティ担当 | `nftables`, Sets (O(1) ハッシュ検索)<br/>`inet` 統合テーブル, iptables-translate |
| **第127弾** | `QIITA_ARTICLE_DETAIL_127.md` *(順次公開)* | **Linux名前空間（Namespaces）で自作するミニコンテナ編**<br/>Linux名前空間（Namespaces）で自作するミニコンテナ！Dockerの仕組みをBashだけで完全理解する | コンテナ開発者、低レイヤー愛好家 | `unshare` (PID/Mount/Net namespaces)<br/>`chroot`, Alpine Rootfs |
| **第128弾** | `QIITA_ARTICLE_DETAIL_128.md` *(順次公開)* | **cgroups v2 による物理リソースハードリミット編**<br/>cgroups v2によるCPU・メモリ・I/O帯域の厳格なハードリミット制御とリソース強奪防止 | インフラSE、マルチテナント運用者 | `cgroups v2` (`memory.max`, `cpu.max`)<br/>`systemd-run`, プロセス幽閉の檻 |
| **第129弾** | `QIITA_ARTICLE_DETAIL_129.md` *(順次公開)* | **TCP keepalive ＆ TIME_WAITソケット枯渇対策編**<br/>TCP keepalive と TIME_WAIT ソケット枯渇（tcp_tw_reuse）の真実とカーネルネットワーク調律 | Webバックエンドエンジニア、SRE | `tcp_tw_reuse=1`, `ip_local_port_range`<br/>エフェメラルポート枯渇完全回避 |
| **第130弾** | `QIITA_ARTICLE_DETAIL_130.md` *(順次公開)* | **Softirq高負荷解消 ＆ RPS/RFSマルチコア分散編**<br/>ゾンビ割り込み（Softirq）高負荷の原因究明とRPS/RFSマルチキューNIC最適化 | ネットワークエンジニア、サーバー管理者 | `RPS (Receive Packet Steering)`<br/>CPU全コア均等分散, %si 100%解消 |

---

### 💾 シリーズ Q：分散ストレージ・NAS・バックアップ・DR対策編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第131弾** | `QIITA_ARTICLE_DETAIL_131.md` *(順次公開)* | **ZFSスナップショットによるランサムウェア耐性NAS編**<br/>ZFSプール構築と読み取り専用スナップショット自動複製によるランサムウェア完全耐性NAS運用 | ファイルサーバー管理者、情シス | OpenZFS, Copy-on-Write<br/>`.zfs/snapshot` 自己復旧, 即時ロールバック |
| **第132弾** | `QIITA_ARTICLE_DETAIL_132.md` *(順次公開)* | **MinIO S3互換ストレージ ＆ Erasure Coding編**<br/>MinIOによるオンプレS3互換オブジェクトストレージの構築と分散Erasure Coding極限冗長化 | クラウドコスト削減担当、インフラSE | `MinIO` (S3 API互換)<br/>Erasure Coding, 2台同時故障耐性 |
| **第133弾** | `QIITA_ARTICLE_DETAIL_133.md` *(順次公開)* | **rclone暗号化同期 ＆ 帯域制限（bwlimit）編**<br/>rcloneによるオンプレ・クラウド間暗号化バックアップ自動化と帯域制限（Bandwidth Limit）設計 | インフラ運用担当、BCP担当 | `rclone` (Crypt透過AES-256)<br/>`--bwlimit` 時間帯別帯域制御 |
| **第134弾** | `QIITA_ARTICLE_DETAIL_134.md` *(順次公開)* | **Samba3マルチチャネル ＆ 非同期I/O爆速化編**<br/>Samba (SMB) パフォーマンスチューニング（aio / vfs / マルチチャネル）による爆速ファイル共有 | SE、ファイルサーバー担当 | SMB 3.1.1 Multi-Channel, `vfs_fruit`<br/>非同期AIO, ゼロコピーsendfile |
| **第135弾** | `QIITA_ARTICLE_DETAIL_135.md` *(順次公開)* | **iSCSIターゲット（targetcli）によるゼロ円SAN編**<br/>iSCSIターゲット（targetcli）とイニシエータによるローカル風ブロックストレージ共有とクラスタ連携 | 仮想化基盤管理者、DBインフラSE | Linux LIO (`targetcli-fb`)<br/>iSCSI (TCP 3260), RAWデバイス提供 |
| **第136弾** | `QIITA_ARTICLE_DETAIL_136.md` *(順次公開)* | **BorgBackup重複排除 ＆ 容量90%削減編**<br/>BorgBackupによる重複排除・高圧縮・完全暗号化バックアップと容量節約90%の極意 | バックアップ担当、SRE | `BorgBackup`, 可変長チャンク重複排除<br/>ZSTD圧縮, `borg mount` FUSE復元 |
| **第137弾** | `QIITA_ARTICLE_DETAIL_137.md` *(順次公開)* | **Syncthing P2P分散同期によるゼロインフラBCP編**<br/>異拠点間ファイル同期（Syncthing）によるクラウド不要・ゼロ円BCP/DR分散同期基盤 | 中小企業情シス、BCP担当 | `Syncthing` (P2P TLS 1.3)<br/>中央サーバーゼロ, 拠点間自動レプリカ |
| **第138弾** | `QIITA_ARTICLE_DETAIL_138.md` *(順次公開)* | **SMART不良セクタ予兆検知 ＆ 故障前自動退避編**<br/>ハードディスク不良セクタ予兆検知とsmartctlセルフテスト自動スケジューラ＆故障前退避 | ストレージSE、データセンター保守 | `smartctl` (ID 5, 196, 197, 198)<br/>深夜自動ロングテスト, 突然死ゼロ化 |
| **第139弾** | `QIITA_ARTICLE_DETAIL_139.md` *(順次公開)* | **NFSv4 Kerberos認証 ＆ ロック解放トラブルシュート編**<br/>NFSv4 Kerberos認証とクライアント再起動時のファイルロック解放（Stale file handle）トラブルシュート | Linuxシステム運用SE | NFSv4 (sec=krb5p), RPCSEC_GSS<br/>`umount -l`, hard/intr マウント |
| **第140弾** | `QIITA_ARTICLE_DETAIL_140.md` *(順次公開)* | **M-DISC光ディスク ＆ 100年エアギャップ金庫保管編**<br/>コールドストレージ・光ディスク（M-DISC）による100年データ長期保存とオフライン金庫保管設計 | 法務監査、アーカイブ担当、CIO | M-DISC BDXL (100GB), UDF 2.60<br/>SHA-256 チェックサム, 物理エアギャップ |

---

### 🔑 シリーズ R：次世代認証・IdP連携・ゼロトラストアクセス編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第141弾** | `QIITA_ARTICLE_DETAIL_141.md` *(順次公開)* | **KeycloakオンプレSSO ＆ Active Directory統合編**<br/>Keycloakによるオンプレミスシングルサインオン（SSO / OIDC）構築とActive Directory透過統合 | 統合認証基盤担当、情シス責任者 | `Keycloak 24.x`, PostgreSQL<br/>User Federation, LDAP同期, OIDC |
| **第142弾** | `QIITA_ARTICLE_DETAIL_142.md` *(順次公開)* | **OAuth2 / OIDC認可コードフロー ＆ JWT署名検証編**<br/>OAuth2 / OpenID Connect (OIDC) 認可コードフローの現場トラブルシュートとトークン署名検証 | Webアプリ開発者、セキュリティSE | `PyJWT`, PyJWKClient<br/>PKCE (RFC 7636), RS256公開鍵検証 |
| **第143弾** | `QIITA_ARTICLE_DETAIL_143.md` *(順次公開)* | **WebAuthn / Passkey 生体認証ログイン実装編**<br/>WebAuthn / Passkey (パスキー) を自作Web管理画面に組み込む完全実装（生体認証ログイン） | フロントエンド・バックエンドエンジニア | FIDO2 / `py_webauthn`<br/>Windows Hello / Touch ID, パスワードレス |
| **第144弾** | `QIITA_ARTICLE_DETAIL_144.md` *(順次公開)* | **LDAPS (ポート636) 証明書失効検知 ＆ 自動テスト編**<br/>LDAP over TLS (LDAPS: 636) 証明書失効・更新の現場落とし穴と接続自動検証スクリプト | AD管理者、LAN内システム担当 | LDAPS (TCP 636), OpenSSL<br/>証明書期限切れ30日前警告, SAN検証 |
| **第145弾** | `QIITA_ARTICLE_DETAIL_145.md` *(順次公開)* | **mTLS（相互TLS）マイクロサービス間ゼロトラスト編**<br/>mTLS（相互TLS認証）によるマイクロサービス間ゼロトラスト通信と自己署名CA運用設計 | バックエンドアーキテクト、SecOps | Mutual TLS (mTLS), OpenSSL<br/>クライアント証明書検証, APIキー廃止 |
| **第146弾** | `QIITA_ARTICLE_DETAIL_146.md` *(順次公開)* | **Cloudflare Tunnel によるポート開放不要公開編**<br/>Cloudflare Zero Trust (Cloudflare Tunnels) でルーター穴あけ不要のセキュアLAN内Web公開 | 自宅サーバー派、情シス、拠点管理者 | `cloudflared` (QUIC トンネル)<br/>Cloudflare Access, ポート開放完全0 |
| **第147弾** | `QIITA_ARTICLE_DETAIL_147.md` *(順次公開)* | **WireGuard高速メッシュVPN ＆ QRコード自動生成編**<br/>WireGuardによる高速メッシュVPN自作とクライアント自動設定QRコード生成スクリプト | リモートワーク管理者、情シス | `WireGuard` (Linux Kernel)<br/>`qrencode` スマホ即時キッティング |
| **第148弾** | `QIITA_ARTICLE_DETAIL_148.md` *(順次公開)* | **JWT即時ブラックリスト失効（Redis TTL）設計編**<br/>JWTトークンの改ざん防止・有効期限切れ・即時ブラックリスト失効管理（Redis連携）設計 | API設計者、バックエンドエンジニア | `jti` (JWT ID), Redis TTL<br/>ログアウト即時無効化, メモリ自動蒸発 |
| **第149弾** | `QIITA_ARTICLE_DETAIL_149.md` *(順次公開)* | **Samba AD-DC による完全フリーActive Directory編**<br/>Samba AD-DC によるオンプレミスクラウドフリーActive Directoryドメイン構築とGPO集中管理 | 中小企業情シス、Windows運用SE | `samba-tool` domain provision<br/>CAL完全不要, Windows RSAT GPO管理 |
| **第150弾** | `QIITA_ARTICLE_DETAIL_150.md` *(順次公開)* | **RBAC (ロールベースアクセス制御) 認可設計編**<br/>RBAC (ロールベースアクセス制御) のDBテーブル設計とFastAPI認可デコレータ完全実装 | Webアプリケーション設計者 | 5テーブル正規化 (RBAC)<br/>FastAPI Depends 依存性注入, 権限制御 |

---

### 🔌 シリーズ S：IoT・エッジデバイス・センシング・現場ハードウェア連携編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第151弾** | `QIITA_ARTICLE_DETAIL_151.md` *(順次公開)* | **シリアル通信（RS-485 / UART）工場機器直結編**<br/>Raspberry Pi / Linux SBC のシリアル通信（UART / RS-485）による工場機器・計測器直結自動化 | 工場DX担当、IoTエンジニア | `pyserial`, USB-RS485<br/>1.2km伝送, レガシー計測器自動回収 |
| **第152弾** | `QIITA_ARTICLE_DETAIL_152.md` *(順次公開)* | **超軽量MQTTブローカー（Mosquitto）データ収集編**<br/>MQTTブローカー（Mosquitto）による大量エッジセンサーデータ超軽量収集とPub/Sub設計 | IoTアーキテクト、組込エンジニア | `Eclipse Mosquitto` (メモリ4MB)<br/>MQTT 2バイトヘッダ, QoS 0/1/2 |
| **第153弾** | `QIITA_ARTICLE_DETAIL_153.md` *(順次公開)* | **Modbus TCP / RTU による産業用PLC連携編**<br/>Modbus TCP / RTU によるPLC機器データ読み出しPython自動化（pymodbus）と現場連携 | 製造業IT担当、OT/IT統合SE | `pymodbus`, Modbus TCP (:502)<br/>保持レジスタ読取, 三菱/オムロンPLC |
| **第154弾** | `QIITA_ARTICLE_DETAIL_154.md` *(順次公開)* | **GPIOリレーによる物理コールドリセット自作編**<br/>GPIO制御とリレー回路による物理サーバー強制コールドリセット自作（IPMI未搭載機救済） | フィールドエンジニア、ハードウェアSE | RPi GPIO + 5V機械式リレー<br/>マザーボードPWR_SW短絡 (5秒長押し) |
| **第155弾** | `QIITA_ARTICLE_DETAIL_155.md` *(順次公開)* | **BLEビーコンによるLAN内備品リアルタイム追跡編**<br/>BLEビーコン（iBeacon / Eddystone）によるLAN内備品・資材のリアルタイム位置トラッキング | 総務・情シス、備品管理担当 | `bleak` (Bluetooth Low Energy)<br/>RSSI電波強度距離推定, ルーム特定 |
| **第156弾** | `QIITA_ARTICLE_DETAIL_156.md` *(順次公開)* | **LoRaWAN長距離無線 ＆ 私設LPWAモニタリング編**<br/>LoRaWAN長距離無線による電源・ネットのない屋外施設・倉庫モニタリング基盤 | スマート農業、屋外施設管理者 | `LoRaWAN` (920MHz 技適)<br/>`ChirpStack`, 見通し5km月額0円伝送 |
| **第157弾** | `QIITA_ARTICLE_DETAIL_157.md` *(順次公開)* | **音響FFT解析によるモーター異音予知保全編**<br/>音響センシング・FFT（高速フーリエ変換）によるモーター異音・異常振動予知保全PoC | 保全エンジニア、品質管理、エッジAI | `numpy.fft`, `pyaudio`<br/>周波数スペクトル解析, 異常ピーク検知 |
| **第158弾** | `QIITA_ARTICLE_DETAIL_158.md` *(順次公開)* | **エッジLinuxの完全ReadOnly化（不壊OS）編**<br/>エッジデバイス向け軽量Linux OS（Alpine / Buildroot）組み込みとReadOnly化（突然の電源断耐性） | 組込Linux開発者、フィールドSE | `OverlayFS`, tmpfs RAMディスク<br/>コンセント引き抜き耐性, SD破損ゼロ |
| **第159弾** | `QIITA_ARTICLE_DETAIL_159.md` *(順次公開)* | **GPS PPS信号による超高精度ナノ秒NTP自作編**<br/>NTPに頼らないGPSレシーバー（PPS信号）による超高精度ナノ秒NTP/PTPサーバー自作 | 閉域網インフラSE、金融・計測SE | GPS u-blox, PPS物理パルス (GPIO)<br/>`chrony` Stratum 1, 完全閉域時刻基盤 |
| **第160弾** | `QIITA_ARTICLE_DETAIL_160.md` *(順次公開)* | **エッジOTA安全更新 ＆ 自動ロールバック編**<br/>エッジデバイスのOTA（Over-The-Air）ファームウェア・アプリ安全更新パイプラインと自動ロールバック | IoT運用リーダー、DevOps | コンテナ自律ヘルスチェック<br/>自動ロールバック, 端末文鎮化完全防止 |

---

### 📊 シリーズ T：エンタープライズ監視・オブザーバビリティ・SRE実践編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第161弾** | `QIITA_ARTICLE_DETAIL_161.md` *(順次公開)* | **Prometheus ＋ Grafana 自立型監視基盤編**<br/>Prometheus ＋ Grafanaによるオンプレミス完全自立型メトリクス監視基盤構築とTSDB最適化 | SRE、インフラ監視担当 | `Prometheus`, `Grafana`<br/>TSDB 30日保持, Pullスクレイピング |
| **第162弾** | `QIITA_ARTICLE_DETAIL_162.md` *(順次公開)* | **Grafana Loki ＋ Promtail 超軽量ログ集約編**<br/>Loki ＋ Promtail による「メモリ激減」超軽量ログ集約スタックとLogQL検索術 | ログ基盤運用者、SRE | `Grafana Loki`, `Promtail`<br/>ラベルのみインデックス, LogQL |
| **第163弾** | `QIITA_ARTICLE_DETAIL_163.md` *(順次公開)* | **OpenTelemetry (OTel) 分散トレーシング編**<br/>OpenTelemetry (OTel) で始める分散トレーシング入門とマイクロサービスのボトルネック可視化 | マイクロサービス開発者、SRE | `OpenTelemetry`, `Jaeger`<br/>W3C TraceContext, ガントチャート分析 |
| **第164弾** | `QIITA_ARTICLE_DETAIL_164.md` *(順次公開)* | **Alertmanager アラート疲弊撲滅 ＆ 抑制設計編**<br/>Alertmanagerによるアラート疲弊（Alert Fatigue）撲滅とグルーピング・抑制・ルーティング設計 | オンコール担当、SREリーダー | `Alertmanager`<br/>Inhibition Rules (抑制), Grouping |
| **第165弾** | `QIITA_ARTICLE_DETAIL_165.md` *(順次公開)* | **Blackbox Exporter 外形死活・SSL期限監視編**<br/>黒番監視（Blackbox Exporter）によるHTTP / DNS / TCP / ICMP外形監視完全網羅 | Webマスター、インフラ保守担当 | `Blackbox Exporter`<br/>SSL残日数監視, HTTP 2xxプローブ |
| **第166弾** | `QIITA_ARTICLE_DETAIL_166.md` *(順次公開)* | **SLO / SLI 設計 ＆ エラーバジェット自動算出編**<br/>SLO / SLI 設計とエラーバジェット算出スクリプトの実装（SRE信頼性エンジニアリング実践） | SRE、プロダクトマネージャー | SLO (99.9%), SLI, Error Budget<br/>PromQL 30日ローリング算出 |
| **第167弾** | `QIITA_ARTICLE_DETAIL_167.md` *(順次公開)* | **自作カオスエンジニアリング耐障害試験編**<br/>カオスエンジニアリング（自作カオススクリプト）による耐障害性ストレステスト自動化 | 品質保証、インフラアーキテクト | Linux `tc` (遅延・パケットロス注入)<br/>コンテナ突発死試験, レジリエンス検証 |
| **第168弾** | `QIITA_ARTICLE_DETAIL_168.md` *(順次公開)* | **SNMP Exporter 異種NW機器統合Prometheus編**<br/>SNMP Exporterによる異種ネットワーク機器の一括Prometheusメトリクス化とMIBコンパイル | ネットワーク監視担当、情シス | `SNMP Exporter`, MIBコンパイル<br/>64bit カウンタ (ifHCInOctets) |
| **第169弾** | `QIITA_ARTICLE_DETAIL_169.md` *(順次公開)* | **Node Exporter Textfile Collector即時可視化編**<br/>Node Exporterカスタムテキストコレクターによる現場固有メトリクス即時可視化（Textfile Collector） | フルスタックエンジニア、情シス | Textfile Collector (`.prom`)<br/>アトミックmv書き出し, 1行メトリクス化 |
| **第170弾** | `QIITA_ARTICLE_DETAIL_170.md` *(順次公開)* | **インシデント初動Runbook自動連携オーケストラ編**<br/>インシデント発生時のランブック（Runbook）自動呼び出し＆初動オーケストレーション自動化 | インシデントコマンダー、SRE | Alertmanager Webhook, FastAPI<br/>一次診断コマンド自動採取, Slack直通 |

---

### 🧠 シリーズ U：自律型AIエージェント・高度RAG・ローカル推論パイプライン編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第171弾** | `QIITA_ARTICLE_DETAIL_171.md` *(順次公開)* | **LangGraph 自律型インフラ調査エージェント編**<br/>LangGraph / 自作ステートマシンによる自律型インフラ調査・一次切り分けAIエージェント設計 | AIエンジニア、SRE | `LangGraph`, StateGraph<br/>循環ループ, 読取専用安全サンドボックス |
| **第172弾** | `QIITA_ARTICLE_DETAIL_172.md` *(順次公開)* | **ハイブリッドRAG ＆ Cross-Encoder リランク編**<br/>ハイブリッドRAG（Dense Vector ＋ BM25 ＋ Cross-Encoder Reranker）の極限チューニング | RAGエンジニア、検索基盤開発者 | `BM25Okapi` + Dense Vector<br/>`BAAI/bge-reranker-base`, 型番検索完全対応 |
| **第173弾** | `QIITA_ARTICLE_DETAIL_173.md` *(順次公開)* | **vLLM PagedAttention 高スループット推論編**<br/>vLLM / llama.cpp による高スループット・低遅延オンプレ推論サーバー構築とPagedAttention設計 | AI基盤エンジニア、MLOps | `vLLM` (PagedAttention)<br/>Continuous Batching, OpenAI互換API |
| **第174弾** | `QIITA_ARTICLE_DETAIL_174.md` *(順次公開)* | **Function Calling（Tools）DB安全接続設計編**<br/>関数呼び出し（Function Calling / Tools）によるローカルLLMへのDB・LAN内API安全接続設計 | バックエンドAI開発者 | Tool Calling, JSON Schema<br/>Pydantic引数検証, 生SQL完全排除 |
| **第175弾** | `QIITA_ARTICLE_DETAIL_175.md` *(順次公開)* | **構造化出力（Instructor / Outlines）JSON確定編**<br/>構造化出力（Instructor / Outlines）でJSONハルシネーションを100%遮断する実装技術 | データパイプライン開発者 | `instructor`, Pydantic<br/>文法制約デコーディング, パースエラー0% |
| **第176弾** | `QIITA_ARTICLE_DETAIL_176.md` *(順次公開)* | **Docling / MinerU 複雑PDFマルチモーダル解析編**<br/>テキスト・画像・表が混在するLAN内PDFのマルチモーダルParser（MinerU / Docling）実践 | RAG前処理担当、DXエンジニア | IBM `Docling`<br/>結合セル表復元, 2段組Markdown化 |
| **第177弾** | `QIITA_ARTICLE_DETAIL_177.md` *(順次公開)* | **Unsloth / PEFT LAN内データ爆速LoRA微調整編**<br/>自前LAN内ドキュメントによるLoRA微調整（Unsloth / PEFT）超軽量ファインチューニング手順 | LLM研究開発者、個人ビルダー | `Unsloth` (QLoRA 4bit)<br/>メモリ80%削減, 市販GPU単体GGUF出力 |
| **第178弾** | `QIITA_ARTICLE_DETAIL_178.md` *(順次公開)* | **Prompt Caching 初回トークン（TTFT）半減編**<br/>プロンプトキャッシュ（Prompt Caching）によるローカルLLMの初回トークン時間（TTFT）半減術 | AIフロントエンド開発者 | KV Cache Prefix Caching<br/>TTFT 80%短縮, システムプロンプト再利用 |
| **第179弾** | `QIITA_ARTICLE_DETAIL_179.md` *(順次公開)* | **Ragas によるRAG精度自動評価・CI/CDゲート編**<br/>RAG検索精度評価（Ragas）による忠実度・関連度自動スコアリングとCI/CD品質ゲート | QAエンジニア、LLMOps | `Ragas` (Faithfulness, Relevance)<br/>ハルシネーション自動スコア判定 |
| **第180弾** | `QIITA_ARTICLE_DETAIL_180.md` *(順次公開)* | **LLM Guard 多層プロンプトインジェクション防御編**<br/>LLM Guard / NeMo Guardrails によるプロンプトインジェクション多層防御と情報漏洩遮断 | AIセキュリティ責任者 | `LLM Guard`<br/>Jailbreak検知, PII自動マスキング, 機密遮断 |

---

### ⚔️ シリーズ V：サイバー攻撃シミュレーション・ペネトレーションテスト・DFIR編
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術 |
| :---: | :--- | :--- | :--- | :--- |
| **第181弾** | `QIITA_ARTICLE_DETAIL_181.md` *(順次公開)* | **LAN内ペネトレーションテスト自己診断編**<br/>LAN内におけるペネトレーションテスト（Metasploit / Nmap）自己診断手順と安全境界設計 | セキュリティ担当、SE | `Nmap` NSE (safe scripts), Metasploit<br/>非破壊スキャン, 除外IPスコープ設計 |
| **第182弾** | `QIITA_ARTICLE_DETAIL_182.md` *(順次公開)* | **標的型攻撃メール訓練基盤自作 ＆ 意識スコア編**<br/>標的型攻撃メール訓練スクリプトとLAN内セキュリティ意識スコアリング基盤自作 | 人事総務、セキュリティ教育担当 | `Gophish`, FastAPI トラップWeb<br/>クリック率集計, 即時教育コンテンツ |
| **第183弾** | `QIITA_ARTICLE_DETAIL_183.md` *(順次公開)* | **ハニーポット（OpenCanary）LAN内おとり検知編**<br/>ハニーポット（Cowrie / OpenCanary）構築によるLAN内侵入者の早期おとり検知 | SOC、LAN内防衛エンジニア | `OpenCanary`, 偽SMB/RDP<br/>ラテラルムーブメント検知, 誤検知率0% |
| **第184弾** | `QIITA_ARTICLE_DETAIL_184.md` *(順次公開)* | **Sysmon ＋ WEF エンドポイント脅威検知編**<br/>Windows Event Forwarding (WEF) とSysmonによるエンドポイント脅威検知基盤 | Windows Server管理者、SecOps | `Sysmon` (Event ID 1), SwiftOnSecurity<br/>Windows Event Forwarding (WinRM HTTPS) |
| **第185弾** | `QIITA_ARTICLE_DETAIL_185.md` *(順次公開)* | **Volatility 3 メモリフォレンジック解析編**<br/>メモリダンプ（Volatility 3）によるインシデントフォレンジック解析実践と不正プロセス特定 | DFIR担当、セキュリティインシデント班 | `Volatility 3`, RAWメモリダンプ<br/>`windows.malfind`, ファイルレス攻撃特定 |
| **第186弾** | `QIITA_ARTICLE_DETAIL_186.md` *(順次公開)* | **FWログ相関分析 ＆ C2ビーコニング数学検知編**<br/>ファイアウォールログ・WAFログの自動相関分析とC2通信ビーコニング検知アルゴリズム | SOCアナリスト、ネットワーク監視SE | 通信間隔デルタ統計分析 (`numpy`)<br/>変動係数 (CV < 0.15), 潜伏C2通信捕捉 |
| **第187弾** | `QIITA_ARTICLE_DETAIL_187.md` *(順次公開)* | **DNSトンネリング検知 ＆ エントロピー解析編**<br/>DNSトンネリング攻撃の検出（長大サブドメイン・高頻度クエリ検知アルゴリズム） | DNS管理者、ネットワークセキュリティSE | シャノン・エントロピー計算 (閾値3.8)<br/>長大サブドメイン検知, ポート53流出遮断 |
| **第188弾** | `QIITA_ARTICLE_DETAIL_188.md` *(順次公開)* | **Hashcat パスワードクラック耐性検証編**<br/>パスワードクラック耐性検証（Hashcat / John the Ripper）と辞書攻撃対策・強化手順 | 認証基盤設計者、セキュリティ監査 | `Hashcat`, GPU並列クラック<br/>`Argon2id` (メモリ64MB), bcrypt コスト調律 |
| **第189弾** | `QIITA_ARTICLE_DETAIL_189.md` *(順次公開)* | **ランサムウェア挙動模倣ストレステスト編**<br/>ランサムウェア挙動模倣スクリプトによるEDR / バックアップ検知能力ストレステスト | セキュリティ監査、SRE | 大量ファイル擬似暗号化シミュレータ<br/>高エントロピー化, カナリーファイル監視 |
| **第190弾** | `QIITA_ARTICLE_DETAIL_190.md` *(順次公開)* | **CSIRTインシデント即時隔離プレイブック編**<br/>CSIRTインシデント対応プレイブック自動化（通信遮断・証拠保全・端末隔離）パイプライン | CSIRT隊長、セキュリティ運用責任者 | `iptables DROP` (ワンコマンド隔離)<br/>揮発性証拠高速保全, SHA-256マニフェスト |

---

### 🚀 シリーズ W：マイクロSaaS開発・エンジニア独立・生涯自立エコシステム編（完結・記念碑）
| 弾数 | ファイル | タイトル・テーマ | 対象読者 | 主要技術・戦略 |
| :---: | :--- | :--- | :--- | :--- |
| **第191弾** | `QIITA_ARTICLE_DETAIL_191.md` *(順次公開)* | **LAN内ツールからマイクロSaaSへの転換編**<br/>LAN内便利ツールから「マイクロSaaS」への転換：マルチテナントDB設計とスキーマ分離術 | プロダクトビルダー、SaaS志望者 | PostgreSQL `Row-Level Security (RLS)`<br/>テナント間データ漏洩完全遮断 |
| **第192弾** | `QIITA_ARTICLE_DETAIL_192.md` *(順次公開)* | **3日で組むマイクロSaaSボイラープレート編**<br/>認証・課金・ダッシュボードを3日で組むマイクロSaaSボイラープレート設計（FastAPI × Stripe） | 個人開発者、スタートアップ | `FastAPI`, `Stripe Checkout`<br/>Webhook署名検証, Customer Portal |
| **第193弾** | `QIITA_ARTICLE_DETAIL_193.md` *(順次公開)* | **独自ドメイン ＆ メール到達率100%DNS編**<br/>独自ドメイン取得からCloudflare・メール配信（Resend / SendGrid）到達率100%設定 | Webマスター、SaaS開発者 | `Cloudflare DNS`, `Resend`<br/>SPF, DKIM, DMARC (`p=reject`), 到達率100% |
| **第194弾** | `QIITA_ARTICLE_DETAIL_194.md` *(順次公開)* | **利用規約・プライバシー・特商法実務作成編**<br/>サービス利用規約・プライバシーポリシー・特商法表記のエンジニア向け実務作成術 | 個人起業家、デジタル物販派 | 損害賠償上限 (直近月額), バーチャルオフィス<br/>特商法住所・電話番号合法非公開テクニック |
| **第195弾** | `QIITA_ARTICLE_DETAIL_195.md` *(順次公開)* | **検索流入（SEO）テクニカルライティング編**<br/>検索流入（SEO）と技術ブログで現場課題を届けるテクニカルライティング・キーワード設計 | 技術ブロガー、個人マーケター | ロングテールペイン解決, 図解・コード抜粋<br/>自然なCTA誘導, 広告費0円オウンドメディア |
| **第196弾** | `QIITA_ARTICLE_DETAIL_196.md` *(順次公開)* | **Product Hunt / はてブ ローンチ初期獲得編**<br/>Product Hunt / はてなブックマーク / Hacker News ローンチ戦略と初期ユーザー獲得実務 | 海外展開志望者、プロダクトビルダー | Product Hunt火曜ローンチ, Show HN<br/>動くGIFバナー, 初日3,000ユニーク獲得 |
| **第197弾** | `QIITA_ARTICLE_DETAIL_197.md` *(順次公開)* | **1人運営サポート自動化（AI返信＋Sentry）編**<br/>1人運用を可能にするカスタマーサポート自動化（AI一次返信＋Sentryエラー直結）設計 | 1人起業家、マイクロSaaS運用者 | RAG自動一次回答メール (Resend)<br/>Sentryクラスタレント即時Slack通知 |
| **第198弾** | `QIITA_ARTICLE_DETAIL_198.md` *(順次公開)* | **合同会社設立 ＆ マイクロ法人税務最適化編**<br/>会社員から合同会社設立・マイクロ法人化による税務最適化（役員報酬・社宅・経費化）実務 | 副業エンジニア、独立準備中 | 合同会社 (設立費6万), 家賃社宅化<br/>本業社保の盾, 役員報酬ゼロスキーム |
| **第199弾** | `QIITA_ARTICLE_DETAIL_199.md` *(順次公開)* | **ひとり起業・MRR100万円ロードマップ編**<br/>ひとり起業・マイクロSaaSのMRR（月次経常収益）100万円ロードマップと撤退基準 | 自立志望エンジニア、SaaS創業者 | $29×220社モデル, LTV/CAC<br/>月次解約率 (Churn < 4%), 6ヶ月撤退ルール |
| **第200弾** | `QIITA_ARTICLE_DETAIL_200.md` *(順次公開)* | **【第200弾完全完結記念碑】生涯自立型プロダクトビルダー宣言**<br/>【第200弾完全完結記念碑】現場の労働者から自由なる「生涯自立型プロダクトビルダー」へ！全200記事完走記念碑 | 全エンジニア、OjisanTech氏、現場の全同志 | 14層大系総括, 自立型ビルダー宣言<br/>月額0円実装力, 生涯生存エコシステム完結 |

---
---

## 🛡️ 本番適用・セキュリティ運用の3大原則
1. **最小特権の原則 (PoLP)**: スクリプトやデーモンは可能な限り非rootユーザーで実行し、必要なCapabilityやグループのみを付与すること
2. **フェイルソフト設計**: 監視・バッチの障害が基幹業務サービスを道連れに停止させないよう、独立プロセス・独立リソース制限（cgroups）を徹底すること
3. **証拠保全と再現性**: 障害発生時のログ・スタックトレースを確実に残し、スクリプト実行はべき等性（Idempotency）を担保すること
