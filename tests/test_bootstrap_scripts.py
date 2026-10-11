import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BootstrapScriptTests(unittest.TestCase):
    def test_wsl_bootstrap_refuses_unexpected_remote_without_writes(self):
        with tempfile.TemporaryDirectory(prefix="peforth-bootstrap-") as directory:
            fixture = Path(directory)
            (fixture / "peforth").mkdir()
            (fixture / "pyproject.toml").write_text("[build-system]\n", encoding="utf-8")
            (fixture / "peforth" / "repl.py").write_text("", encoding="utf-8")
            (fixture / "bin").mkdir()
            fake_git = fixture / "bin" / "git"
            fake_git.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' https://example.invalid/not-peforth.git\n"
                "exit 0\n",
                encoding="utf-8",
            )
            fake_git.chmod(0o755)
            result = subprocess.run(
                ["bash", str(ROOT / "bootstrap.sh")],
                cwd=fixture,
                text=True,
                capture_output=True,
                check=False,
                env={"PATH": f"{fixture / 'bin'}:/usr/bin:/bin", "HOME": str(fixture / "home")},
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("Unexpected origin remote", result.stderr)
            self.assertFalse((fixture / ".venv").exists())
            self.assertFalse((fixture / "home").exists())

    def test_windows_bootstrap_parses_and_refuses_in_wsl_checkout(self):
        script_win = subprocess.run(
            ["wslpath", "-w", str(ROOT / "bootstrap.ps1")],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        temp_root = Path("/mnt/c/Users/8304018/AppData/Local/Temp")
        with tempfile.TemporaryDirectory(prefix="peforth-ps-", dir=temp_root) as directory:
            probe_path = Path(directory) / "probe.ps1"
            probe_win = subprocess.run(
                ["wslpath", "-w", str(probe_path)],
                check=True,
                text=True,
                capture_output=True,
            ).stdout.strip()
            probe_path.write_text(
                "$tokens = $null\n"
                "$errors = $null\n"
                f"$target = '{script_win}'\n"
                "[System.Management.Automation.Language.Parser]::ParseFile(\n"
                "    $target, [ref]$tokens, [ref]$errors) | Out-Null\n"
                "if ($errors.Count) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }\n"
                f"& '{script_win}'\n"
                "exit $LASTEXITCODE\n",
                encoding="utf-8",
            )
            probe = subprocess.run(
                ["pwsh.exe", "-NoLogo", "-NoProfile", "-File", probe_win],
                cwd=ROOT,
                capture_output=True,
                check=False,
            )
        diagnostic = (probe.stdout + probe.stderr).decode("utf-8", "replace")
        self.assertEqual(probe.returncode, 1, diagnostic)
        self.assertIn("Unexpected origin remote", diagnostic)


if __name__ == "__main__":
    unittest.main()
