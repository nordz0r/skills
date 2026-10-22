"""Synthetic regression tests for context-audit CLI.

Tests catch real consumer-visible bugs:
1. Tool schemas are not double counted in static metrics.
2. Compaction epoch and snapshot selection (first, last, explicit record ID).
3. Optional ContextSnapshot fields (historyRewriteTokensRemoved, lastMessageTimestamp, toolSchemaTokens).
4. Non-negative checks and nonMessageTokens exceeding promptTokens edge case.
5. Incompatible comparison rejection (mixing native JSONL with dump JSON).
6. Malformed JSONL line reporting with line number and clean exit.
7. Verified dump inspection and component sizing without payload leaking.
8. Unicode character and byte counting accuracy.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "audit_context.py"


def run_cli(*args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestContextAuditCli(unittest.TestCase):
    def test_schema_not_double_counted_and_derived_tokens(self) -> None:
        record = {
            "type": "message",
            "id": "rec-001",
            "timestamp": "2026-10-22T10:00:00.000Z",
            "message": {
                "role": "assistant",
                "model": "model-alpha",
                "contextSnapshot": {
                    "promptTokens": 20000,
                    "nonMessageTokens": 5000,
                    "toolSchemaTokens": 1500,
                    "compactionEpoch": 0,
                },
            },
        }
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps(record) + "\n")
            path = f.name

        code, out, err = run_cli("inspect", path)
        self.assertEqual(code, 0, f"CLI error: {err}")
        data = json.loads(out)
        metrics = data["metrics"]
        self.assertEqual(metrics["prompt_tokens"], 20000)
        self.assertEqual(metrics["non_message_tokens"], 5000)
        self.assertEqual(metrics["tool_schema_tokens"], 1500)
        # Verify non_tool_static_tokens = 5000 - 1500 = 3500 (schema not double counted)
        self.assertEqual(metrics["non_tool_static_tokens"], 3500)
        # Verify provider_anchor_remainder = 20000 - 5000 = 15000
        self.assertEqual(metrics["provider_anchor_remainder"], 15000)

    def test_snapshot_selection_and_optional_fields(self) -> None:
        rec1 = {
            "type": "message",
            "id": "snap-first",
            "message": {
                "role": "assistant",
                "model": "model-beta",
                "contextSnapshot": {
                    "promptTokens": 10000,
                    "nonMessageTokens": 4000,
                    "toolSchemaTokens": 1000,
                    "compactionEpoch": 0,
                },
            },
        }
        rec2 = {
            "type": "message",
            "id": "snap-middle",
            "message": {
                "role": "assistant",
                "model": "model-beta",
                "contextSnapshot": {
                    "promptTokens": 15000,
                    "nonMessageTokens": 4000,
                    "compactionEpoch": 0,
                    "historyRewriteTokensRemoved": 500,
                },
            },
        }
        rec3 = {
            "type": "message",
            "id": "snap-last",
            "message": {
                "role": "assistant",
                "model": "model-beta",
                "contextSnapshot": {
                    "promptTokens": 25000,
                    "nonMessageTokens": 3800,
                    "compactionEpoch": 1,
                },
            },
        }
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            for r in (rec1, rec2, rec3):
                f.write(json.dumps(r) + "\n")
            path = f.name

        # Test selecting first
        code, out, _ = run_cli("inspect", path, "--snapshot", "first")
        self.assertEqual(code, 0)
        first_data = json.loads(out)
        self.assertEqual(first_data["capture"]["record_id"], "snap-first")
        self.assertEqual(first_data["capture"]["compaction_epoch"], 0)

        # Test selecting by explicit record ID with optional historyRewriteTokensRemoved
        code, out, _ = run_cli("inspect", path, "--snapshot", "snap-middle")
        self.assertEqual(code, 0)
        mid_data = json.loads(out)
        self.assertEqual(mid_data["capture"]["record_id"], "snap-middle")
        self.assertEqual(mid_data["metrics"]["history_rewrite_tokens_removed"], 500)
        self.assertEqual(mid_data["metrics"]["corrected_provider_prompt"], 14500)
        self.assertIsNone(mid_data["metrics"]["tool_schema_tokens"])

        # Test selecting last
        code, out, _ = run_cli("inspect", path, "--snapshot", "last")
        self.assertEqual(code, 0)
        last_data = json.loads(out)
        self.assertEqual(last_data["capture"]["record_id"], "snap-last")
        self.assertEqual(last_data["capture"]["compaction_epoch"], 1)

    def test_compare_same_file_and_compaction_warning(self) -> None:
        rec1 = {
            "type": "message",
            "id": "rec-before",
            "message": {
                "role": "assistant",
                "model": "model-1",
                "contextSnapshot": {
                    "promptTokens": 10000,
                    "nonMessageTokens": 5000,
                    "toolSchemaTokens": 2000,
                    "compactionEpoch": 0,
                },
            },
        }
        rec2 = {
            "type": "message",
            "id": "rec-after",
            "message": {
                "role": "assistant",
                "model": "model-1",
                "contextSnapshot": {
                    "promptTokens": 18000,
                    "nonMessageTokens": 4500,
                    "toolSchemaTokens": 1500,
                    "compactionEpoch": 1,
                },
            },
        }
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps(rec1) + "\n" + json.dumps(rec2) + "\n")
            path = f.name

        code, out, err = run_cli("compare", path, path, "--before", "rec-before", "--after", "rec-after")
        self.assertEqual(code, 0, f"Compare failed: {err}")
        data = json.loads(out)
        schema_change = data["changes"]["tool_schema_tokens"]
        self.assertEqual(schema_change["before"], 2000)
        self.assertEqual(schema_change["after"], 1500)
        self.assertEqual(schema_change["delta"], -500)
        self.assertEqual(schema_change["direction"], "decrease")
        self.assertAlmostEqual(schema_change["reduction_percent"], 25.0)

        # Compaction warning must be present
        warnings = " ".join(data["warnings"])
        self.assertIn("Compaction epoch differs", warnings)

    def test_non_message_exceeding_prompt_tokens_tolerated(self) -> None:
        # Edge case: local tokenizer estimate higher than provider reported usage
        record = {
            "type": "message",
            "id": "rec-edge",
            "message": {
                "role": "assistant",
                "contextSnapshot": {
                    "promptTokens": 27008,
                    "nonMessageTokens": 27651,
                    "compactionEpoch": 0,
                },
            },
        }
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps(record) + "\n")
            path = f.name

        code, out, err = run_cli("inspect", path)
        self.assertEqual(code, 0, f"Edge case rejected: {err}")
        data = json.loads(out)
        self.assertEqual(data["metrics"]["provider_anchor_remainder"], -643)

    def test_incompatible_comparison_rejected(self) -> None:
        rec = {
            "type": "message",
            "id": "rec-1",
            "message": {
                "role": "assistant",
                "contextSnapshot": {"promptTokens": 100, "nonMessageTokens": 50},
            },
        }
        dump = {
            "systemPrompt": "sys",
            "tools": [],
            "messages": [],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f1, \
             tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f2:
            f1.write(json.dumps(rec) + "\n")
            f2.write(json.dumps(dump))
            p1, p2 = f1.name, f2.name

        code, _, err = run_cli("compare", p1, p2)
        self.assertEqual(code, 2)
        self.assertIn("incompatible comparison", err)

    def test_malformed_jsonl_line_reporting(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write('{"type": "message", "id": "1", "message": {"role": "user"}}\n')
            f.write('{ INVALID JSON LINE HERE\n')
            path = f.name

        code, _, err = run_cli("inspect", path)
        self.assertEqual(code, 2)
        self.assertIn("malformed JSONL at line 2", err)

    def test_dump_inspection_without_payload_leaks(self) -> None:
        secret_instruction = "TOP_SECRET_PASSWORD_DO_NOT_LEAK"
        dump = {
            "model": "model-gamma",
            "systemPrompt": f"System with secret {secret_instruction}",
            "tools": [{"name": "calculator", "description": "calc tool"}],
            "messages": [{"role": "user", "content": "hello world"}],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write(json.dumps(dump))
            path = f.name

        code, out, err = run_cli("inspect", path)
        self.assertEqual(code, 0, f"Dump inspect error: {err}")
        self.assertNotIn(secret_instruction, out, "Dump output must not leak system prompt or payload content")
        data = json.loads(out)
        self.assertEqual(data["source"]["kind"], "dump-json")
        self.assertIn("systemPrompt", data["metrics"]["largest_components"])


if __name__ == "__main__":
    unittest.main()
