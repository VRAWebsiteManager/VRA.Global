#!/bin/bash
# Mirrors the VRA.Global site folder to a timestamped snapshot inside
#   <Downloads>/VRA Website Backups/
# on every local repo change (commit or pull), keeping the 2 most recent.
# Installed as the git hooks post-commit and post-merge.
#
# The Downloads folder is located at run time rather than hardcoded, because
# this runs in two different places: on the Mac itself (where Downloads is
# ~/Downloads) and inside a Claude session's view of the Mac (where the same
# real folder appears as ~/mnt/Downloads). Both resolve to one directory.
set -e

REPO_DIR="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"

BASE=""
for cand in "$HOME/Downloads" "$HOME/mnt/Downloads"; do
  [ -d "$cand" ] && BASE="$cand" && break
done
if [ -z "$BASE" ]; then
  echo "backup skipped: no Downloads folder found" >&2
  exit 0
fi

ROOT="$BASE/VRA Website Backups"
TIMESTAMP=$(date "+%Y-%m-%d %-l-%M%p" | tr '[:upper:]' '[:lower:]' | sed 's/^ *//')
BACKUP_DIR="$ROOT/$TIMESTAMP"

mkdir -p "$BACKUP_DIR"
rsync -a --exclude='.git' --exclude='deploy-*/' --exclude='.DS_Store' "$REPO_DIR/" "$BACKUP_DIR/"

# Keep the 2 most recent snapshots. Never let pruning fail the commit:
# deleting is not always permitted from inside a Claude session.
cd "$ROOT" && ls -dt */ 2>/dev/null | tail -n +3 | while IFS= read -r old; do
  rm -rf "$old" || true
done || true

echo "Backed up to: $BACKUP_DIR"
