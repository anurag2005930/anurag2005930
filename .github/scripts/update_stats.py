#!/usr/bin/env python3
"""Auto-update assets/stats-card.svg using GitHub GraphQL API."""
import json
import os
import urllib.request
from pathlib import Path

LOGIN = os.environ.get("TARGET_USER", "anurag2005930")
TOKEN = os.environ["GH_TOKEN"]
ACCENT1 = "#00e5ff"
ACCENT2 = "#7c3aed"

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    pullRequests { totalCount }
    contributionsCollection { contributionCalendar { totalContributions } }
    repositories(first: 50, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode("utf-8"),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "profile-stats-updater"},
)
user = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))["data"]["user"]
repos = user["repositories"]["nodes"]
stars = sum(r["stargazerCount"] for r in repos)
lang_bytes = {}
for r in repos:
    for edge in r["languages"]["edges"]:
        name = edge["node"]["name"]
        color = edge["node"]["color"] or "#8b949e"
        lang_bytes[name] = (lang_bytes.get(name, (0, color))[0] + edge["size"], color)
total = sum(v[0] for v in lang_bytes.values()) or 1
top = sorted([(k, v[0], v[0] * 100.0 / total, v[1]) for k, v in lang_bytes.items()], key=lambda x: x[1], reverse=True)[:5]

bar_x, bar_w, cur_x = 486, 384, 486.0
segments, legend = [], []
for idx, (name, _sz, pct, color) in enumerate(top):
    seg_w = (bar_x + bar_w) - cur_x if idx == len(top) - 1 else bar_w * (pct / 100.0)
    segments.append(f'<rect x="{cur_x:.1f}" y="76" width="{max(seg_w, 2.0):.1f}" height="12" fill="{color}"/>')
    cur_x += seg_w
    col, row = idx % 2, idx // 2
    lx, ly = 486 + col * 196, 114 + row * 28
    legend.append(
        f'<circle cx="{lx + 6}" cy="{ly - 4}" r="5" fill="{color}"/>'
        f'<text x="{lx + 18}" y="{ly}" fill="#e2e8f0" font-family="Segoe UI, Ubuntu, sans-serif" font-size="12.5" font-weight="600">{name}</text>'
        f'<text x="{lx + 178}" y="{ly}" text-anchor="end" fill="#94a3b8" font-family="Consolas, monospace" font-size="12">{pct:.1f}%</text>'
    )

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="215" viewBox="0 0 900 215" role="img" aria-label="GitHub Telemetry and Language Stats">
  <defs><clipPath id="barClip"><rect x="486" y="76" width="384" height="12" rx="6"/></clipPath></defs>
  <rect x="2" y="2" width="438" height="211" rx="14" fill="#0d1117" stroke="{ACCENT1}" stroke-opacity="0.35" stroke-width="1.3"/>
  <text x="26" y="34" fill="#ffffff" font-family="Segoe UI, Ubuntu, sans-serif" font-size="15.5" font-weight="700">⚡ GitHub Telemetry</text>
  <rect x="330" y="18" width="88" height="22" rx="11" fill="#161f30" stroke="{ACCENT1}" stroke-opacity="0.4" stroke-width="1"/>
  <text x="374" y="33" text-anchor="middle" fill="{ACCENT1}" font-family="Consolas, monospace" font-size="10.5" font-weight="700">SINCE {user['createdAt'][:4]}</text>
  <rect x="24" y="52" width="190" height="66" rx="10" fill="#131924" stroke="#243045" stroke-width="1"/>
  <text x="40" y="75" fill="#94a3b8" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11.5" font-weight="600">PUBLIC REPOS</text>
  <text x="40" y="104" fill="{ACCENT1}" font-family="Consolas, monospace" font-size="24" font-weight="800">{user['repositories']['totalCount']}</text>
  <rect x="228" y="52" width="190" height="66" rx="10" fill="#131924" stroke="#243045" stroke-width="1"/>
  <text x="244" y="75" fill="#94a3b8" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11.5" font-weight="600">CONTRIBUTIONS (1Y)</text>
  <text x="244" y="104" fill="#22c55e" font-family="Consolas, monospace" font-size="24" font-weight="800">{user['contributionsCollection']['contributionCalendar']['totalContributions']}</text>
  <rect x="24" y="128" width="190" height="66" rx="10" fill="#131924" stroke="#243045" stroke-width="1"/>
  <text x="40" y="151" fill="#94a3b8" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11.5" font-weight="600">STARS EARNED</text>
  <text x="40" y="180" fill="#fbbf24" font-family="Consolas, monospace" font-size="24" font-weight="800">{stars}</text>
  <rect x="228" y="128" width="190" height="66" rx="10" fill="#131924" stroke="#243045" stroke-width="1"/>
  <text x="244" y="151" fill="#94a3b8" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11.5" font-weight="600">PULL REQUESTS</text>
  <text x="244" y="180" fill="{ACCENT2}" font-family="Consolas, monospace" font-size="24" font-weight="800">{user['pullRequests']['totalCount']}</text>
  <rect x="460" y="2" width="438" height="211" rx="14" fill="#0d1117" stroke="{ACCENT2}" stroke-opacity="0.35" stroke-width="1.3"/>
  <text x="486" y="34" fill="#ffffff" font-family="Segoe UI, Ubuntu, sans-serif" font-size="15.5" font-weight="700">🧬 Language Distribution</text>
  <text x="870" y="34" text-anchor="end" fill="#64748b" font-family="Consolas, monospace" font-size="11">@{LOGIN}</text>
  <rect x="486" y="76" width="384" height="12" rx="6" fill="#1e293b"/>
  <g clip-path="url(#barClip)">{''.join(segments)}</g>
  {''.join(legend)}
  <text x="486" y="196" fill="#64748b" font-family="Consolas, monospace" font-size="10.5">Weighted by bytes across original public repositories</text>
</svg>"""

Path("assets/stats-card.svg").write_text(svg, encoding="utf-8")
