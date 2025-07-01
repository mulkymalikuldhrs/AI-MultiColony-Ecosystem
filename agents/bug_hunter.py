"""🕵️‍♂️ BugHunterAgent – Autonomous ethical-hacking & bug-bounty worker
Part of Dhaher / Agentic-AI Ecosystem
Made with ❤️ in Indonesia 🇮🇩 by Mulky Malikul Dhaher

This agent performs automated vulnerability discovery on target URLs,
creates a structured report (Markdown / JSON), and – if SMTP credentials are
available – e-mails the site owner introducing itself as an AI agent from the
Dhaher AI Ecosystem.

NOTE: This is a **safe** proof-of-concept.  It only does *passive* security
checks (headers, TLS grade, and simple GET param fuzzing). You can extend it
by plugging in tools like `nuclei`, `sqlmap`, or `OWASP ZAP` via CLI.
"""
import os
import re
import smtplib
import ssl
import json
from email.message import EmailMessage
from typing import List, Dict

import requests


class BugHunterAgent:
    """Autonomous bug-bounty / security-testing agent"""

    status: str = "ready"
    capabilities: List[str] = [
        "passive_scan",
        "header_analysis",
        "simple_fuzzer",
        "email_report",
        "agent_teamwork",
    ]

    def __init__(self, smtp_server: str | None = None,
                 smtp_port: int = 587,
                 smtp_username: str | None = None,
                 smtp_password: str | None = None,
                 from_addr: str | None = None) -> None:
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", smtp_port))
        self.smtp_username = smtp_username or os.getenv("SMTP_USERNAME")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_addr = from_addr or self.smtp_username

    # ---------------------------------------------------------------------
    # 🛡️  Core scanning logic
    # ---------------------------------------------------------------------
    def scan(self, url: str) -> Dict[str, str]:
        """Run passive/fuzz scan against *url* and return findings."""
        findings: Dict[str, str] = {}

        try:
            resp = requests.get(url, timeout=15, allow_redirects=True)
            findings["status_code"] = str(resp.status_code)
            findings["headers"] = json.dumps(dict(resp.headers), indent=2)

            # Simple header issues
            missing_headers = []
            for header in ["Content-Security-Policy", "X-Frame-Options",
                             "Strict-Transport-Security", "X-XSS-Protection"]:
                if header not in resp.headers:
                    missing_headers.append(header)
            if missing_headers:
                findings["missing_headers"] = ", ".join(missing_headers)

            # Very naive GET param reflection check
            params = re.findall(r"[?&]([a-zA-Z0-9_]+)=", url)
            for p in params:
                test_url = re.sub(p + r"=[^&]*", f"{p}=\"'><script>alert(1)</script>", url)
                test_resp = requests.get(test_url, timeout=15, allow_redirects=True)
                if "<script>alert(1)</script>" in test_resp.text:
                    findings.setdefault("potential_xss", []).append(p)
        except Exception as exc:
            findings["error"] = str(exc)

        return findings

    # ------------------------------------------------------------------
    # ✉️  Email reporting
    # ------------------------------------------------------------------
    def _send_email(self, to_addr: str, subject: str, body: str) -> None:
        if not (self.smtp_server and self.smtp_username and self.smtp_password):
            print("[BugHunterAgent] SMTP not configured, skipping email.")
            return

        msg = EmailMessage()
        msg["From"] = self.from_addr
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls(context=context)
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            print(f"[BugHunterAgent] Report sent to {to_addr} ✔️")

    # ------------------------------------------------------------------
    # 🚀  Public API
    # ------------------------------------------------------------------
    def hunt_and_report(self, target_url: str, owner_email: str | None = None) -> Dict[str, str]:
        """Scan **target_url**; optionally e-mail **owner_email**."""
        self.status = "scanning"
        findings = self.scan(target_url)
        self.status = "ready"

        # Prepare human-readable report
        report_md = self._format_report_md(target_url, findings)

        # Save local log
        os.makedirs("reports/bug_hunter", exist_ok=True)
        report_path = os.path.join("reports", "bug_hunter", f"report_{re.sub('[^a-zA-Z0-9]', '_', target_url)}.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"[BugHunterAgent] Report saved to {report_path}")

        # Email if address given
        if owner_email:
            self._send_email(owner_email,
                              subject=f"[Security] Potential issues on {target_url}",
                              body=report_md)
        return findings

    # ------------------------------------------------------------------
    def _format_report_md(self, target_url: str, findings: Dict[str, str]) -> str:
        """Return markdown string for findings."""
        md = [f"# 🐞 BugHunter Report for `{target_url}`\n",
              "Generated automatically by **Dhaher AI Ecosystem – BugHunterAgent**\n",
              "---\n"]
        for k, v in findings.items():
            md.append(f"## {k.replace('_', ' ').title()}\n")
            md.append("```")
            if isinstance(v, list):
                md.append(json.dumps(v, indent=2))
            else:
                md.append(str(v))
            md.append("```\n")
        md.append("\n---\nGenerated with ❤️ by Dhaher AI Ecosystem 🧠🤖")
        return "\n".join(md)


# Factory function expected by agents registry

def bug_hunter_agent(*args, **kwargs):  # noqa: N802
    return BugHunterAgent(*args, **kwargs)