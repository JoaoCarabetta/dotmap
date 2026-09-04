# Deploy

The public map is [https://carabetta.xyz/dotsbr/](https://carabetta.xyz/dotsbr/). The GitHub repo is [JoaoCarabetta/dotsbr](https://github.com/JoaoCarabetta/dotsbr) (the old `dotmap` name redirects). `master` and `main` are production: a push of `index.html`, `og.jpg`, or the favicon files deploys those files to the VPS. The old slug `/dataviz/brazildots/` 301s to `/dotsbr/`. Production `index.html` loads Umami (`analytics.carabetta.xyz`, website **dotsbr-prod**); localhost does not. See [`user-analytics.md`](user-analytics.md).

Nginx and the rest of carabetta.xyz live in the sibling `carabetta.xyz` repo. That repo deploys on push to `main` (its `master` branch is an older diverged line and is not wired to prod).

## What CI uploads

| Job | Repo | Uploads |
|---|---|---|
| `.github/workflows/deploy.yml` | this repo | `index.html` + `og.jpg` (WhatsApp/iMessage Open Graph card) + `favicon.svg` / `favicon.ico` / `apple-touch-icon.png` |
| `.github/workflows/deploy.yml` | `carabetta.xyz` | site HTML + nginx; **not** PMTiles |

The four archives (`censo2022.pmtiles`, `censo2022_income.pmtiles`, `censo2022_deaths.pmtiles`, `hover.pmtiles`) stay on the VPS at `/var/www/carabetta.xyz/dotsbr/data/tiles/`. They are gitignored (~700MB). Upload them from a machine that already has `data/tiles/`:

```sh
cp deploy.env.example deploy.env
./deploy.sh --tiles
```

`carabetta.xyz` `./deploy.sh` does the same sync from `../dotmap/data/tiles` unless `SKIP_TILES=1` (what CI sets).

## GitHub secrets

Both repos need:

| Secret | Value |
|---|---|
| `VPS_HOST` | VPS public IP (not an SSH config alias) |
| `VPS_USER` | `root` |
| `VPS_SSH_KEY` | private key whose public half is on the VPS |
| `TRANSPARENCIA_AUTH_PASSWORD` | only on `carabetta.xyz`; omit and existing `/transparencia/` auth stays |

`workflow_dispatch` on either workflow redeploys without a new commit.

## Nginx

`/dotsbr/` is static files. `.pmtiles` must be served with `Accept-Ranges: bytes` and **without** gziping the archive body — otherwise Range `206` breaks and the map is blank. Config lives in `carabetta.xyz/nginx.carabetta.xyz.conf`.
