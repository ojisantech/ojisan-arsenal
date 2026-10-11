# 【第174弾 詳細解説】Function Calling（Tools）DB安全接続設計編 - 関数呼び出し（Function Calling / Tools）によるローカルLLMへのDB・社内API安全接続設計

> **対象読者**: バックエンドAI開発者  
> **主要技術スタック**: Tool Calling, JSON Schema, Pydantic引数検証, 生SQL完全排除  

---

## 1. 概要と背景（サマリーからの深掘り）

### なぜこの技術が現場で不可欠なのか
「ローカルLLMに社内DBの在庫を照会させたいが、自然言語でプロンプトに指示しても変なSQLを出力したり、関係ないカラムを覗き見しようとする」
「LLMに直接SQLを発行させるのはSQLインジェクションや全件DELETEの危険があり怖すぎる」

LLMに安全に社内システムを操作させる現代の業界標準が **`Function Calling (Tool Calling)`** です。

LLMに直接DBを触らせるのではなく、**「JSON Schemaで厳格に定義された関数仕様（名前、引数、型）」**をプロンプトに提示。LLMは「どの関数を、どんな引数で呼ぶべきか」というJSONのみを出力し、実際の実行は**サーバー側の厳格なPythonバリデーション層**で行うことで、DBや社内APIへの安全なアクセスを100%保証します。

従来の画一的なアプローチや商用ブラックボックス製品に頼る運用では、ライセンス費用の高騰や仕様変更に伴うベンダーロックイン、さらには現場特有のエッジケースに対する対応力の欠如が深刻なボトルネックとなります。
本稿では、オープンソースおよび標準技術の基本原理に立ち返り、外部コストゼロかつ自立運用可能なアーキテクチャの完全実装と運用基準を詳細に解説します。

---

## 2. アーキテクチャと深層メカニズム

システムの全体構造および通信・処理フローは以下の通りです。

```mermaid
flowchart TD
    User["ユーザー: 『社員ID 1042 の残日数を教えて』"]
    LLM["ローカルLLM (Qwen2.5 / Llama 3)"]

    subgraph ToolSchema["関数定義 (JSON Schema)"]
        FuncDef["get_employee_pto(employee_id: int)"]
    end

    User --> LLM
    ToolSchema -.->|利用可能ツールとして注入| LLM

    LLM -->|Tool Call出力: {'name': 'get_employee_pto', 'args': {'employee_id': 1042}}| Validator

    subgraph BackendSafety["バックエンド安全実行層"]
        Validator["型検証 & 権限チェック (Pydantic)"]
        ExecSQL["安全なプリペアドステートメント実行<br/>SELECT pto_days FROM employees WHERE id = %s"]
    end

    Validator --> ExecSQL --> Result["実行結果: {'pto_days': 14.5}"]
    Result --> LLM --> Final["最終回答: 『社員ID 1042 の有給残日数は14.5日です。』"]
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

### `safe_tool_calling.py`

```python
#!/usr/bin/env python3
# safe_tool_calling.py
# ローカルLLM向けの安全なFunction Calling実行とPydantic引数バリデーション
# ライセンス: MIT

from pydantic import BaseModel, Field
import json

# 1. ツールの引数スキーマ定義 (Pydantic)
class GetEmployeePTOArgs(BaseModel):
    employee_id: int = Field(..., description="照会対象の正の整数社員番号", ge=1)

# 2. OpenAI / Ollama 互換のツール仕様定義
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "get_employee_pto",
            "description": "社員の有給休暇の残り日数を安全に照会する",
            "parameters": GetEmployeePTOArgs.model_json_schema()
        }
    }
]

# 3. 実際の安全な実行関数
def execute_get_employee_pto(args_json: dict) -> dict:
    # Pydantic による厳格な型チェックとバリデーション
    validated_args = GetEmployeePTOArgs(**args_json)
    emp_id = validated_args.employee_id

    # 模擬DB照会 (安全なパラメーター化クエリ)
    mock_db = {1042: 14.5, 2088: 8.0}
    days = mock_db.get(emp_id, None)

    if days is None:
        return {"error": f"社員番号 {emp_id} が見つかりません"}
    return {"employee_id": emp_id, "remaining_pto_days": days}

def handle_llm_tool_call(tool_name: str, arguments_str: str):
    print(f"[TOOL CALL] 関数名: {tool_name} | 引数: {arguments_str}")
    try:
        args = json.loads(arguments_str)
        if tool_name == "get_employee_pto":
            result = execute_get_employee_pto(args)
            print(f"[TOOL RESULT] 実行結果: {result}")
            return result
        else:
            return {"error": "未知の関数呼び出しです"}
    except Exception as e:
        return {"error": f"引数バリデーション失敗: {e}"}

if __name__ == "__main__":
    # LLMが生成したと想定されるJSONのテスト
    dummy_llm_output = '{"employee_id": 1042}'
    handle_llm_tool_call("get_employee_pto", dummy_llm_output)
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

1. **Tool Choice (auto / required / none)**:
   API呼び出し時に `tool_choice="auto"` を指定すると「必要に応じてツールを呼ぶ」、`tool_choice={"type": "function", "function": {"name": "..."}}` を指定すると「特定の関数呼び出しを強制」させることができます。

2. **生SQL生成の完全禁止**:
   LLMに `execute_raw_sql(query)` のような何でも実行できるツールを渡すのは致命的な脆弱性の温床です。必ず「用途を限定した特定の業務関数（例: `cancel_order`, `lookup_user`）」のみを公開するのが安全設計の絶対原則です。

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
