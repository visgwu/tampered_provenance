#!/bin/bash

REPO="visgwu/tampered_provenance"
ARTIFACT_NAME="provenance.intoto.jsonl"
OUTPUT_DIR="downloaded-provenance"

mkdir -p "$OUTPUT_DIR"

echo "🔍 Searching for workflow runs with uploaded provenance artifacts..."

gh run list --repo "$REPO" --limit 100 --json databaseId,status,conclusion,headSha -q '.[] | select(.status=="completed" and .conclusion=="success") | .databaseId' | while read -r run_id; do
    echo "⬇️ Downloading provenance from run ID: $run_id"
    
    TEMP_DIR="$(mktemp -d)"
    gh run download "$run_id" --repo "$REPO" --name "$ARTIFACT_NAME" --dir "$TEMP_DIR"
    
    # Rename and move the artifact file
    if [ -f "$TEMP_DIR/$ARTIFACT_NAME" ]; then
        mv "$TEMP_DIR/$ARTIFACT_NAME" "$OUTPUT_DIR/${ARTIFACT_NAME%.jsonl}-$run_id.jsonl"
    else
        echo "⚠️ Artifact not found for run ID: $run_id"
    fi
    
    rm -rf "$TEMP_DIR"
done

echo "✅ All done. Files are in: $OUTPUT_DIR/"
