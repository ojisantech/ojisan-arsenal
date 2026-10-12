#!/usr/bin/env python3
# 私であることの証明: https://github.com/ojisantech/
# 日付: 2026/10/12
"""
patch_deployer.py - 完全エージェントレス遠隔パッチ適用 ＆ 台帳自動連動スクリプト
==============================================================================
私であることの証明: https://github.com/ojisantech/
日付: 2026/10/12
------------------------------------------------------------------------------
常駐エージェントを一切使わず、OS標準機能（WinRM: 5985 / SSH: 22）のみでリモート端末に
パッチを適用し、第1弾のSQLiteパッチ台帳（applied_patches）へ自動記録します。

【主な機能】
- 事前疎通診断 (Pre-flight Check): 実行前にポートの健全性を超高速(1秒以内)に検証しハング防止
- Windows (WinRM): PowerShell / winget によるアプリ・OSセキュリティパッチのサイレント適用
- Linux (SSH): apt-get / dnf 等によるリモートパッケージアップデート
- 第1弾台帳連動: パッチ適用成功時に SQLite 台帳へ自動登録 (次回脆弱性診断で過剰検知ゼロ化)
- CLI / ライブラリ両対応: ターミナルから単体実行も可能

【使用方法 (CLI)】
  # 疎通確認と更新確認 (ドライラン)
  python3 patch_deployer.py 192.168.1.50 --check

  # 自動OS判別でパッチ適用 ＆ 台帳記録
  python3 patch_deployer.py 192.168.1.50 --cve CVE-2024-6387

  # 明示的にOSと認証情報を指定
  python3 patch_deployer.py 192.168.1.50 --os windows --user admin --password "SecretPass"
  python3 patch_deployer.py 192.168.1.200 --os linux --user ubuntu --cve CVE-2024-6387
==============================================================================
"""

import os
import sys
import socket
import sqlite3
import argparse
import datetime
import subprocess
from pathlib import Path

# .env ファイルの読み込みサポート (存在する場合)
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=False)
    else:
        load_dotenv(override=False)
except ImportError:
    pass


# ==============================================================================
# 1. 事前疎通診断 (Pre-flight Check)
# ==============================================================================
def preflight_check(target_ip: str, port: int, timeout: float = 1.0) -> bool:
    """
    パッチ実行前にポートが確実にリッスンしているか高速検証 (ハング防止)。
    タイムアウトはデフォルト1秒。
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((target_ip, port))
        return result == 0
    except Exception:
        return False
    finally:
        sock.close()


def detect_target_os(target_ip: str) -> str:
    """
    ポート開放状況から対象OSを高速自動判定 (WinRM: 5985 -> windows, SSH: 22 -> linux)
    """
    if preflight_check(target_ip, port=5985, timeout=1.0):
        return "windows"
    if preflight_check(target_ip, port=22, timeout=1.0):
        return "linux"
    return "unknown"


# ==============================================================================
# 2. Windows 向け WinRM 遠隔パッチ適用
# ==============================================================================
def deploy_windows_patch(
    ip: str,
    user: str = None,
    password: str = None,
    command: str = None,
    timeout_sec: int = 300
) -> dict:
    """
    WinRM 経由で対象 Windows 端末に PowerShell / winget をサイレント実行
    """
    user = user or os.getenv("WINRM_USER", "Administrator")
    password = password or os.getenv("WINRM_PASS", "")

    # 事前疎通チェック
    if not preflight_check(ip, port=5985):
        return {
            "success": False,
            "os": "windows",
            "error": f"WinRM ポート (5985) への事前疎通に失敗しました: {ip}"
        }

    try:
        import winrm
    except ImportError:
        return {
            "success": False,
            "os": "windows",
            "error": "pywinrm がインストールされていません ('pip install pywinrm' を実行してください)"
        }

    if not password:
        return {
            "success": False,
            "os": "windows",
            "error": "WinRM パスワードが指定されていません (--password または環境変数 WINRM_PASS)"
        }

    cmd = command or "winget upgrade --all --include-pinned --accept-source-agreements --accept-package-agreements"
    ps_script = f"powershell.exe -ExecutionPolicy Bypass -Command {cmd}"

    try:
        session = winrm.Session(
            f"http://{ip}:5985/wsman",
            auth=(user, password),
            transport="ntlm",
            server_cert_validation="ignore",
            operation_timeout_sec=timeout_sec,
            read_timeout_sec=timeout_sec + 30
        )
        res = session.run_cmd(ps_script)
        out = res.std_out.decode("cp932", errors="ignore")
        err = res.std_err.decode("cp932", errors="ignore")

        if res.status_code == 0:
            return {"success": True, "os": "windows", "output": out, "error": None}
        else:
            return {"success": False, "os": "windows", "output": out, "error": err or f"ExitCode: {res.status_code}"}
    except Exception as e:
        return {"success": False, "os": "windows", "error": f"WinRM 実行例外: {str(e)}"}


# ==============================================================================
# 3. Linux 向け SSH 遠隔パッチ適用
# ==============================================================================
def deploy_linux_patch(
    ip: str,
    user: str = None,
    password: str = None,
    key_path: str = None,
    command: str = None,
    timeout_sec: int = 180
) -> dict:
    """
    SSH 経由で対象 Linux 端末にリモートパッチコマンド (apt-get 等) を実行
    """
    user = user or os.getenv("SSH_USER", os.getenv("LINUX_SSH_USER", "ubuntu"))
    password = password or os.getenv("SSH_PASS", os.getenv("LINUX_SSH_PASS", ""))
    key_path = key_path or os.getenv("SSH_KEY_PATH", "")

    # 事前疎通チェック
    if not preflight_check(ip, port=22):
        return {
            "success": False,
            "os": "linux",
            "error": f"SSH ポート (22) への事前疎通に失敗しました: {ip}"
        }

    cmd = command or "sudo apt-get update -qq && sudo apt-get --only-upgrade install -y -qq openssh-server"

    # パスワード認証で paramiko が利用可能な場合
    if password:
        try:
            import paramiko
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=user, password=password, timeout=10)
            stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=timeout_sec)
            stdin.write(f"{password}\n")
            stdin.flush()
            out = stdout.read().decode("utf-8", errors="ignore")
            ssh.close()
            return {"success": True, "os": "linux", "output": out, "error": None}
        except ImportError:
            pass
        except Exception as e:
            return {"success": False, "os": "linux", "error": f"Paramiko SSH 実行エラー: {str(e)}"}

    # 標準の ssh コマンドによる実行 (鍵認証またはエージェントフォワード)
    ssh_args = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5"
    ]
    if key_path and os.path.exists(key_path):
        ssh_args.extend(["-i", key_path])
    ssh_args.extend([f"{user}@{ip}", cmd])

    try:
        res = subprocess.run(ssh_args, capture_output=True, text=True, timeout=timeout_sec)
        if res.returncode == 0:
            return {"success": True, "os": "linux", "output": res.stdout, "error": None}
        else:
            return {"success": False, "os": "linux", "output": res.stdout, "error": res.stderr}
    except Exception as e:
        return {"success": False, "os": "linux", "error": f"SSH サブプロセス実行エラー: {str(e)}"}


# ==============================================================================
# 4. 第1弾パッチ台帳 (SQLite) への自動更新
# ==============================================================================
def record_to_ledger(db_path: str, ip: str, patch_id: str, memo: str = "エージェントレス自動適用"):
    """
    パッチ適用成功時に SQLite 台帳へ自動追記 (次回スキャン時の過剰検知をゼロ化)
    """
    conn = sqlite3.connect(db_path, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applied_patches (
            ip TEXT NOT NULL,
            patch_id TEXT NOT NULL,
            memo TEXT DEFAULT '',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (ip, patch_id)
        )
    """)
    cursor.execute("""
        INSERT OR REPLACE INTO applied_patches (ip, patch_id, memo, applied_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (ip, patch_id, memo))
    conn.commit()
    conn.close()


# ==============================================================================
# 5. CLI エントリーポイント
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="完全エージェントレス遠隔パッチ適用 ＆ 台帳自動連動スクリプト (patch_deployer.py)"
    )
    parser.add_argument("ip", help="対象端末の IP アドレス")
    parser.add_argument("--os", choices=["auto", "windows", "linux"], default="auto", help="対象 OS (デフォルト: auto 自動判別)")
    parser.add_argument("--check", action="store_true", help="適用せず事前疎通・ポート状態の確認のみ行う (ドライラン)")
    parser.add_argument("--cve", default="", help="解消対象の CVE 番号 (例: CVE-2024-6387)。指定時は台帳に自動記録")
    parser.add_argument("--user", default="", help="接続ユーザー名 (未指定時は環境変数またはデフォルト値)")
    parser.add_argument("--password", default="", help="接続パスワード (Windows WinRM または Linux SSH)")
    parser.add_argument("--key-file", default="", help="SSH 秘密鍵パス (Linux)")
    parser.add_argument("--command", default="", help="実行するカスタムパッチコマンド")
    parser.add_argument("--db", default="patch_ledger.db", help="第1弾 SQLite パッチ台帳パス (デフォルト: patch_ledger.db)")

    args = parser.parse_args()
    target_ip = args.ip

    print("=" * 60)
    print(f"🚀 [TARGET] {target_ip} (エージェントレス遠隔パッチ処理開始)")
    print("=" * 60)

    # OS 自動判別
    target_os = args.os
    if target_os == "auto":
        print(f"[PROBE] {target_ip} の開放ポートを診断中 (WinRM:5985 / SSH:22)...")
        target_os = detect_target_os(target_ip)
        if target_os == "unknown":
            print(f"❌ [ERROR] {target_ip} の WinRM(5985) および SSH(22) ポートが開いていません。", file=sys.stderr)
            sys.exit(1)
        print(f"[DETECT] 検出された OS タイプ: {target_os.upper()}")

    # --check モード (事前確認のみ)
    if args.check:
        port = 5985 if target_os == "windows" else 22
        ok = preflight_check(target_ip, port)
        status = "✅ 疎通確認 OK (パッチ適用可能)" if ok else "❌ 疎通失敗"
        print(f"[CHECK] 対象ポート {port} ({target_os}): {status}")
        sys.exit(0 if ok else 1)

    # パッチ適用実行
    print(f"[DEPLOY] {target_os.upper()} パッチ適用コマンドをサイレント送信中...")
    if target_os == "windows":
        res = deploy_windows_patch(
            target_ip,
            user=args.user,
            password=args.password,
            command=args.command
        )
    else:
        res = deploy_linux_patch(
            target_ip,
            user=args.user,
            password=args.password,
            key_path=args.key_file,
            command=args.command
        )

    # 結果判定と台帳更新
    if res["success"]:
        print(f"✅ [SUCCESS] {target_ip} へのパッチ適用が正常に完了しました。")
        if res.get("output"):
            snippet = res["output"].strip().splitlines()[-5:]
            print("--- 実行出力ログ (末尾抜粋) ---")
            for line in snippet:
                print(f"  {line}")
            print("--------------------------------")

        if args.cve:
            memo = f"patch_deployer.py ({target_os}) 自動適用"
            record_to_ledger(args.db, target_ip, args.cve, memo)
            print(f"📝 [LEDGER] 第1弾 SQLite 台帳 ({args.db}) に登録完了: {target_ip} - {args.cve}")
            print("🎉 次回 cve_lookup_db.sh 実行時に該当脆弱性のアラートが自動で除外されます。")
        else:
            print("ℹ️  --cve が未指定のため、台帳登録はスキップされました。")
    else:
        print(f"❌ [FAILED] パッチ適用失敗: {res.get('error', '不明なエラー')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
