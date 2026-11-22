#!/usr/bin/env python3
"""Comprueba rutas y tipos declarados frente al catálogo STD-OKF-001 local."""
import json
import re
import sys
from pathlib import Path
PLUGIN = Path(__file__).resolve().parents[1]

def main() -> int:
    try:
        pathmap = json.loads((PLUGIN / "assets/pathmap.json").read_text(encoding="utf-8-sig"))
        standard = (PLUGIN / "standards/STD-OKF-001-v0.1.0-stable.md").read_text(encoding="utf-8-sig")
        approved = set(re.findall(r"(?m)^\| `?([A-Z]{2,5})`? \|", standard))
        mapped = set(pathmap["document_types"])
        for role, mapping in pathmap["catalog_role_routes"].items():
            if mapping["type"] != "CTLG" or not mapping.get("indexes"):
                raise ValueError(f"catalog_role inválido: {role}")
            mapped.add(mapping["type"])
        if mapped - approved:
            raise ValueError(f"tipos no registrados en STD-OKF-001: {sorted(mapped - approved)}")
        if set(pathmap["approved_types"]) != mapped or len(pathmap["approved_types"]) != len(set(pathmap["approved_types"])):
            raise ValueError("approved_types y rutas documentales no coinciden")
        if pathmap["operational_artifacts"]["orchestrator_root"] != ".comsatel/ux-design/runs/":
            raise ValueError("orchestrator_root debe ser .comsatel/ux-design/runs/")
        for doc_type, folder in pathmap["document_types"].items():
            if not folder.startswith("design/") or not folder.endswith("/"):
                raise ValueError(f"ruta canónica inválida para {doc_type}: {folder}")
        print("PASS: pathmap usa tipos aprobados y rutas canónicas")
        return 0
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
