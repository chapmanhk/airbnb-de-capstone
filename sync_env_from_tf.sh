#!/usr/bin/env bash
set -euo pipefail

# Usage: ./sync_env_from_tf [--restart]
RESTART=0
if [[ "${1:-}" == "--restart" ]]; then RESTART=1; fi

# Paths
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${ROOT_DIR}/terraform"
ENV_FILE="${ROOT_DIR}/.env"

# Helpers
die() { echo "❌ $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

upsert_kv() {
  local key="$1" val="$2" tmp
  tmp="$(mktemp)"
  if [[ -f "$ENV_FILE" ]] && grep -q "^${key}=" "$ENV_FILE"; then
    # Replace in-place (portable: write tmp then move)
    awk -v k="$key" -v v="$val" -F= 'BEGIN{OFS="="} {if($1==k){$0=k"="v} print}' "$ENV_FILE" > "$tmp"
    mv "$tmp" "$ENV_FILE"
  else
    # Append key if not present; ensure file exists
    : > "${ENV_FILE}"
    printf "%s=%s\n" "$key" "$val" >> "$ENV_FILE"
  fi
}

# Checks
[[ -d "$TF_DIR" ]] || die "Could not find terraform directory at: $TF_DIR"
have terraform || die "Terraform not found. Install Terraform first."

# Ensure terraform has been inited (non-fatal check)
if [[ ! -d "${TF_DIR}/.terraform" ]]; then
  echo "ℹ️  Terraform not initialized. Running 'terraform init'..."
  (cd "$TF_DIR" && terraform init -input=false -no-color >/dev/null)
fi

# Read outputs (fail clearly if any missing)
cd "$TF_DIR"
RAW="$(terraform output -raw raw_data_bucket 2>/dev/null || true)"
CLEANED="$(terraform output -raw cleaned_data_bucket 2>/dev/null || true)"
MODELS="$(terraform output -raw models_bucket 2>/dev/null || true)"
PRED="$(terraform output -raw predictions_bucket 2>/dev/null || true)"
cd "$ROOT_DIR"

[[ -n "$RAW"     ]] || die "Terraform output 'raw_data_bucket' not found. Did you run 'terraform apply'?"
[[ -n "$CLEANED" ]] || die "Terraform output 'cleaned_data_bucket' not found."
[[ -n "$MODELS"  ]] || die "Terraform output 'models_bucket' not found."
[[ -n "$PRED"    ]] || die "Terraform output 'predictions_bucket' not found."

# Create .env if needed (preserves any existing secrets)
touch "$ENV_FILE"

# Upsert only the bucket keys
upsert_kv "RAW_BUCKET" "$RAW"
upsert_kv "CLEANED_BUCKET" "$CLEANED"
upsert_kv "MODELS_BUCKET" "$MODELS"
upsert_kv "PREDICTIONS_BUCKET" "$PRED"

echo "✅ Updated .env with latest Terraform outputs (keys changed):"
printf "  RAW_BUCKET=%s\n" "$RAW"
printf "  CLEANED_BUCKET=%s\n" "$CLEANED"
printf "  MODELS_BUCKET=%s\n" "$MODELS"
printf "  PREDICTIONS_BUCKET=%s\n" "$PRED"

# Optional restart (supports both docker compose syntaxes)
if [[ "$RESTART" -eq 1 ]]; then
  if have docker-compose; then
    echo "♻️  Restarting with docker-compose…"
    docker-compose down && docker-compose up -d
  else
    echo "♻️  Restarting with docker compose…"
    docker compose down && docker compose up -d
  fi
  echo "✅ Airflow restarted. Environment synced!"
fi


