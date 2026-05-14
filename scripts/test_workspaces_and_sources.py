#!/usr/bin/env python3
"""
Test script for Workspace and Source API endpoints.
Run with: python scripts/test_workspaces_and_sources.py
Requires: API running at http://localhost:8000, PostgreSQL with tables created
"""

import urllib.request
import urllib.error
import json
import os
import sys

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def request(method: str, path: str, data: dict | None = None) -> dict | list:
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}")
        sys.exit(1)


def main():
    print("=== 1. Health check ===")
    health = request("GET", "/health")
    print(json.dumps(health, indent=2))
    assert health["status"] == "ok"

    print("\n=== 2. Create a workspace ===")
    workspace = request("POST", "/workspaces", {"name": "Test Project", "description": "A test workspace"})
    print(json.dumps(workspace, indent=2, default=str))
    workspace_id = workspace["id"]

    print("\n=== 3. List workspaces ===")
    workspaces = request("GET", "/workspaces")
    print(json.dumps(workspaces, indent=2, default=str))

    print("\n=== 4. Create a text source ===")
    text_source = request(
        "POST",
        "/sources/text",
        {
            "workspace_id": workspace_id,
            "title": "Sample notes",
            "raw_text": "Sample document text. " * 120,
        },
    )
    print(json.dumps(text_source, indent=2, default=str))

    print("\n=== 5. Create a URL source ===")
    url_source = request(
        "POST",
        "/sources/url",
        {
            "workspace_id": workspace_id,
            "title": "Example",
            "url": "https://example.com",
        },
    )
    print(json.dumps(url_source, indent=2, default=str))

    print("\n=== 6. List sources in the workspace ===")
    sources = request("GET", f"/sources?workspace_id={workspace_id}")
    print(json.dumps(sources, indent=2, default=str))

    print("\n=== 7. Get text source details ===")
    source_detail = request("GET", f"/sources/{text_source['id']}")
    print(json.dumps(source_detail, indent=2, default=str))
    assert source_detail["chunk_count"] > 0

    print("\n=== 8. List text source chunks ===")
    chunks = request("GET", f"/chunks?source_id={text_source['id']}")
    print(json.dumps(chunks, indent=2, default=str))
    assert len(chunks) == source_detail["chunk_count"]

    print("\n=== 9. Delete URL source ===")
    request("DELETE", f"/sources/{url_source['id']}")
    print("Deleted URL source")

    print("\n=== All tests completed successfully ===")


if __name__ == "__main__":
    main()
