import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('tc_detail',Path(__file__).parents[1]/'scripts'/'check_tc_detail.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def test_rejects_empty_sections():
    assert mod.check('## Precondiciones\n## Datos de prueba\n## Pasos\n## Resultado esperado (oracle)\n')

def test_frontmatter_requires_automation_status_and_rejects_execution():
    base='## Precondiciones\n| PC-ID | Estado inicial requerido | Cómo comprobarlo |\n|---|---|---|\n| PC-01 | a | b |\n## Datos de prueba\n| TD-ID | Técnica/estrategia | Valor exacto |\n|---|---|---|\n| TD-01 | x | 0 |\n## Pasos\n| STEP-ID | Acción concreta | Resultado esperado observable |\n|---|---|---|\n| STEP-01 | a | b |\n## Resultado esperado (oracle)\n| OR-ID | Aserción exacta | Fuente AC/BR/API |\n|---|---|---|\n| OR-01 | a | AC-1 |\n## Postcondiciones y limpieza\n- ok\n'
    bad=lambda r:[i for i in mod.check(r) if 'automation_status' in i or 'execution' in i]
    assert bad('---\nautomation_status: MANUAL_ONLY\n---\n'+base)==[]
    assert any('execution' in i for i in bad('---\nautomation_status: MANUAL_ONLY\nexecution: manual\n---\n'+base))
    assert any('automation_status' in i for i in bad('---\nautomation_status: X\n---\n'+base))

def test_accepts_detailed_sections():
    doc='## Precondiciones\n| PC-ID | Estado inicial requerido | Cómo comprobarlo |\n|---|---|---|\n| PC-01 | estado activo | GET /status |\n## Datos de prueba\n| TD-ID | Técnica/estrategia | Valor exacto |\n|---|---|---|\n| TD-01 | boundary | 0 |\n## Pasos\n| STEP-ID | Acción concreta | Resultado esperado observable |\n|---|---|---|\n| STEP-01 | POST /items | HTTP 400 |\n## Resultado esperado (oracle)\n| OR-ID | Aserción exacta | Fuente AC/BR/API |\n|---|---|---|\n| OR-01 | HTTP 400 | AC-01 |\n## Postcondiciones y limpieza\n- Sin cambios persistentes.\n'
    assert [e for e in mod.check(doc) if e not in ('surface: missing or unsupported','Surface Target section missing','missing section: Elemento bajo prueba (Surface Target)')]==[]
