import requests
email = "hmv_agents" + chr(64) + "gmail.com"
body = {"name": "Demo", "email": email, "plan": "pro"}
h = {"X-Admin-Key": "6f876024373086c3460f8416a80c55c9aa3bb444825037b7400e7f7bad44c6fa", "Content-Type": "application/json"}
r = requests.post("https://ai-agent-toolkit-production.up.railway.app/admin/tenants", json=body, headers=h)
print(r.status_code)
print(r.text)