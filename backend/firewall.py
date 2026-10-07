"""Explicit, manual firewall actions.  No rule is applied during prediction."""
from __future__ import annotations
import ipaddress
import os
import platform
import subprocess

def validate_ip(value: str) -> str:
    try:
        return str(ipaddress.ip_address(value.strip()))
    except ValueError as exc:
        raise ValueError("Enter a valid IPv4 or IPv6 address.") from exc

def rule_name(ip: str) -> str:
    return "SecureFlow-Block-" + ip.replace(":", "_").replace(".", "_")

def block(ip: str) -> bool:
    """Apply an inbound deny rule when FIREWALL_ENFORCEMENT=true; otherwise simulate."""
    if os.getenv("FIREWALL_ENFORCEMENT", "false").lower() != "true":
        return False
    if platform.system() == "Windows":
        result = subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name(ip)}", "dir=in", "action=block", f"remoteip={ip}"], capture_output=True, text=True)
    else:
        result = subprocess.run(["iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Firewall command failed.")
    return True

def unblock(ip: str) -> bool:
    if os.getenv("FIREWALL_ENFORCEMENT", "false").lower() != "true":
        return False
    if platform.system() == "Windows":
        result = subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name(ip)}"], capture_output=True, text=True)
    else:
        result = subprocess.run(["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Firewall command failed.")
    return True
