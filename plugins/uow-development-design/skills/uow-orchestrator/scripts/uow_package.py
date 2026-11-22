#!/usr/bin/env python3
"""Genera y verifica uow-package.yaml, el manifiesto cuyo digest aprueba el humano en UOW_READY_GATE. Stdlib + PyYAML.

  python uow_package.py build  --root ./management/uows --uow UOW-001
  python uow_package.py verify --root ./management/uows --uow UOW-001

El manifiesto lista UOW, UCB, UCM, UAP y UWR con su sha256 y un digest del conjunto. Cualquier cambio posterior
a un documento invalida el digest y, con él, la aprobación humana.
"""
import argparse, json, sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_uow_package import Pack, package_digest  # noqa: E402

import hashlib


def build(root, uow):
    p = Pack(root, uow)
    root = Path(root)
    docs = []
    u = p.of("UOW").get(uow)
    if not u:
        raise ValueError(f"no existe la UOW {uow}")
    members = [("UOW", u)] + [(t, c) for t in ("UCB", "UCM", "UAP", "UWR") for c in p.companion(t)[-1:]]
    missing = [t for t in ("UCB", "UCM", "UAP", "UWR") if not p.companion(t)]
    if missing:
        raise ValueError(f"paquete incompleto, faltan: {', '.join(missing)}")
    folder = root / uow
    for t, (meta, raw, path) in members:
        docs.append({"id": meta["id"], "path": Path(path).relative_to(folder).as_posix() if folder in Path(path).parents else
                     "../" + Path(path).relative_to(root).as_posix(), "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()})
    # el manifiesto vive en <root>/<uow>/; las rutas son relativas a esa carpeta
    folder.mkdir(parents=True, exist_ok=True)
    man = {"uow_id": uow, "documents": docs, "digest": package_digest(folder, docs), "approval": None}
    (folder / "uow-package.yaml").write_text(yaml.safe_dump(man, sort_keys=False, allow_unicode=True), encoding="utf8")
    return man


def verify(root, uow):
    f = Path(root) / uow / "uow-package.yaml"
    m = yaml.safe_load(f.read_text(encoding="utf8"))
    ok = package_digest(f.parent, m["documents"]) == m["digest"]
    return {"uow_id": uow, "digest": m["digest"], "valid": ok}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["build", "verify"])
    ap.add_argument("--root", default="./management/uows")
    ap.add_argument("--uow", required=True)
    a = ap.parse_args(argv)
    try:
        out = build(a.root, a.uow) if a.cmd == "build" else verify(a.root, a.uow)
    except (OSError, ValueError, KeyError, yaml.YAMLError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if a.cmd == "build" or out["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
