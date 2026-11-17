# depuc(1)

My portfolio, written as a man page. Live at https://depuc8.github.io/depuc/

Press `:` on the page and type `help`.

## Layout

- `site/` is what gets published: `index.html`, the `404.html` segfault page, `resume.pdf` and the PGP key `depuc.asc`.
- `scripts/update_activity.py` refreshes the GitHub contribution tiles in `site/index.html`.
- `.github/workflows/pages.yml` runs that script every day at 00:17 UTC and on every push,
  commits the refreshed tiles if they changed, and deploys `site/` to GitHub Pages.

## Run it locally

```sh
python3 -m http.server -d site
```
