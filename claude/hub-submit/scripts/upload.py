#!/usr/bin/env python3
"""Upload a Claude Code plugin (or wrap a single command) to the Remedio AI Hub.

The hub (https://ai-hub.mgmt.cloud.gytpol.com) hosts skills and plugins. An
authored upload commits the files to the hub's repo and opens a review PR in
gytpol/ai-hub — it is NOT published until a maintainer merges that PR.

Auth: the hub sits behind SSO, so there's no API token. Supply your browser
session token via the REMEDIO_HUB_COOKIE env var or the file
~/.config/remedio-hub/cookie.txt. Refresh it when uploads start failing auth.

Usage:
    upload.py PLUGIN_DIR [--slug SLUG] [--tags a,b,c] [--mode create|update]
    upload.py --command FILE.md [--name NAME] [--desc TEXT] [--tags a,b,c]

PLUGIN_DIR must contain .claude-plugin/plugin.json. All regular files under it
are sent (skipping .git, node_modules, __pycache__, *.pyc, .DS_Store).

The --command flag wraps a single slash-command markdown file into a one-command
plugin on the fly (manifest synthesized from the file's frontmatter / args).
"""
import argparse, json, os, pathlib, re, sys, urllib.request, urllib.error

HUB = "https://ai-hub.mgmt.cloud.gytpol.com"
ENDPOINT = f"{HUB}/api/commit-authored-plugin/"
COOKIE_FILE = pathlib.Path.home() / ".config" / "remedio-hub" / "cookie.txt"
SKIP = {".git", "node_modules", "__pycache__", ".DS_Store"}
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_cookie() -> str:
    c = os.environ.get("REMEDIO_HUB_COOKIE")
    if c:
        return c.strip()
    if COOKIE_FILE.exists():
        return COOKIE_FILE.read_text().strip()
    sys.exit(
        f"No hub session token. Set the REMEDIO_HUB_COOKIE env var or write it to {COOKIE_FILE}.\n"
        "Obtain it from an authenticated browser session to the hub."
    )


def collect_files(plugin_dir: pathlib.Path) -> list[dict]:
    files = []
    for p in sorted(plugin_dir.rglob("*")):
        if not p.is_file() or any(part in SKIP for part in p.relative_to(plugin_dir).parts):
            continue
        if p.suffix == ".pyc":
            continue
        files.append({"path": p.relative_to(plugin_dir).as_posix(),
                      "content": p.read_text(encoding="utf-8")})
    return files


def frontmatter_desc(md: str) -> str:
    m = re.match(r"^---\n(.*?)\n---", md, re.S)
    if m:
        d = re.search(r"^description:\s*(.+)$", m.group(1), re.M)
        if d:
            return d.group(1).strip()
    return ""


def post(payload: dict, cookie: str) -> dict:
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json",
                 "Cookie": cookie}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read().decode()
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        ct = e.headers.get("content-type", "")
        if e.code in (301, 302, 303, 307, 308) or e.code == 401:
            sys.exit("Auth failed — your hub session token is missing or expired. Refresh it.")
        if e.code == 403 and "text/html" in ct:
            sys.exit("Blocked by the hub's edge firewall (403). This is a content/WAF rule, "
                     "not an auth problem — the request never reached the app. Check the files "
                     "for content the firewall may reject, or submit via the hub's web UI.")
        sys.exit(f"Hub returned HTTP {e.code}: {body[:400]}")
    return json.loads(body)


def main() -> None:
    ap = argparse.ArgumentParser(description="Upload a plugin/command to the Remedio AI Hub")
    ap.add_argument("plugin_dir", nargs="?", help="plugin directory (with .claude-plugin/plugin.json)")
    ap.add_argument("--command", help="single slash-command .md to wrap as a one-command plugin")
    ap.add_argument("--slug", help="override slug (defaults to manifest name / command filename)")
    ap.add_argument("--name", help="plugin name when using --command")
    ap.add_argument("--desc", help="description when using --command")
    ap.add_argument("--tags", default="", help="comma-separated tags")
    ap.add_argument("--mode", default="create", choices=["create", "update"])
    args = ap.parse_args()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    if args.command:
        md_path = pathlib.Path(args.command).expanduser()
        slug = args.slug or md_path.stem
        manifest = {
            "name": args.name or slug,
            "version": "1.0.0",
            "description": args.desc or frontmatter_desc(md_path.read_text()) or f"The /{slug} command.",
        }
        files = [
            {"path": ".claude-plugin/plugin.json", "content": json.dumps(manifest, indent=2) + "\n"},
            {"path": f"commands/{md_path.name}", "content": md_path.read_text(encoding="utf-8")},
        ]
    elif args.plugin_dir:
        plugin_dir = pathlib.Path(args.plugin_dir).expanduser().resolve()
        mpath = plugin_dir / ".claude-plugin" / "plugin.json"
        if not mpath.exists():
            sys.exit(f"No manifest at {mpath}. Pass --command to wrap a single command instead.")
        manifest = json.loads(mpath.read_text())
        slug = args.slug or manifest.get("name")
        files = collect_files(plugin_dir)
    else:
        ap.error("give a <plugin_dir> or --command FILE.md")

    if not slug or not KEBAB.match(slug):
        sys.exit(f"slug {slug!r} must be kebab-case (a-z, 0-9, hyphens).")

    payload = {"slug": slug, "manifest": manifest, "tags": tags,
               "mode": args.mode, "files": files}
    print(f"Uploading '{slug}' ({len(files)} file(s)) to the AI Hub …", file=sys.stderr)
    res = post(payload, load_cookie())
    if res.get("ok"):
        print(f"OK  slug={res['slug']}  PR #{res.get('pr_number')}  {res.get('pr_url')}")
    else:
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
