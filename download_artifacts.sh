#!/bin/bash

REPO="visgwu/tampered_provenance"
ARTIFACT_NAME="provenance.intoto.jsonl"
OUTPUT_DIR="downloaded-provenance"

mkdir -p "$OUTPUT_DIR"

echo "🔍 Searching for workflow runs with uploaded provenance artifacts..."

gh run list --repo "$REPO" --limit 100 --json databaseId,status,conclusion,headSha -q '.[] | select(.status=="completed" and .conclusion=="success") | .databaseId' | while read -r run_id; do
    echo "⬇️ Downloading provenance from run ID: $run_id"
    gh run download "$run_id" --repo "$REPO" --name "$ARTIFACT_NAME-$run_id" --dir "$OUTPUT_DIR"
done

echo "✅ All done. Files are in: $OUTPUT_DIR/"