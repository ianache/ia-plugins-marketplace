# Validación de rutas

```text
python scripts/validate_pathmap.py --workspace <raíz> --type TRM --file business/terms/TRM-001-cliente.md
python scripts/validate_pathmap.py --workspace <raíz> --check-catalog BR
python scripts/validate_pathmap.py --workspace <raíz> --check-catalog TRM
python skills/biz-rules-modeler/scripts/rules.py check <raíz>/business/rules
python skills/biz-glossary-curator/scripts/glossary.py check <raíz>/business/terms
python skills/biz-pack-validator-publisher/scripts/check_pack.py --workspace <raíz>
```

Comprueban directorio, `type`, correspondencia nombre-`id` y correspondencia 1:1 entre documentos y catálogo CTLG. No certifican contenido ni aprobación humana.
