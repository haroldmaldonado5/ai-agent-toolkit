# Security Policy

## Credential Management

### Google OAuth Credentials

**Location:** C:\Users\cu5to\.config\google-drive-mcp\gcp-oauth.keys.json

**Last Regeneration:** March 31, 2026

**Process:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials?project=claude-agents-491403)
2. Delete old OAuth client
3. Create new "Desktop app" OAuth client
4. Configure required scopes BEFORE first use:
   - https://www.googleapis.com/auth/drive
   - https://www.googleapis.com/auth/drive.file
   - https://www.googleapis.com/auth/drive.readonly
   - https://www.googleapis.com/auth/documents
   - https://www.googleapis.com/auth/documents.readonly
   - https://www.googleapis.com/auth/spreadsheets
   - https://www.googleapis.com/auth/spreadsheets.readonly
   - https://www.googleapis.com/auth/calendar
   - https://www.googleapis.com/auth/calendar.readonly
5. Download credentials JSON
6. Update gcp-oauth.keys.json with new client_id and client_secret
7. Delete old 	okens.json
8. Run auth command to generate new tokens

**Google Cloud Project:** claude-agents-491403  
**Account:** hmv.agents@gmail.com

---

### GitHub Personal Access Token

**Last Regeneration:** March 28, 2026

**Stored In:** .claude.json (not committed to Git)

**Process:**
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate new token (classic)
3. Required scopes: epo, workflow, ead:org
4. Update token in .claude.json under mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN
5. Restart Claude Code/Antigravity

**GitHub Account:** haroldmaldonado5

---

### Other API Keys

#### Tavily API Key
- **Stored In:** .claude.json
- **Regenerate At:** [Tavily Dashboard](https://tavily.com)

#### Notion API Key
- **Stored In:** .claude.json
- **Regenerate At:** [Notion Integrations](https://www.notion.so/my-integrations)

---

## Protected Files (.gitignore)

The following file patterns are protected and will never be committed:

- gcp-oauth.keys.json - Google OAuth credentials
- client_secret*.json - Google OAuth downloads
- 	okens.json - OAuth tokens
- .env* - Environment variables
- *.key, *.pem, *.p12 - Private keys
- .claude.json - Claude Code configuration (contains API keys)
- databases/ - Local SQLite databases
- *secret*, *token*, *credential* - Any file with sensitive keywords

---

## Legacy Repository Warning

**OLD REPO (DO NOT PUSH):** C:\Users\cu5to\OneDrive\Documents\APP- AGENTE1.OLD.NO-PUSH\

This folder contains an old repository with exposed credentials in its files (not Git history).

**NEVER push from this directory.**

The folder has been renamed with .OLD.NO-PUSH suffix as a warning.

---

## Security Audit Log

### 2026-03-31: Phase 0 Security Audit
- ✅ Identified exposed Google Client Secret in legacy repo (file-level, not Git history)
- ✅ Regenerated Google OAuth client with fresh credentials
- ✅ Configured scopes before first use
- ✅ Renamed legacy folder with warning suffix
- ✅ Created comprehensive .gitignore
- ✅ Verified no secrets in Git history
- ✅ Temporarily disabled Google Drive MCP (to be re-enabled in Phase 1)

**Actions Taken:**
- Old Google OAuth client deleted and replaced with new credentials
- New credentials stored securely in .config/google-drive-mcp/ (not committed to Git)
- All credential values excluded from this public documentation

---

## Reporting Security Issues

If you discover a security vulnerability, please email: haroldmaldonado.v5@gmail.com

Do not open public GitHub issues for security vulnerabilities.