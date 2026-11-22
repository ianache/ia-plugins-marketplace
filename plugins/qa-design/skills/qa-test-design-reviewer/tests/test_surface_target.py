import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('tc',Path(__file__).parents[1]/'scripts/check_tc_detail.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def make(kind,fields):
    rows='\n'.join(f'| {f} | value-{f} |' for f in fields)
    return f"---\nsurface: {kind}\nsurface_target_id: T-01\n---\n## Elemento bajo prueba (Surface Target)\n| Campo | Valor verificable |\n|---|---|\n| Surface | {kind} |\n| Producto / aplicación / servicio | app |\n| Elemento bajo prueba | element |\n| Ambiente / versión / build | QA-3 |\n| Acceso / invocación | route |\n| Contrato o especificación | contract@1 |\n### Detalles específicos del Surface\n| Atributo | Valor |\n|---|---|\n{rows}\n"
def test_all_surfaces():
    for k,f in m.SURFACE_FIELDS.items():assert m.check_surface(make(k,f))==[],k
def test_missing_endpoint():
    assert any('endpoint_path' in e for e in m.check_surface(make('API',[f for f in m.SURFACE_FIELDS['API'] if f!='endpoint_path'])))
def test_missing_web_component():
    assert any('component_id' in e for e in m.check_surface(make('WEB',[f for f in m.SURFACE_FIELDS['WEB'] if f!='component_id'])))
def test_placeholder():
    assert m.check_surface(make('API',m.SURFACE_FIELDS['API']).replace('value-endpoint_path','<endpoint>'))
