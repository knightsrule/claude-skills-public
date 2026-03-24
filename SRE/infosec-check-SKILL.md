You are running a pre-production infosec checklist. Your goal is to perform an external security audit against a website and API, combining publicly observable signals with Cloudflare API checks when a token is provided.

## Step 1: Get inputs

If not provided as arguments, ask the user for:
- **Website URL** (e.g. `https://app.example.com`)
- **API URL** (e.g. `https://api.example.com`)
- **Cloudflare API token** (optional — say "skip" to skip; if provided, enables deeper Cloudflare checks)

Extract the root domain from each URL for DNS checks.

## Step 2: Run all checks in parallel using Bash

Run the following checks. Use `curl -sI --max-time 10` for HTTP header checks. Use `dig` for DNS checks.

### DNS & Email

```bash
# SPF
dig TXT <domain> +short | grep spf

# DMARC
dig TXT _dmarc.<domain> +short

# Common DKIM selectors
for sel in default mail cf2024-1 s1 s2 google amazonses; do
  result=$(dig TXT ${sel}._domainkey.<domain> +short 2>/dev/null)
  [ -n "$result" ] && echo "DKIM[$sel]: found"
done

# MX
dig MX <domain> +short
```

### TLS & HTTP Headers (website)

```bash
curl -sI --max-time 10 <website_url>
```

Check for:
- `strict-transport-security` (HSTS)
- `x-frame-options`
- `x-content-type-options`
- `content-security-policy`
- `referrer-policy`
- `permissions-policy`
- Server header (should not leak version info)

### TLS & HTTP Headers (API)

```bash
curl -sI --max-time 10 <api_url>
```

Also check:
- `access-control-allow-origin` (CORS — flag if `*`)
- `access-control-allow-credentials`

### Exposed sensitive endpoints (API)

```bash
for path in /docs /redoc /openapi.json /swagger /swagger-ui /graphql /metrics /health /debug /admin /env /config; do
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 <api_url>$path)
  echo "$path: $status"
done
```

Flag any that return 200 other than `/health`.

### Auth endpoint rate limiting

```bash
for i in $(seq 1 10); do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST <api_url>/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrongpassword"}'
done
```

If all 10 return 200 or 401 (not 429), rate limiting may not be active.

### Certificate expiry

```bash
echo | openssl s_client -connect <domain>:443 -servername <domain> 2>/dev/null | openssl x509 -noout -dates
```

Flag if expiry is within 30 days.

### Cloudflare API checks (only if token provided)

First resolve the zone ID for the domain:
```bash
curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=<domain>" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" | jq '.result[0].id'
```

Then run all checks using the zone ID:

```bash
# All zone settings in one call
curl -s "https://api.cloudflare.com/client/v4/zones/<zone_id>/settings" \
  -H "Authorization: Bearer <token>" | jq '.result[] | select(.id | test("ssl|always_use_https|min_tls_version|security_level|browser_check|hotlink_protection|waf|development_mode|hsts|brotli")) | {id, value}'

# Bot Fight Mode
curl -s "https://api.cloudflare.com/client/v4/zones/<zone_id>/bot_management" \
  -H "Authorization: Bearer <token>" | jq '{fight_mode: .result.fight_mode, session_score: .result.enable_js}'

# WAF managed rulesets
curl -s "https://api.cloudflare.com/client/v4/zones/<zone_id>/rulesets" \
  -H "Authorization: Bearer <token>" | jq '[.result[] | select(.phase == "http_request_firewall_managed") | {name, description}]'

# Email routing status
curl -s "https://api.cloudflare.com/client/v4/zones/<zone_id>/email/routing" \
  -H "Authorization: Bearer <token>" | jq '{enabled: .result.enabled, status: .result.status}'

# DNS records — flag any unproxied A/CNAME records (grey cloud = exposed origin IP)
curl -s "https://api.cloudflare.com/client/v4/zones/<zone_id>/dns_records?per_page=100" \
  -H "Authorization: Bearer <token>" | jq '[.result[] | select(.type == "A" or .type == "CNAME") | {name, type, proxied, content}]'

# Rate limiting rules
curl -s "https://api.cloudflare.com/client/v4/zones/<zone_id>/rulesets" \
  -H "Authorization: Bearer <token>" | jq '[.result[] | select(.phase == "http_ratelimit") | {name}]'
```

Check for and flag:
- `ssl` not set to `full_strict` (Flexible = critical failure)
- `always_use_https` = off
- `min_tls_version` below `1.2`
- `security_level` = `essentially_off`
- `development_mode` = `on` (must be off in production)
- Bot Fight Mode disabled
- No WAF managed ruleset active
- Any A or CNAME records with `proxied: false` (origin IP exposed)
- Email routing enabled with shared DKIM key (`cf2024-1`) and DMARC not enforced

## Step 3: Produce a report

Output a pass/fail table grouped by category:

| Category | Check | Status | Notes |
|---|---|---|---|
| **DNS/Email** | SPF `-all` | ✓ / ⚠️ / ✗ | |
| **DNS/Email** | DMARC `p=quarantine` or `p=reject` | | |
| **DNS/Email** | DKIM configured | | |
| **DNS/Email** | No shared DKIM keys | | |
| **TLS** | HTTPS enforced | | |
| **TLS** | HSTS header present | | |
| **TLS** | Cert expiry > 30 days | | |
| **Headers (web)** | X-Frame-Options | | |
| **Headers (web)** | X-Content-Type-Options | | |
| **Headers (web)** | Content-Security-Policy | | |
| **Headers (web)** | Referrer-Policy | | |
| **Headers (web)** | Server header hides version | | |
| **Headers (API)** | CORS not wildcard | | |
| **API** | No sensitive endpoints exposed | | |
| **API** | Rate limiting on auth | | |
| **Cloudflare** | SSL mode = Full (strict) | ✓ / ⚠️ / ✗ / — | — if no token |
| **Cloudflare** | Always Use HTTPS = on | | |
| **Cloudflare** | Min TLS version ≥ 1.2 | | |
| **Cloudflare** | Development mode = off | | |
| **Cloudflare** | Security level not "essentially off" | | |
| **Cloudflare** | Bot Fight Mode enabled | | |
| **Cloudflare** | WAF managed rules active | | |
| **Cloudflare** | No unproxied A/CNAME records | | |
| **Cloudflare** | Rate limiting rules configured | | |
| **Cloudflare** | Email routing + shared DKIM risk assessed | | |

Then list **action items** — only the failures, with the specific fix needed.

## Grading

- All pass → **Ready for production**
- 1–3 minor failures → **Conditionally ready** (list blockers vs. nice-to-haves)
- Critical failures (DMARC `p=none`, wildcard CORS, exposed `/docs` or `/env`) → **Not ready**

Critical failures that block go-live:
- DMARC missing or `p=none`
- SPF `~all` or missing
- CORS `Access-Control-Allow-Origin: *` on API
- Exposed `/openapi.json`, `/env`, `/config`, `/debug`, or `/admin` returning 200
- TLS cert expiring within 7 days
- No HTTPS (HTTP accessible without redirect)
- Cloudflare SSL mode = Flexible (origin traffic unencrypted)
- Cloudflare development mode = on
- Unproxied DNS records exposing origin server IP
