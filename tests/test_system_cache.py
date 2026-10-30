import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from peforth import repl as _f_mod


class SystemCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache_dir = Path(self.tmp.name)
        self.cache_path = self.cache_dir / ".system_cache.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_default_shell_is_pwsh_on_windows(self):
        with patch.object(_f_mod.os, "name", "nt"), \
                patch.object(_f_mod.platform, "system", return_value="Windows"), \
                patch.dict(os.environ, {"PEFORTH_CACHE_TTL": "0"}), \
                patch.object(_f_mod, "_latest_runtime_file_info", return_value=None):
            with patch.object(_f_mod, "_pwsh_info", return_value={"available": True, "path": "pwsh.exe", "version": "7"}), \
                    patch.object(_f_mod, "_windows_wsl_info", return_value={"available": False, "distros": []}), \
                    patch.object(_f_mod, "_program_info", return_value={"available": True, "path": "bash", "version": "bash"}):
                detected = _f_mod._detect_system_info(cache_path=self.cache_path)

        self.assertEqual(detected["default_shell"], "pwsh")

    def test_default_shell_is_bash_on_wsl(self):
        with patch.dict(os.environ, {"PEFORTH_CACHE_TTL": "0", "WSL_DISTRO_NAME": "Ubuntu"}), \
                patch.object(_f_mod.platform, "release", return_value="5.15.0-microsoft-standard-WSL2"), \
                patch.object(_f_mod, "_latest_runtime_file_info", return_value=None):
            with patch.object(_f_mod, "_pwsh_info", return_value={"available": True, "path": "pwsh.exe", "version": "7"}), \
                    patch.object(_f_mod, "_program_info", return_value={"available": True, "path": "/usr/bin/bash", "version": "bash"}):
                detected = _f_mod._detect_system_info(cache_path=self.cache_path)

        self.assertEqual(detected["default_shell"], "bash")

    def test_cache_is_created_on_first_run_and_hit_on_second_run(self):
        calls = []

        def fake_program_info(name, version_args):
            calls.append(name)
            return {"available": True, "path": f"/bin/{name}", "version": "1.0.0"}

        with patch.dict(os.environ, {"PEFORTH_CACHE_TTL": "600"}):
            with patch.object(_f_mod, "_program_info", side_effect=fake_program_info):
                with patch.object(_f_mod, "_pwsh_info", return_value={"available": False, "path": None, "version": None}):
                    with patch.object(_f_mod, "_windows_wsl_info", return_value={"available": False, "distros": []}):
                        first_detected = _f_mod._detect_system_info(cache_path=self.cache_path)

        self.assertTrue(self.cache_path.exists())
        self.assertGreater(len(calls), 0)
        cache_content = json.loads(self.cache_path.read_text(encoding="utf-8"))
        self.assertEqual(cache_content["schema_version"], 1)
        self.assertIn("shells", cache_content)
        self.assertIn("wsl", cache_content)

        # Second run should hit cache and make 0 probe calls
        calls.clear()
        with patch.dict(os.environ, {"PEFORTH_CACHE_TTL": "600"}):
            with patch.object(_f_mod, "_program_info", side_effect=fake_program_info):
                with patch.object(_f_mod, "_pwsh_info", side_effect=lambda *args: (_ for _ in ()).throw(AssertionError("pwsh probed"))):
                    second_detected = _f_mod._detect_system_info(cache_path=self.cache_path)

        self.assertEqual(len(calls), 0)
        self.assertEqual(first_detected["shells"], second_detected["shells"])

    def test_cache_ttl_expiry_triggers_refresh(self):
        calls = []

        def fake_program_info(name, version_args):
            calls.append(name)
            return {"available": True, "path": f"/bin/{name}", "version": "1.0.0"}

        with patch.dict(os.environ, {"PEFORTH_CACHE_TTL": "100"}):
            with patch.object(_f_mod, "_program_info", side_effect=fake_program_info):
                with patch.object(_f_mod, "_pwsh_info", return_value={"available": False, "path": None, "version": None}):
                    with patch.object(_f_mod, "_windows_wsl_info", return_value={"available": False, "distros": []}):
                        _f_mod._detect_system_info(cache_path=self.cache_path)

        self.assertTrue(self.cache_path.exists())
        calls.clear()

        # Set mtime back by 200 seconds (TTL is 100)
        old_time = time.time() - 200
        os.utime(self.cache_path, (old_time, old_time))

        with patch.dict(os.environ, {"PEFORTH_CACHE_TTL": "100"}):
            with patch.object(_f_mod, "_program_info", side_effect=fake_program_info):
                with patch.object(_f_mod, "_pwsh_info", return_value={"available": False, "path": None, "version": None}):
                    with patch.object(_f_mod, "_windows_wsl_info", return_value={"available": False, "distros": []}):
                        _f_mod._detect_system_info(cache_path=self.cache_path)

        # Probing should have been re-triggered because cache was expired
        self.assertGreater(len(calls), 0)

    def test_cache_fingerprint_change_triggers_refresh(self):
        calls = []

        def fake_program_info(name, version_args):
            calls.append(name)
            return {"available": True, "path": f"/bin/{name}", "version": "1.0.0"}

        with patch.dict(os.environ, {"PEFORTH_CACHE_TTL": "600", "PEFORTH_PWSH_PATH": ""}):
            with patch.object(_f_mod, "_program_info", side_effect=fake_program_info):
                with patch.object(_f_mod, "_pwsh_info", return_value={"available": False, "path": None, "version": None}):
                    with patch.object(_f_mod, "_windows_wsl_info", return_value={"available": False, "distros": []}):
                        _f_mod._detect_system_info(cache_path=self.cache_path)

        calls.clear()

        # Change PEFORTH_PWSH_PATH -> fingerprint mismatch -> re-probe
        with patch.dict(os.environ, {"PEFORTH_CACHE_TTL": "600", "PEFORTH_PWSH_PATH": "/custom/pwsh.exe"}):
            with patch.object(_f_mod, "_program_info", side_effect=fake_program_info):
                with patch.object(_f_mod, "_pwsh_info", return_value={"available": True, "path": "/custom/pwsh.exe", "version": "7.5"}):
                    with patch.object(_f_mod, "_windows_wsl_info", return_value={"available": False, "distros": []}):
                        detected = _f_mod._detect_system_info(cache_path=self.cache_path)

        self.assertGreater(len(calls), 0)
        cache_content = json.loads(self.cache_path.read_text(encoding="utf-8"))
        self.assertEqual(cache_content["config_fingerprint"]["PEFORTH_PWSH_PATH"], "/custom/pwsh.exe")

    def test_manual_cache_delete_triggers_recreation(self):
        calls = []

        def fake_program_info(name, version_args):
            calls.append(name)
            return {"available": True, "path": f"/bin/{name}", "version": "1.0.0"}

        with patch.dict(os.environ, {"PEFORTH_CACHE_TTL": "600"}):
            with patch.object(_f_mod, "_program_info", side_effect=fake_program_info):
                with patch.object(_f_mod, "_pwsh_info", return_value={"available": False, "path": None, "version": None}):
                    with patch.object(_f_mod, "_windows_wsl_info", return_value={"available": False, "distros": []}):
                        _f_mod._detect_system_info(cache_path=self.cache_path)

        self.assertTrue(self.cache_path.exists())

        # Manually delete cache file
        self.cache_path.unlink()
        self.assertFalse(self.cache_path.exists())
        calls.clear()

        with patch.dict(os.environ, {"PEFORTH_CACHE_TTL": "600"}):
            with patch.object(_f_mod, "_program_info", side_effect=fake_program_info):
                with patch.object(_f_mod, "_pwsh_info", return_value={"available": False, "path": None, "version": None}):
                    with patch.object(_f_mod, "_windows_wsl_info", return_value={"available": False, "distros": []}):
                        _f_mod._detect_system_info(cache_path=self.cache_path)

        self.assertTrue(self.cache_path.exists())
        self.assertGreater(len(calls), 0)

    def test_corrupted_cache_file_falls_back_gracefully(self):
        # Write corrupted JSON content
        self.cache_path.write_text("{ broken json content ...", encoding="utf-8")
        calls = []

        def fake_program_info(name, version_args):
            calls.append(name)
            return {"available": True, "path": f"/bin/{name}", "version": "1.0.0"}

        with patch.dict(os.environ, {"PEFORTH_CACHE_TTL": "600"}):
            with patch.object(_f_mod, "_program_info", side_effect=fake_program_info):
                with patch.object(_f_mod, "_pwsh_info", return_value={"available": False, "path": None, "version": None}):
                    with patch.object(_f_mod, "_windows_wsl_info", return_value={"available": False, "distros": []}):
                        detected = _f_mod._detect_system_info(cache_path=self.cache_path)

        self.assertIn("shells", detected)
        # Should have regenerated a valid JSON file
        recovered = json.loads(self.cache_path.read_text(encoding="utf-8"))
        self.assertEqual(recovered["schema_version"], 1)

    def test_ttl_zero_disables_cache(self):
        calls = []

        def fake_program_info(name, version_args):
            calls.append(name)
            return {"available": True, "path": f"/bin/{name}", "version": "1.0.0"}

        with patch.dict(os.environ, {"PEFORTH_CACHE_TTL": "0"}):
            with patch.object(_f_mod, "_program_info", side_effect=fake_program_info):
                with patch.object(_f_mod, "_pwsh_info", return_value={"available": False, "path": None, "version": None}):
                    with patch.object(_f_mod, "_windows_wsl_info", return_value={"available": False, "distros": []}):
                        _f_mod._detect_system_info(cache_path=self.cache_path)

        # Cache file should not have been created
        self.assertFalse(self.cache_path.exists())


if __name__ == "__main__":
    unittest.main()
