"""PostgreSQL-backed history, user, notification, and firewall-rule storage.

SQLite is retained only as a local-development fallback when DATABASE_URL is absent.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException, Request


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class Store:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.database_url = os.getenv("DATABASE_URL", "").strip()
        self.uses_postgres = bool(self.database_url)
        if not self.uses_postgres:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.secret = os.getenv("AUTH_SECRET", "change-this-development-secret").encode()
        self._initialize()

    def connection(self):
        if self.uses_postgres:
            try:
                import psycopg
                from psycopg.rows import dict_row
            except ImportError as exc:
                raise RuntimeError("PostgreSQL is configured but psycopg is not installed. Run pip install -r requirements.txt.") from exc
            return PostgresConnection(psycopg.connect(self.database_url, row_factory=dict_row))
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        if self.uses_postgres:
            with self.connection() as db:
                db.executescript("""
                    CREATE TABLE IF NOT EXISTS users (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, username TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS analysis_sessions (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, filename TEXT NOT NULL, created_at TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS alert_history (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, session_id BIGINT NOT NULL REFERENCES analysis_sessions(id), timestamp TEXT, source_ip TEXT, detection_method TEXT, predicted_intrusion_type TEXT, traffic_status TEXT, reason TEXT, severity TEXT);
                    CREATE TABLE IF NOT EXISTS blocked_ips (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, ip TEXT UNIQUE NOT NULL, reason TEXT NOT NULL, protocol TEXT NOT NULL, blocked_at TEXT NOT NULL, status TEXT NOT NULL, enforced BOOLEAN NOT NULL DEFAULT FALSE);
                    CREATE TABLE IF NOT EXISTS notifications (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, recipient TEXT NOT NULL, subject TEXT NOT NULL, message TEXT NOT NULL, status TEXT NOT NULL, timestamp TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS uploaded_files (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, session_id BIGINT NOT NULL REFERENCES analysis_sessions(id), filename TEXT NOT NULL, content BYTEA NOT NULL, content_type TEXT, size_bytes BIGINT NOT NULL, uploaded_at TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS capture_records (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, session_id BIGINT NOT NULL REFERENCES analysis_sessions(id), capture_file TEXT, flow_csv TEXT, capture_data BYTEA, flow_data BYTEA, recorded_at TEXT NOT NULL);
                    ALTER TABLE capture_records ADD COLUMN IF NOT EXISTS capture_data BYTEA;
                    ALTER TABLE capture_records ADD COLUMN IF NOT EXISTS flow_data BYTEA;
                """)
            return
        with self.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                  id INTEGER PRIMARY KEY, username TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS analysis_sessions (
                  id INTEGER PRIMARY KEY, filename TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS alert_history (
                  id INTEGER PRIMARY KEY, session_id INTEGER NOT NULL, timestamp TEXT,
                  source_ip TEXT, detection_method TEXT, predicted_intrusion_type TEXT,
                  traffic_status TEXT, reason TEXT, severity TEXT,
                  FOREIGN KEY(session_id) REFERENCES analysis_sessions(id)
                );
                CREATE TABLE IF NOT EXISTS blocked_ips (
                  id INTEGER PRIMARY KEY, ip TEXT UNIQUE NOT NULL, reason TEXT NOT NULL,
                  protocol TEXT NOT NULL, blocked_at TEXT NOT NULL, status TEXT NOT NULL,
                  enforced INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS notifications (
                  id INTEGER PRIMARY KEY, recipient TEXT NOT NULL, subject TEXT NOT NULL,
                  message TEXT NOT NULL, status TEXT NOT NULL, timestamp TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS uploaded_files (
                  id INTEGER PRIMARY KEY, session_id INTEGER NOT NULL, filename TEXT NOT NULL,
                  content BLOB NOT NULL, content_type TEXT, size_bytes INTEGER NOT NULL, uploaded_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS capture_records (
                  id INTEGER PRIMARY KEY, session_id INTEGER NOT NULL, capture_file TEXT,
                  flow_csv TEXT, capture_data BLOB, flow_data BLOB, recorded_at TEXT NOT NULL
                );
            """)

    @staticmethod
    def password_hash(password: str, salt: str | None = None) -> str:
        salt = salt or secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 310_000).hex()
        return f"{salt}${digest}"

    def verify_password(self, password: str, encoded: str) -> bool:
        salt, _, expected = encoded.partition("$")
        return bool(salt and hmac.compare_digest(self.password_hash(password, salt), encoded))

    def register(self, username: str, email: str, password: str) -> dict[str, str]:
        if len(username.strip()) < 3 or len(password) < 6:
            raise HTTPException(422, "Username must have 3 characters and password must have 6 characters.")
        try:
            with self.connection() as db:
                db.execute("INSERT INTO users(username,email,password_hash,created_at) VALUES(?,?,?,?)",
                           (username.strip(), email.lower().strip(), self.password_hash(password), now()))
        except Exception as exc:
            raise HTTPException(409, "Email already registered.") from exc
        return {"username": username.strip(), "email": email.lower().strip()}

    def login(self, email: str, password: str) -> dict[str, str]:
        with self.connection() as db:
            row = db.execute("SELECT username,email,password_hash FROM users WHERE email=?", (email.lower().strip(),)).fetchone()
        if not row or not self.verify_password(password, row["password_hash"]):
            raise HTTPException(401, "Invalid email or password.")
        return {"username": row["username"], "email": row["email"]}

    def token(self, user: dict[str, str]) -> str:
        payload = f"{user['email']}|{user['username']}|{secrets.token_urlsafe(24)}"
        signature = hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
        return f"{payload}.{signature}"

    def require_user(self, request: Request) -> dict[str, str]:
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            raise HTTPException(401, "Authentication required.")
        token = header[7:]
        payload, separator, signature = token.rpartition(".")
        expected = hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
        if not separator or not hmac.compare_digest(signature, expected):
            raise HTTPException(401, "Invalid authentication token.")
        email, username, _nonce = payload.split("|", 2)
        return {"email": email, "username": username}

    def record_prediction(self, filename: str, response: dict[str, Any]) -> int:
        with self.connection() as db:
            if self.uses_postgres:
                cursor = db.execute("INSERT INTO analysis_sessions(filename,created_at) VALUES(?,?) RETURNING id", (filename, now()))
                session_id = cursor.fetchone()["id"]
            else:
                cursor = db.execute("INSERT INTO analysis_sessions(filename,created_at) VALUES(?,?)", (filename, now()))
                session_id = cursor.lastrowid
            rows = response["predictions"]
            db.executemany("""INSERT INTO alert_history(session_id,timestamp,source_ip,detection_method,predicted_intrusion_type,traffic_status,reason,severity)
                VALUES(?,?,?,?,?,?,?,?)""", [
                (session_id, row.get("Timestamp"), row.get("Source_IP"), row["Detection_Method"],
                 row["Predicted_Intrusion_Type"], row["Traffic_Status"], row["Reason"], row.get("Severity")) for row in rows])
            return int(session_id)

    def record_upload_and_prediction(self, filename: str, content: bytes, response: dict[str, Any]) -> int:
        session_id = self.record_prediction(filename, response)
        with self.connection() as db:
            db.execute("INSERT INTO uploaded_files(session_id,filename,content,content_type,size_bytes,uploaded_at) VALUES(?,?,?,?,?,?)",
                       (session_id, filename, content, "text/csv", len(content), now()))
        return session_id

    def record_capture_and_prediction(self, capture_file: str | None, flow_csv: str | None, response: dict[str, Any]) -> int:
        session_id = self.record_prediction(flow_csv or capture_file or "realtime-capture", response)
        capture_data = Path(capture_file).read_bytes() if capture_file and Path(capture_file).is_file() else None
        flow_data = Path(flow_csv).read_bytes() if flow_csv and Path(flow_csv).is_file() else None
        with self.connection() as db:
            db.execute("INSERT INTO capture_records(session_id,capture_file,flow_csv,capture_data,flow_data,recorded_at) VALUES(?,?,?,?,?,?)",
                       (session_id, capture_file, flow_csv, capture_data, flow_data, now()))
        return session_id

    def sessions(self) -> list[dict[str, Any]]:
        with self.connection() as db:
            rows = db.execute("""SELECT s.id,s.filename,s.created_at AS timestamp,COUNT(a.id) AS alert_count
                FROM analysis_sessions s LEFT JOIN alert_history a ON a.session_id=s.id
                GROUP BY s.id ORDER BY s.id DESC LIMIT 100""").fetchall()
        return [dict(row) for row in rows]

    def alerts(self, session_id: int) -> list[dict[str, Any]]:
        with self.connection() as db:
            rows = db.execute("SELECT * FROM alert_history WHERE session_id=? ORDER BY id", (session_id,)).fetchall()
        return [{"Alert_ID": row["id"], "Timestamp": row["timestamp"], "Source_IP": row["source_ip"], "Detection_Method": row["detection_method"], "Predicted_Intrusion_Type": row["predicted_intrusion_type"], "Traffic_Status": row["traffic_status"], "Reason": row["reason"], "Severity": row["severity"]} for row in rows]

    def delete_session(self, session_id: int) -> None:
        with self.connection() as db:
            db.execute("DELETE FROM alert_history WHERE session_id=?", (session_id,))
            db.execute("DELETE FROM analysis_sessions WHERE id=?", (session_id,))

    def blocked(self) -> list[dict[str, Any]]:
        with self.connection() as db:
            return [dict(row) for row in db.execute("SELECT * FROM blocked_ips ORDER BY id DESC").fetchall()]

    def save_block(self, ip: str, reason: str, protocol: str, enforced: bool) -> dict[str, Any]:
        with self.connection() as db:
            db.execute("""INSERT INTO blocked_ips(ip,reason,protocol,blocked_at,status,enforced) VALUES(?,?,?,?,?,?)
              ON CONFLICT(ip) DO UPDATE SET reason=excluded.reason,protocol=excluded.protocol,blocked_at=excluded.blocked_at,status=excluded.status,enforced=excluded.enforced""",
              (ip, reason, protocol, now(), "ACTIVE", bool(enforced) if self.uses_postgres else int(enforced)))
            return dict(db.execute("SELECT * FROM blocked_ips WHERE ip=?", (ip,)).fetchone())

    def remove_block(self, ip: str) -> None:
        with self.connection() as db:
            db.execute("DELETE FROM blocked_ips WHERE ip=?", (ip,))

    def notification(self, recipient: str, subject: str, message: str, status: str) -> None:
        with self.connection() as db:
            db.execute("INSERT INTO notifications(recipient,subject,message,status,timestamp) VALUES(?,?,?,?,?)", (recipient, subject, message, status, now()))

    def notifications(self) -> list[dict[str, Any]]:
        with self.connection() as db:
            return [dict(row) for row in db.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 50").fetchall()]


class PostgresConnection:
    """Small compatibility wrapper so the store can use SQLite-style ? parameters."""
    def __init__(self, connection):
        self.connection = connection

    @staticmethod
    def _sql(query: str) -> str:
        return query.replace("?", "%s")

    def execute(self, query: str, params=()):
        return self.connection.execute(self._sql(query), params)

    def executemany(self, query: str, params):
        return self.connection.cursor().executemany(self._sql(query), params)

    def executescript(self, script: str) -> None:
        for statement in script.split(";"):
            if statement.strip():
                self.connection.execute(statement)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()
