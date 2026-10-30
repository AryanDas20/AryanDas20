#!/usr/bin/env python3
"""Generates animated profile SVGs (stats, languages, contribution matrix, trophies)
straight from the GitHub GraphQL API. No third-party services, no dependencies."""
import os, sys, json, math, html, datetime, urllib.request

USER = os.environ.get("GH_USER", "AryanDas20")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.environ.get("OUT_DIR", "assets")
MOCK = os.environ.get("MOCK") == "1"

MONO = "'Fira Code','JetBrains Mono','Courier New',monospace"
SANS = "'Segoe UI','Helvetica Neue',Arial,sans-serif"
BG, LINE = "#070b14", "#00d9f5"

QUERY = """
query($login:String!){
  user(login:$login){
    name
    followers{totalCount}
    pullRequests{totalCount}
    issues{totalCount}
    repositories(first:100, ownerAffiliations:OWNER, isFork:false){
      totalCount
      nodes{ stargazerCount
        languages(first:8, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name color } } } }
    }
    contributionsCollection{
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } }
    }
  }
}"""

def fetch():
    if MOCK:
        import random
        random.seed(7)
        d0 = datetime.date.today() - datetime.timedelta(days=364)
        weeks, day, cur = [], d0, []
        while day <= datetime.date.today():
            cur.append({"date": day.isoformat(), "contributionCount": random.choice([0,0,0,1,2,3,5,8])})
            if (day.weekday()+1) % 7 == 6:
                weeks.append({"contributionDays": cur}); cur = []
            day += datetime.timedelta(days=1)
        if cur: weeks.append({"contributionDays": cur})
        return {"name":"Aryan Das","followers":{"totalCount":11},"pullRequests":{"totalCount":14},"issues":{"totalCount":3},
          "repositories":{"totalCount":25,"nodes":[
            {"stargazerCount":4,"languages":{"edges":[{"size":90000,"node":{"name":"JavaScript","color":"#f1e05a"}},{"size":50000,"node":{"name":"HTML","color":"#e34c26"}},{"size":30000,"node":{"name":"CSS","color":"#563d7c"}}]}},
            {"stargazerCount":2,"languages":{"edges":[{"size":40000,"node":{"name":"Python","color":"#3572A5"}},{"size":9000,"node":{"name":"PHP","color":"#4F5D95"}}]}}]},
          "contributionsCollection":{"totalCommitContributions":210,"restrictedContributionsCount":30,
            "contributionCalendar":{"totalContributions":260,"weeks":weeks}}}
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    if "errors" in payload or not payload.get("data", {}).get("user"):
        raise SystemExit(f"GitHub API error: {payload.get('errors')}")
    return payload["data"]["user"]

def esc(s): return html.escape(str(s), quote=True)
def fmt(n): return f"{n:,}"

COMMON_DEFS = f"""<defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00f5a0"/><stop offset=".55" stop-color="#00d9f5"/><stop offset="1" stop-color="#7b2ff7"/></linearGradient>
<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00f5a0" stop-opacity="0"/><stop offset=".5" stop-color="#00f5a0" stop-opacity=".16"/><stop offset="1" stop-color="#00f5a0" stop-opacity="0"/></linearGradient>
<style>
.t{{font:600 13px {MONO};fill:#00f5a0;letter-spacing:2px}}
.l{{font:500 12px {MONO};fill:#8fa3bf}}
.v{{font:800 28px {SANS};fill:url(#g)}}
.s{{font:500 12px {MONO};fill:#cfe9ff}}
.blink{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}
</style>"""

def frame(w, h, title, body, extra_defs="", beam=True):
    sweep = (f'<rect x="-200" y="0" width="200" height="{h}" fill="url(#beam)"><animateTransform attributeName="transform" type="translate" from="0 0" to="{w+200} 0" dur="6s" repeatCount="indefinite"/></rect>') if beam else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
{COMMON_DEFS}{extra_defs}<clipPath id="cl"><rect width="{w}" height="{h}" rx="14"/></clipPath></defs>
<g clip-path="url(#cl)"><rect width="{w}" height="{h}" fill="{BG}"/>
<text x="20" y="30" class="t">&gt; {esc(title)}<tspan class="blink">_</tspan></text>
{body}{sweep}</g>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="none" stroke="{LINE}" stroke-opacity=".3"/>
</svg>'''

# ---------------------------------------------------------------- STATS
def build_stats(u):
    cc = u["contributionsCollection"]
    commits = cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    tiles = [("COMMITS (1Y)", commits, 500), ("PULL REQUESTS", u["pullRequests"]["totalCount"], 50),
             ("ISSUES", u["issues"]["totalCount"], 50), ("STARS EARNED", stars, 100),
             ("REPOSITORIES", u["repositories"]["totalCount"], 50), ("FOLLOWERS", u["followers"]["totalCount"], 100)]
    body = ""
    for i, (lab, val, goal) in enumerate(tiles):
        col, row = i % 3, i // 3
        x, y = 20 + col*182, 52 + row*92
        fillw = max(4, min(150, round(150*val/goal))) if val else 0
        t = 0.2 + i*0.15
        body += f'''<g transform="translate({x},{y})"><rect width="170" height="80" rx="10" fill="#0b1424" stroke="{LINE}" stroke-opacity=".18"/>
<text x="14" y="24" class="l">{lab}</text>
<text x="14" y="56" class="v" opacity="0">{fmt(val)}<animate attributeName="opacity" from="0" to="1" begin="{t}s" dur="0.5s" fill="freeze"/><animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" begin="{t}s" dur="0.5s" fill="freeze"/></text>
<rect x="14" y="66" width="142" height="4" rx="2" fill="#16243a"/>
<rect x="14" y="66" width="0" height="4" rx="2" fill="url(#g)"><animate attributeName="width" from="0" to="{round(fillw*142/150)}" begin="{t}s" dur="1.1s" fill="freeze"/></rect></g>'''
    return frame(560, 244, f"GITHUB.STATS // {USER}", body), commits, stars

# ---------------------------------------------------------------- LANGS
def build_langs(u):
    agg, colors = {}, {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]; agg[n] = agg.get(n, 0) + e["size"]; colors[n] = e["node"]["color"] or LINE
    top = sorted(agg.items(), key=lambda kv: -kv[1])[:6]
    total = sum(v for _, v in top) or 1
    body = ""
    if not top:
        body = f'<text x="20" y="80" class="s">no language data yet</text>'
        return frame(420, 244, "TOP.LANGUAGES", body)
    x = 20
    for n, v in top:
        w = 380 * v / total
        body += f'<rect x="{x:.1f}" y="48" width="0" height="10" fill="{esc(colors[n])}"><animate attributeName="width" from="0" to="{w:.1f}" begin="0.2s" dur="1s" fill="freeze"/></rect>'
        x += w
    for i, (n, v) in enumerate(top):
        y = 92 + i*24; pct = 100*v/total; t = 0.3 + i*0.12
        body += f'''<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{t}s" dur="0.4s" fill="freeze"/>
<circle cx="26" cy="{y-4}" r="5" fill="{esc(colors[n])}"/><text x="40" y="{y}" class="s">{esc(n)}</text>
<rect x="150" y="{y-9}" width="190" height="6" rx="3" fill="#16243a"/>
<rect x="150" y="{y-9}" width="0" height="6" rx="3" fill="{esc(colors[n])}"><animate attributeName="width" from="0" to="{190*pct/100:.1f}" begin="{t}s" dur="1s" fill="freeze"/></rect>
<text x="400" y="{y}" text-anchor="end" class="l">{pct:.1f}%</text></g>'''
    return frame(420, 244, "TOP.LANGUAGES", body)

# ---------------------------------------------------------------- ACTIVITY
def streaks(days):
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0; longest = max(longest, run)
    cur, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0: i -= 1
    while i >= 0 and counts[i] > 0: cur += 1; i -= 1
    return cur, longest

def build_activity(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    cur, longest = streaks(days)
    mx = max([d["contributionCount"] for d in days] + [1])
    pal = ["#10202f", "#0e4d3a", "#00875a", "#00c47a", "#00f5a0"]
    cell, gap, x0, y0 = 13, 3, 20, 76
    W = x0*2 + len(weeks)*(cell+gap)
    body = f'''<text x="20" y="54" class="l">TOTAL <tspan fill="#00f5a0" font-weight="700">{fmt(cal["totalContributions"])}</tspan>   |   CURRENT STREAK <tspan fill="#00f5a0" font-weight="700">{cur}d</tspan>   |   LONGEST <tspan fill="#00f5a0" font-weight="700">{longest}d</tspan>   |   BEST DAY <tspan fill="#00f5a0" font-weight="700">{mx}</tspan></text>'''
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            dt = datetime.date.fromisoformat(d["date"]); row = (dt.weekday() + 1) % 7
            c = d["contributionCount"]; lv = 0 if c == 0 else min(4, math.ceil(4*c/mx))
            x, y = x0 + wi*(cell+gap), y0 + row*(cell+gap)
            body += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{pal[lv]}" opacity="0"><animate attributeName="opacity" from="0" to="{1 if lv else .55}" begin="{wi*0.04:.2f}s" dur="0.3s" fill="freeze"/><title>{d["date"]}: {c}</title></rect>'
    ly = y0 + 7*(cell+gap) + 18
    body += f'<text x="{W-190}" y="{ly+10}" class="l">LESS</text>'
    for i, cc_ in enumerate(pal):
        body += f'<rect x="{W-150+i*18}" y="{ly}" width="13" height="13" rx="3" fill="{cc_}"/>'
    body += f'<text x="{W-52}" y="{ly+10}" class="l">MORE</text>'
    return frame(W, ly + 30, "CONTRIBUTION.MATRIX // LAST 12 MONTHS", body), W

# ---------------------------------------------------------------- TROPHIES
TIERS = [("STARTER", "#6b7a90"), ("BRONZE", "#cd7f32"), ("SILVER", "#c9d3df"), ("GOLD", "#ffd24a"), ("DIAMOND", "#00e5ff")]

def tier(val, th):
    t = 0
    for i, x in enumerate(th, 1):
        if val >= x: t = i
    return TIERS[t]

def build_trophies(u, commits, stars, W):
    items = [("COMMITS", commits, (1, 50, 300, 1000)), ("PULL REQUESTS", u["pullRequests"]["totalCount"], (1, 10, 50, 150)),
             ("STARS", stars, (1, 10, 50, 200)), ("REPOSITORIES", u["repositories"]["totalCount"], (1, 10, 30, 75)),
             ("FOLLOWERS", u["followers"]["totalCount"], (1, 10, 50, 200))]
    gapx = 12; cw = (W - 40 - gapx*4) / 5; body = ""
    for i, (lab, val, th) in enumerate(items):
        name, col = tier(val, th); x = 20 + i*(cw+gapx); cx = cw/2
        body += f'''<g transform="translate({x:.1f},48)"><rect width="{cw:.1f}" height="124" rx="12" fill="#0b1424" stroke="{col}" stroke-opacity=".55"/>
<g transform="translate({cx:.1f},38) scale(1.25)"><animateTransform attributeName="transform" type="translate" values="{cx:.1f} 38;{cx:.1f} 33;{cx:.1f} 38" dur="3s" begin="{i*0.4}s" repeatCount="indefinite" additive="replace"/>
<g transform="scale(1.25)" fill="{col}"><path d="M-12 -18H12V-6A12 12 0 0 1 -12 -6Z"/><rect x="-3" y="6" width="6" height="8"/><rect x="-10" y="14" width="20" height="4" rx="2"/>
<path d="M-12 -14H-18V-8A8 8 0 0 0 -10 0M12 -14H18V-8A8 8 0 0 1 10 0" fill="none" stroke="{col}" stroke-width="3"/></g></g>
<text x="{cx:.1f}" y="88" text-anchor="middle" style="font:800 22px {SANS}" fill="#e6f1ff">{fmt(val)}</text>
<text x="{cx:.1f}" y="104" text-anchor="middle" class="l">{lab}</text>
<text x="{cx:.1f}" y="118" text-anchor="middle" style="font:700 10px {MONO};letter-spacing:2px" fill="{col}">{name}</text></g>'''
    return frame(W, 190, "ACHIEVEMENTS.UNLOCKED", body)

def main():
    u = fetch()
    os.makedirs(OUT, exist_ok=True)
    stats, commits, stars = build_stats(u)
    activity, W = build_activity(u)
    files = {"stats.svg": stats, "langs.svg": build_langs(u), "activity.svg": activity,
             "trophies.svg": build_trophies(u, commits, stars, W)}
    for name, svg in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f: f.write(svg)
    print("wrote", ", ".join(files))

if __name__ == "__main__":
    main()
