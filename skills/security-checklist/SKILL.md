---
name: security-checklist
description: Security and compliance checklist for hackathons. Use when evaluating security risks, compliance requirements, data handling, or auth patterns. Covers hackathon security tiers (blocker/fix-before-demo/acceptable), common vulnerabilities (SQL injection, XSS, exposed secrets), quick security wins, and red flags that should stop a project.
---

# Security Checklist for Hackathons

## Hackathon Security Tiers

### 🔴 BLOCKER (Must fix - will cause real damage)

| Risk | Why It's Bad | Example | Time to Fix |
|------|--------------|---------|-------------|
| **Exposed API keys in code** | Attacker can run up your bill | `api_key = "sk-ant-..."` in GitHub | 15 min |
| **No auth on admin endpoints** | Anyone can delete all data | `/admin/delete_all` is public | 30 min |
| **SQL injection** | Attacker can steal/delete database | `f"SELECT * WHERE id={user_input}"` | 1 hour |
| **Public S3 with write access** | Malware hosting, data theft | Bucket policy allows `s3:PutObject` | 30 min |
| **Real PII in demos** | Privacy law violation | Using real user emails/SSNs | 1 hour (generate synthetic) |

**If you find a blocker: STOP and fix immediately. A data breach during a hackathon is career-damaging.**

### 🟡 FIX-BEFORE-DEMO (Won't hurt now, but looks bad)

| Risk | Why It Matters | Example | Time to Fix |
|------|----------------|---------|-------------|
| **No input validation** | XSS, broken UI | Doesn't check if email is valid | 30 min |
| **Hardcoded passwords** | Looks unprofessional | `password = "admin123"` | 15 min |
| **No HTTPS** | Judge asks "is this secure?" | `http://` URLs | 10 min (free with Vercel/Railway) |
| **CORS wide open** | Judge: "Anyone can call your API?" | `allow_origins=["*"]` in production | 15 min |
| **No rate limiting** | Easy to DDoS during demo | Unlimited requests allowed | 30 min |

**Fix these before judges see your demo. They're easy wins that make you look competent.**

### 🟢 ACCEPTABLE-FOR-HACKATHON (Would fix in production, OK for demo)

- Using demo accounts with fixed passwords
- Self-signed certificates for local services
- Logs containing non-sensitive debug info
- Basic auth instead of OAuth
- No session expiration (if demo is < 1 hour)
- Storing non-sensitive data in localStorage

**Acknowledge these if asked, mention you'd fix in production. Judges understand hackathon constraints.**

## Common Vulnerabilities & Quick Fixes

### 1. SQL Injection

**❌ Vulnerable Code:**
```python
# NEVER do this!
user_id = request.args.get('id')
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# Attacker sends: ?id=1 OR 1=1
# Result: Returns ALL users (data breach)
```

**✅ Fixed Code:**
```python
# Use parameterized queries
user_id = request.args.get('id')
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))

# Or use an ORM
user = db.query(User).filter(User.id == user_id).first()
```

**Time to fix:** 30 minutes to audit all queries  
**How to test:** Try input like `' OR '1'='1` in form fields

### 2. Cross-Site Scripting (XSS)

**❌ Vulnerable Code:**
```javascript
// React - NEVER use dangerouslySetInnerHTML with user input!
function UserComment({ comment }) {
  return <div dangerouslySetInnerHTML={{__html: comment}} />;
}

// Attacker submits: <script>alert('XSS!')</script>
// Result: Script executes in other users' browsers
```

**✅ Fixed Code:**
```javascript
// React escapes by default - just render normally
function UserComment({ comment }) {
  return <div>{comment}</div>;  // Safe!
}

// If you MUST render HTML, sanitize first
import DOMPurify from 'dompurify';

function UserComment({ comment }) {
  const clean = DOMPurify.sanitize(comment);
  return <div dangerouslySetInnerHTML={{__html: clean}} />;
}
```

**Time to fix:** 1 hour (install DOMPurify, audit all user content rendering)  
**How to test:** Submit `<script>alert(1)</script>` in text fields

### 3. Exposed Secrets

**❌ Vulnerable Code:**
```python
# NEVER commit this to GitHub!
import anthropic

client = anthropic.Anthropic(
    api_key="sk-ant-api03-X5mzownpZBaJJw..."  # EXPOSED!
)
```

**✅ Fixed Code:**
```python
# Use environment variables
import os
import anthropic

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

**.env file (add to .gitignore!):**
```bash
# .env - NEVER commit this file!
ANTHROPIC_API_KEY=sk-ant-api03-...
DATABASE_URL=postgresql://...
SECRET_KEY=random-string-here
```

**.gitignore:**
```
.env
.env.local
*.key
*.pem
secrets/
```

**Time to fix:** 15 minutes  
**Prevention:** Use `git-secrets` to scan commits

**If you already exposed a secret:**
1. Rotate the key IMMEDIATELY (generate new one, revoke old)
2. Check billing dashboard for unauthorized usage
3. Update environment variables with new key
4. Don't just delete the commit - keys are still in git history!

### 4. Broken Authentication

**❌ Vulnerable Code:**
```python
# NEVER store passwords in plaintext!
@app.post("/register")
def register(username: str, password: str):
    db.execute("INSERT INTO users (username, password) VALUES (?, ?)",
               (username, password))  # BAD!
```

**✅ Fixed Code:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

@app.post("/register")
def register(username: str, password: str):
    hashed = generate_password_hash(password)
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
               (username, hashed))

@app.post("/login")
def login(username: str, password: str):
    user = db.execute("SELECT * FROM users WHERE username = ?", 
                      (username,)).fetchone()
    if user and check_password_hash(user['password_hash'], password):
        return {"token": generate_jwt(user['id'])}
    return {"error": "Invalid credentials"}, 401
```

**Even better:** Use Clerk/Auth0 (don't roll your own auth)

**Time to fix:** 2-4 hours for custom auth, 30 min for Clerk

### 5. Insecure Direct Object Reference (IDOR)

**❌ Vulnerable Code:**
```python
# User can access ANY user's data by changing ID!
@app.get("/api/user/{user_id}/profile")
def get_profile(user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Attacker visits: /api/user/999/profile (not their ID)
# Result: Can see anyone's profile
```

**✅ Fixed Code:**
```python
@app.get("/api/user/{user_id}/profile")
def get_profile(user_id: int, current_user: User = Depends(get_current_user)):
    # Check authorization
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Forbidden")
    
    return db.query(User).filter(User.id == user_id).first()
```

**Time to fix:** 1 hour to audit all endpoints  
**How to test:** Try accessing `/api/resource/1`, `/api/resource/2`, etc.

## Quick Security Wins (< 4 hours total)

### 1. Environment Variables (15 min)

```bash
# Create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...
JWT_SECRET=$(openssl rand -hex 32)
EOF

# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore

# Load in Python
from dotenv import load_dotenv
load_dotenv()
```

### 2. Input Validation (30 min)

```python
from pydantic import BaseModel, EmailStr, validator

class UserInput(BaseModel):
    email: EmailStr  # Validates email format
    age: int
    username: str
    
    @validator('age')
    def age_must_be_positive(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Invalid age')
        return v
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

# FastAPI auto-validates
@app.post("/register")
def register(user: UserInput):  # Validates automatically!
    # If we get here, input is safe
    pass
```

### 3. Rate Limiting (30 min)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/generate")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def generate(request: Request):
    return {"result": "..."}
```

### 4. HTTPS Everywhere (10 min)

```python
# Redirect HTTP to HTTPS
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv("ENV") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

**Or:** Just use Vercel/Render (HTTPS by default)

### 5. CORS Configuration (15 min)

```python
from fastapi.middleware.cors import CORSMiddleware

# ❌ Don't do this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows any website to call your API
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Do this
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        "http://localhost:3000"  # For local dev
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 6. Security Headers (15 min)

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["your-app.com"])

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## Data Handling Rules

### Never Use Real PII (Personally Identifiable Information)

**❌ Don't:**
- Use real user emails from your company database
- Include actual SSNs, credit card numbers, addresses
- Screenshot real customer data for demos
- Use production database dumps

**✅ Do:**
```python
# Generate synthetic data
from faker import Faker

fake = Faker()

synthetic_users = [
    {
        "name": fake.name(),
        "email": fake.email(),
        "address": fake.address(),
        "ssn": fake.ssn(),
        "credit_card": fake.credit_card_number()
    }
    for _ in range(100)
]

# Save for demo
import json
with open('demo_data.json', 'w') as f:
    json.dump(synthetic_users, f)
```

**Legal note:** Using real PII without consent violates GDPR, CCPA, and can result in fines. Use synthetic data.

### Demo Boundaries

**What NOT to demo publicly:**
- Real API keys (use demo keys or censored screenshots)
- Database credentials
- Real user accounts (create demo accounts)
- Production systems (use staging/local)
- Proprietary algorithms (if covered by NDA)

**Safe to demo:**
- Synthetic data
- Open-source code
- Public APIs
- Mock/fake credentials labeled as such

## Auth Patterns for Hackathons

### Option 1: Clerk (Easiest, 15 min)

```bash
npm install @clerk/nextjs
```

```typescript
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      {children}
    </ClerkProvider>
  )
}

// Any protected page
import { auth } from '@clerk/nextjs/server'

export default async function ProtectedPage() {
  const { userId } = await auth()
  if (!userId) return redirect('/sign-in')
  
  return <div>Protected content</div>
}
```

**Security:** ✅ Production-ready  
**Time:** 15 minutes  
**Cost:** FREE for 10k monthly active users

### Option 2: JWT Tokens (2 hours)

```python
from datetime import datetime, timedelta
import jwt
from werkzeug.security import check_password_hash

SECRET_KEY = os.getenv("JWT_SECRET")

def create_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

@app.post("/login")
def login(username: str, password: str):
    user = db.get_user(username)
    if user and check_password_hash(user.password_hash, password):
        token = create_token(user.id)
        return {"token": token}
    raise HTTPException(401, "Invalid credentials")

# Use in endpoints
from fastapi import Depends, Header

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    token = authorization.split(" ")[1]
    user_id = verify_token(token)
    return db.get_user_by_id(user_id)

@app.get("/api/protected")
def protected(user: User = Depends(get_current_user)):
    return {"message": f"Hello, {user.username}"}
```

### Option 3: Demo Accounts (Fastest for hackathons)

```python
# For demos only - NOT production!
DEMO_USERS = {
    "demo@example.com": {"password": "demo123", "role": "user"},
    "admin@example.com": {"password": "admin123", "role": "admin"}
}

@app.post("/login")
def demo_login(email: str, password: str):
    user = DEMO_USERS.get(email)
    if user and user["password"] == password:
        return {"token": create_token(email), "role": user["role"]}
    raise HTTPException(401, "Invalid credentials")
```

**Show this during demo:** "For the hackathon, we're using demo accounts. In production, we'd integrate Clerk/Auth0."

## Red Flags That Should Stop a Project

### 🛑 Stop if you see:

| Red Flag | Why It's Bad | What To Do |
|----------|--------------|------------|
| **NoSQL injection possible** | `db.find({"user": user_input})` without sanitization | Use parameterized queries |
| **eval() or exec() on user input** | Arbitrary code execution | NEVER use eval() with user data |
| **Shell command with user input** | `os.system(f"rm {user_file}")` | Use safe libraries, validate input |
| **Deserializing untrusted data** | `pickle.loads(user_data)` | Use JSON instead |
| **No auth on admin/delete endpoints** | Anyone can delete all data | Add authentication checks |
| **API keys client-side** | `const API_KEY = "sk-ant-..."` in JavaScript | Move to backend |

**These are not "we'll fix later" - these are "we need to redesign this part now."**

## OWASP Top 10 Hackathon Checklist

Quick 15-minute scan before demo:

```bash
# 1. Broken Access Control
- [ ] Admin endpoints require admin role check?
- [ ] Users can't access others' data by changing IDs?

# 2. Cryptographic Failures
- [ ] No passwords stored in plaintext?
- [ ] HTTPS enabled in production?
- [ ] Secrets in environment variables, not code?

# 3. Injection
- [ ] Using parameterized SQL queries?
- [ ] Not using eval() on user input?
- [ ] Input validation on all forms?

# 4. Insecure Design
- [ ] Authentication required for sensitive operations?
- [ ] Rate limiting on API endpoints?
- [ ] Demo uses synthetic data, not real PII?

# 5. Security Misconfiguration
- [ ] .env in .gitignore?
- [ ] Debug mode OFF in production?
- [ ] CORS not wide open ("*") in production?

# 6. Vulnerable Components
- [ ] Using recent versions of libraries?
- [ ] No critical npm audit warnings?

# 7. Authentication Failures
- [ ] Passwords hashed with bcrypt/pbkdf2?
- [ ] JWT tokens have expiration?
- [ ] No hardcoded credentials in code?

# 8. Data Integrity Failures
- [ ] API responses signed/verified if critical?
- [ ] File uploads restricted to safe types?

# 9. Logging Failures
- [ ] Errors logged (but not sensitive data)?
- [ ] Can trace issues from logs?

# 10. Server-Side Request Forgery (SSRF)
- [ ] Not fetching user-provided URLs without validation?
- [ ] Allowlist for external API calls?
```

**Time to complete:** 15 minutes if you've been following best practices, 2-4 hours if you need to fix multiple issues.

## Security Review Workflow

**2 hours before demo:**
1. Run this checklist (15 min)
2. Test login/auth flows (15 min)
3. Try SQL injection on inputs (15 min)
4. Check GitHub for exposed secrets (15 min)
5. Verify .env is in .gitignore (5 min)
6. Test with demo account (15 min)
7. Prepare answer for "Is this secure?" (15 min)

**Answer to "Is this secure?":**
> "For the hackathon, we focused on the critical security measures: HTTPS, input validation, environment variables for secrets, and authentication via [Clerk/JWT]. In production, we'd add comprehensive logging, security scanning, and penetration testing."

**What NOT to say:**
> "Security isn't important for a demo" ← Judge will think you don't understand security
> "We didn't have time for security" ← Red flag

**Better framing:**
> "We implemented hackathon-appropriate security - the critical blockers are handled, and we have a roadmap for production hardening."