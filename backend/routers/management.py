from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ..firewall import block, unblock, validate_ip
from ..persistence import Store
from ..nips_controls import set_control, status as nips_status


class Credentials(BaseModel):
    email: str
    password: str = Field(min_length=6)


class Registration(Credentials):
    username: str = Field(min_length=3)


class FirewallRequest(BaseModel):
    ip: str
    reason: str = Field(default="Manual administrator block", max_length=300)
    protocol: str = Field(default="ALL", max_length=20)


def create_management_router(store: Store) -> APIRouter:
    router = APIRouter()

    @router.post("/api/auth/register", tags=["auth"])
    def register(data: Registration):
        user = store.register(data.username, data.email, data.password)
        return {"access_token": store.token(user), "token_type": "bearer", "user": user}

    @router.post("/api/auth/login", tags=["auth"])
    def login(data: Credentials):
        user = store.login(data.email, data.password)
        return {"access_token": store.token(user), "token_type": "bearer", "user": user}

    @router.get("/api/auth/me", tags=["auth"])
    def current_user(request: Request):
        return store.require_user(request)

    @router.get("/history/sessions", tags=["history"])
    def sessions(request: Request):
        store.require_user(request)
        return store.sessions()

    @router.get("/history/alerts", tags=["history"])
    def alerts(session_id: int, request: Request):
        store.require_user(request)
        return store.alerts(session_id)

    @router.delete("/history/session", tags=["history"])
    def delete_session(session_id: int, request: Request):
        store.require_user(request)
        store.delete_session(session_id)
        return {"detail": "Session deleted."}

    @router.get("/api/firewall/blocked", tags=["firewall"])
    def blocked(request: Request):
        store.require_user(request)
        return store.blocked()

    @router.post("/api/firewall/block", tags=["firewall"])
    def block_ip(data: FirewallRequest, request: Request):
        store.require_user(request)
        try:
            ip = validate_ip(data.ip); enforced = block(ip)
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(400, str(exc)) from exc
        return store.save_block(ip, data.reason, data.protocol.upper(), enforced)

    @router.post("/api/firewall/unblock", tags=["firewall"])
    def unblock_ip(data: FirewallRequest, request: Request):
        store.require_user(request)
        try:
            ip = validate_ip(data.ip); unblock(ip)
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(400, str(exc)) from exc
        store.remove_block(ip)
        return {"status": "success", "ip": ip}

    @router.get("/api/notifications", tags=["notifications"])
    def notifications(request: Request):
        store.require_user(request)
        return store.notifications()

    @router.get("/nips/status", tags=["firewall"])
    def nips_state(request: Request):
        store.require_user(request)
        return nips_status()

    @router.post("/nips/{protocol}/{action}", tags=["firewall"])
    def nips_control(protocol: str, action: str, request: Request):
        store.require_user(request)
        if action not in {"block", "unblock"}:
            raise HTTPException(400, "Action must be block or unblock.")
        try:
            enforced = set_control(protocol, action == "block")
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(400, str(exc)) from exc
        return {"protocol": protocol, "blocked": action == "block", "enforced": enforced}

    @router.post("/api/notifications/test-alert", tags=["notifications"])
    def test_notification(request: Request):
        user = store.require_user(request)
        subject = "[SecureFlow-AI] Test security alert"
        message = "This is a test alert generated from the SecureFlow-AI firewall console."
        status = "SIMULATED"
        username, password = os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD")
        if username and password:
            try:
                email = EmailMessage(); email["Subject"] = subject; email["From"] = username; email["To"] = user["email"]
                email.set_content(message)
                with smtplib.SMTP(os.getenv("SMTP_SERVER", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", "587"))) as smtp:
                    smtp.starttls(); smtp.login(username, password); smtp.send_message(email)
                status = "SENT"
            except Exception as exc:
                status = f"FAILED: {exc}"
        store.notification(user["email"], subject, message, status)
        return {"status": status, "recipient": user["email"]}

    return router
