#!/usr/bin/env python3
"""Comprueba consistencia interna del mapa de salidas ssp-closure."""
import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]

def main() -> int:
    path = PLUGIN / "assets" / "pathmap.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        types = set(data["document_types"])
        if types != set(data["approved_types"]):
            raise ValueError("document_types y approved_types difieren")
        if types != {"STR", "CLS"}:
            raise ValueError(f"tipo no aprobado o faltante: {sorted(types)}")
        if set(data["artifacts"]) != types:
            raise ValueError("cada tipo debe tener una entrada artifacts")
        if data["operational_artifacts"]["orchestrator_root"] != ".comsatel/ssp-closure/runs/":
            raise ValueError("orchestrator_root debe usar la ruta .comsatel canónica")
        for doc_type, folder in data["document_types"].items():
            if not folder.startswith("management/") or not folder.endswith("/"):
                raise ValueError(f"ruta canónica inválida para {doc_type}: {folder}")
        print("PASS: pathmap consistente con STD-OKF-001 v1.9.0")
        return 0
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
