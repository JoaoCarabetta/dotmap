#!/usr/bin/env bash
# Publish the page, share card and favicons to https://carabetta.xyz/dotsbr/
# og.jpg is the WhatsApp/iMessage share card (Open Graph); without it the
# preview is title-only. Favicons sit next to the HTML so /dotsbr/favicon.ico
# matches the <link rel="icon"> tags. Tiles stay on the VPS. Pass --tiles to
# rsync local data/tiles/*.pmtiles.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ROOT_DIR}/deploy.env"
SYNC_TILES=0

for arg in "$@"; do
  case "${arg}" in
    --tiles) SYNC_TILES=1 ;;
    *)
      echo "Unknown argument: ${arg}" >&2
      echo "Usage: ./deploy.sh [--tiles]" >&2
      exit 1
      ;;
  esac
done

# Local deploys read deploy.env. GitHub Actions exports SSH_* instead.
if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi

: "${SSH_HOST:?SSH_HOST is required (deploy.env or CI environment)}"
: "${SSH_USER:?SSH_USER is required (deploy.env or CI environment)}"
: "${REMOTE_PATH:?REMOTE_PATH is required (deploy.env or CI environment)}"

SSH_TARGET="${SSH_USER}@${SSH_HOST}"

ssh_cmd() {
  if [[ -n "${SSH_IDENTITY_FILE:-}" ]]; then
    command ssh -i "${SSH_IDENTITY_FILE}" -o StrictHostKeyChecking=accept-new "$@"
  else
    command ssh "$@"
  fi
}

rsync_ssh() {
  if [[ -n "${SSH_IDENTITY_FILE:-}" ]]; then
    echo "ssh -i ${SSH_IDENTITY_FILE} -o StrictHostKeyChecking=accept-new"
  else
    echo "ssh"
  fi
}

echo "Deploying map HTML, share image and favicons to ${SSH_TARGET}:${REMOTE_PATH}"
ssh_cmd "${SSH_TARGET}" "mkdir -p ${REMOTE_PATH}"
# Same directory as the page so /dotsbr/og.jpg matches the absolute og:image
# and the relative favicon links resolve.
rsync -avz -e "$(rsync_ssh)" \
  "${ROOT_DIR}/index.html" \
  "${ROOT_DIR}/og.jpg" \
  "${ROOT_DIR}/favicon.svg" \
  "${ROOT_DIR}/favicon.ico" \
  "${ROOT_DIR}/apple-touch-icon.png" \
  "${SSH_TARGET}:${REMOTE_PATH}/"

if [[ "${SYNC_TILES}" -eq 1 ]]; then
  TILES_DIR="${DOTMAP_TILES:-${ROOT_DIR}/data/tiles}"
  if [[ ! -f "${TILES_DIR}/censo2022.pmtiles" ]]; then
    echo "Missing ${TILES_DIR}/censo2022.pmtiles — build PMTiles first." >&2
    exit 1
  fi
  echo "Syncing PMTiles from ${TILES_DIR}"
  ssh_cmd "${SSH_TARGET}" "mkdir -p ${REMOTE_PATH}/data/tiles"
  rsync -avz --progress -e "$(rsync_ssh)" \
    "${TILES_DIR}/censo2022.pmtiles" \
    "${TILES_DIR}/censo2022_income.pmtiles" \
    "${TILES_DIR}/censo2022_deaths.pmtiles" \
    "${TILES_DIR}/hover.pmtiles" \
    "${SSH_TARGET}:${REMOTE_PATH}/data/tiles/"
fi

echo "Deploy complete. Live at https://carabetta.xyz/dotsbr/"
