# Kalembang Security Audit

**Audit Date:** January 7, 2026  
**Scope:** Orange Pi 5 production/local deployment  
**Status:** Review Complete

---

## 🔴 Critical Issues

### 1. No Authentication/Authorization

**Location:** `api/kalembang/main.py` lines 231-236

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Risk:** Any device on the LAN can control motors, create/delete alarms, and trigger emergency stops without authentication.

**Recommendation:** 
- Add API key authentication via header (e.g., `X-API-Key`)
- Restrict CORS to specific origins

---

### 2. API Bound to All Interfaces (0.0.0.0)

**Location:** 
- `api/kalembang/config.py` line 30: `API_HOST = "0.0.0.0"`
- `api/systemd/kalembang.service` line 14: `--host 0.0.0.0`

**Risk:** If the Orange Pi connects to a public network, the API is exposed to the internet.

**Recommendation:**
- Bind to specific LAN interface IP (e.g., `192.168.1.x`)
- Or use firewall rules to restrict access to port 8088

---

## 🟠 High Severity Issues

### 3. SQLite Thread Safety

**Location:** `api/kalembang/database.py` line 69

```python
self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
```

**Risk:** FastAPI handles concurrent async requests. Without a connection pool or mutex, concurrent writes may corrupt the database.

**Recommendation:**
- Use `aiosqlite` for async-safe access
- Or add `threading.Lock()` around write operations
- Or use a connection pool

---

### 4. Self-Hosted Runner with Sudo Access

**Location:** `.github/workflows/deploy.yml`

The self-hosted runner requires passwordless sudo for `systemctl` commands.

**Risk:** If the GitHub repository is compromised, an attacker could execute privileged commands on the Orange Pi.

**Recommendation:**
- Limit sudoers to specific commands only:
  ```
  orangepi ALL=(ALL) NOPASSWD: /bin/systemctl start kalembang*, /bin/systemctl stop kalembang*, /bin/systemctl status kalembang*, /bin/systemctl daemon-reload, /bin/systemctl enable kalembang*, /bin/cp * /etc/systemd/system/*, /bin/journalctl -u kalembang*
  ```
- Consider SSH deploy keys with limited scope instead of self-hosted runner

---

## 🟡 Medium Severity Issues

### 5. Relative Database Path

**Location:** `api/kalembang/config.py` line 33

```python
DATABASE_PATH = "data/kalembang.db"
```

**Risk:** If working directory changes, database may be created in unexpected location.

**Recommendation:** Use absolute path or resolve at startup:
```python
DATABASE_PATH = Path(__file__).parent.parent / "data" / "kalembang.db"
```

---

### 6. No Rate Limiting

**Location:** All API endpoints in `main.py`

**Risk:** Denial of service via request flooding.

**Recommendation:** Add rate limiting with `slowapi`:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
```

---

### 7. No Input Sanitization on Alarm Name

**Location:** `api/kalembang/main.py` line 50

```python
name: str = Field(..., min_length=1, max_length=100)
```

**Risk:** While SQL injection is prevented via parameterized queries, special characters could cause issues in logs or UI (log injection, XSS if rendered unsafely).

**Recommendation:** Add regex validation:
```python
name: str = Field(..., min_length=1, max_length=100, pattern=r'^[\w\s\-\.]+$')
```

---

### 8. GPIO Pin Validation

**Location:** `api/kalembang/gpio.py` lines 31-44

While subprocess uses `capture_output=True` (good), pin values passed to CLI aren't validated against an allowlist.

**Recommendation:** Validate pins before execution:
```python
VALID_PINS = {ENA_PIN, ENB_PIN, IN1_PIN, IN2_PIN, IN3_PIN, IN4_PIN, STOP_BTN_PIN}

def _validate_pin(self, pin: int) -> None:
    if pin not in VALID_PINS:
        raise GPIOError(f"Invalid pin: {pin}")
```

---

## 🟢 Good Security Practices

| Practice | Location | Notes |
|----------|----------|-------|
| ✅ Parameterized SQL | `database.py` | All queries use `?` placeholders |
| ✅ No shell=True | `gpio.py` | subprocess uses list args |
| ✅ Pydantic validation | `main.py` | Input models with constraints |
| ✅ GPIO cleanup | `gpio.py` | Motors turned off on shutdown |
| ✅ Secrets in GitHub | `.github/workflows/` | Cloudflare tokens not hardcoded |
| ✅ .env.example pattern | Root | No secrets committed |
| ✅ DB schema constraints | `database.py` | CHECK constraints on columns |
| ✅ Timeout on subprocess | `gpio.py` | 5-second timeout prevents hangs |

---

## 📋 Remediation Checklist

| Priority | Issue | Status |
|----------|-------|--------|
| 🔴 | Add API authentication | ⬜ TODO |
| 🔴 | Restrict CORS origins | ⬜ TODO |
| 🔴 | Bind to specific interface | ⬜ TODO |
| 🟠 | Fix SQLite thread safety | ⬜ TODO |
| 🟠 | Limit sudoers for runner | ⬜ TODO |
| 🟡 | Use absolute database path | ⬜ TODO |
| 🟡 | Add rate limiting | ⬜ TODO |
| 🟡 | Sanitize alarm name input | ⬜ TODO |
| 🟡 | Validate GPIO pins | ⬜ TODO |

---

## Notes

- This is a LAN-only device controller, so some risks are mitigated by network isolation
- Physical STOP button provides hardware-level safety override
- Consider adding network firewall rules on the Orange Pi as defense in depth
