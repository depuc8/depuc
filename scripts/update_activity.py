#!/usr/bin/env python3
"""Refresh the GitHub contribution tiles in the portfolio page.

Usage: update_activity.py <index.html> <github-username>

Reads the public contributions calendar at github.com/users/<name>/contributions
and rewrites the ACTIVITY block, the total and the "as of" date in the page.
If GitHub's markup changes and nothing can be parsed, the page is left alone.
"""

import datetime
import json
import re
import sys
import urllib.request


def fetch(user):
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions",
        headers={"User-Agent": "depuc-portfolio-activity"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse(html):
    days = {}
    for tag in re.findall(r"<td\b[^>]*\bdata-date=[^>]*>", html):
        date = re.search(r'data-date="(\d{4}-\d\d-\d\d)"', tag)
        level = re.search(r'data-level="([0-4])"', tag)
        if date and level:
            days[datetime.date.fromisoformat(date.group(1))] = level.group(1)
    total = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
    if len(days) < 300 or not total:
        return None
    first, last = min(days), max(days)
    # the page lays tiles out in Sunday-first columns
    start = first - datetime.timedelta(days=(first.weekday() + 1) % 7)
    levels = []
    d = start
    while d <= last:
        levels.append(days.get(d, "0"))
        d += datetime.timedelta(days=1)
    return {
        "start": start.isoformat(),
        "total": int(total.group(1).replace(",", "")),
        "levels": "".join(levels),
    }, last


def rewrite(page, data, as_of):
    block = "  const ACTIVITY = %s;\n" % json.dumps(data)
    page, n = re.subn(
        r"(// activity:start[^\n]*\n).*?(\s*// activity:end)",
        lambda m: m.group(1) + block.rstrip("\n") + m.group(2),
        page,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("activity markers not found in page")
    total = f"{data['total']:,}"
    page = re.sub(r"(<b data-contrib-total>)[\d,]+(</b>)", rf"\g<1>{total}\g<2>", page)
    page = re.sub(r"(contribution graph: )[\d,]+( contributions)", rf"\g<1>{total}\g<2>", page)
    stamp = f"as of {as_of.day} {as_of:%b %Y}"
    page = re.sub(r"(<span[^>]*data-contrib-asof>)[^<]*(</span>)", rf"\g<1>{stamp}\g<2>", page)
    return page


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    path, user = sys.argv[1], sys.argv[2]
    parsed = parse(fetch(user))
    if parsed is None:
        print("could not parse the contributions calendar; leaving the page as it is")
        return
    data, last = parsed
    with open(path, encoding="utf-8") as f:
        page = f.read()
    updated = rewrite(page, data, last)
    if updated != page:
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"updated: {data['total']} contributions, as of {last}")
    else:
        print("no change")


if __name__ == "__main__":
    main()
