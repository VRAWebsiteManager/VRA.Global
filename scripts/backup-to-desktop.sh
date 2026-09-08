#!/bin/bash
# Mirrors the VRA.Global site folder to a timestamped backup on the Desktop
# every time the local repo changes (new commit or pull), and keeps only the
# 2 most recent backup snapshots. Installed as git hooks post-commit/post-merge.
set -e

REPO_DIR="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"
DESKTOP_DIR="$HOME/mnt/Desktop"
TIMESTAMP=$(date "+%Y-%m-%d %-l-%M%p" | tr '[:upper:]' '[:lower:]' | sed 's/^ *//')
BACKUP_DIR="$DESKTOP_DIR/VRA Website Backup $TIMESTAMP"

mkdir -p "$BACKUP_DIR"
rsync -a --exclude='.git' --exclude='deploy-*/' --exclude='.DS_Store' "$REPO_DIR/" "$BACKUP_DIR/"

# Keep only the 2 most recent "VRA Website Backup *" folders on the Desktop
cd "$DESKTOP_DIR"
ls -dt "VRA Website Backup "* 2>/dev/null | tail -n +3 | while IFS= read -r old; do
  rm -rf "$old"
done

echo "Backed up to: $BACKUP_DIR"
