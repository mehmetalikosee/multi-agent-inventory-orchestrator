"""Mock SMTP tool for sending supplier emails and alerts."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from config import get_settings

logger = logging.getLogger(__name__)


class SendEmailInput(BaseModel):
    """Input schema for sending an email."""

    to_email: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body (plain text)")
    reply_to: Optional[str] = Field(default=None, description="Optional reply-to address")


class SupplierCommunicationTool(BaseTool):
    """
    Send automated emails to suppliers (e.g. reorder alerts). Uses real SMTP when
    configured; otherwise logs the email (mock mode).
    """

    name: str = "supplier_communication"
    description: str = (
        "Send an email to a supplier. Input: JSON with to_email, subject, and body. "
        "Use for reorder requests, alerts, or notifications. In mock mode, "
        "the email is logged but not sent."
    )

    def _run(self, raw_input: str, **kwargs: Any) -> str:
        """Send email (or log in mock mode). Parses JSON or key=value from raw_input."""
        to_email, subject, body, reply_to = self._parse_input(raw_input)
        return self._send(to_email, subject, body, reply_to)

    def _send(
        self,
        to_email: str,
        subject: str,
        body: str,
        reply_to: Optional[str] = None,
    ) -> str:
        settings = get_settings()
        if settings.smtp_mock_mode:
            logger.info(
                "[MOCK SMTP] To=%s Subject=%s Body=%s",
                to_email,
                subject,
                body[:200] + "..." if len(body) > 200 else body,
            )
            return '{"status": "mock_sent", "message": "Email logged (mock mode)"}'
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.smtp_user or "noreply@orchestrator.local"
            msg["To"] = to_email
            if reply_to:
                msg["Reply-To"] = reply_to
            msg.attach(MIMEText(body, "plain"))
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(
                    msg["From"],
                    to_email,
                    msg.as_string(),
                )
            logger.info("Email sent to %s: %s", to_email, subject)
            return '{"status": "sent", "to": "' + to_email + '"}'
        except Exception as e:
            logger.exception("Failed to send email to %s: %s", to_email, e)
            return f'{{"status": "error", "message": "{e!s}"}}'

    def _parse_input(self, raw: str) -> tuple[str, str, str, Optional[str]]:
        """Parse JSON or key=value input into to_email, subject, body, reply_to."""
        import json
        raw = raw.strip()
        if raw.startswith("{"):
            data = json.loads(raw)
            return (
                data.get("to_email", ""),
                data.get("subject", ""),
                data.get("body", ""),
                data.get("reply_to"),
            )
        to_email = subject = body = ""
        reply_to: Optional[str] = None
        for part in raw.split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
                k, v = k.strip().lower(), v.strip()
                if k == "to_email":
                    to_email = v
                elif k == "subject":
                    subject = v
                elif k == "body":
                    body = v
                elif k == "reply_to":
                    reply_to = v
        return to_email, subject, body, reply_to

    def invoke(self, input: str | dict[str, Any], **kwargs: Any) -> str:
        """Handle both string (JSON) and dict input."""
        if isinstance(input, dict):
            return self._send(
                input.get("to_email", ""),
                input.get("subject", ""),
                input.get("body", ""),
                input.get("reply_to"),
            )
        to_email, subject, body, reply_to = self._parse_input(input)
        return self._send(to_email, subject, body, reply_to)

    async def _arun(self, *args: Any, **kwargs: Any) -> str:
        """Async: delegate to sync."""
        return self._run(*args, **kwargs)
