from pathlib import Path
import re, sys, yaml
# Secciones mínimas por tipo (STD-OKF-001 v0.1.0-stable, perfil de Infraestructura).
SECTIONS = {
 "IDS": [
  "Alcance y modo",
  "Hechos observados",
  "Inferencias",
  "Incertidumbres y vacíos",
  "Fuentes y evidencia"
 ],
 "IRQ": [
  "Requisitos de infraestructura",
  "Requisitos no funcionales",
  "Restricciones",
  "Criterios de aceptación",
  "Trazabilidad"
 ],
 "IBL": [
  "Alcance y fecha de línea base",
  "Inventario de componentes",
  "Topología actual",
  "Nivel de confianza de la evidencia",
  "Brechas conocidas"
 ],
 "IIA": [
  "Cambio evaluado",
  "Componentes y consumidores afectados",
  "Compatibilidad y migración",
  "Riesgos",
  "Mitigación y rollback"
 ],
 "ITP": [
  "Alcance",
  "Topología lógica y física",
  "Redes y conectividad",
  "Zonas, alta disponibilidad y ubicación",
  "Decisiones y riesgos"
 ],
 "ICP": [
  "Demanda y supuestos de carga",
  "Dimensionamiento por componente",
  "Margen y crecimiento",
  "Límites y cuellos de botella",
  "Método de cálculo"
 ],
 "IFO": [
  "Alcance de costos",
  "Modelo de costos",
  "Estimación por componente",
  "Escenarios y sensibilidad",
  "Palancas de optimización",
  "Supuestos y exclusiones"
 ],
 "ISA": [
  "Alcance y activos",
  "Zonas y segmentación",
  "Identidad y acceso",
  "Protección de datos",
  "Monitoreo y respuesta",
  "Cumplimiento y decisiones"
 ],
 "ICM": [
  "Marco de referencia",
  "Controles",
  "Mapeo a requisitos y riesgos",
  "Brechas y excepciones",
  "Evidencia de implementación"
 ],
 "ITA": [
  "Alcance y activos",
  "Amenazas identificadas",
  "Valoración del riesgo",
  "Mitigaciones y controles",
  "Riesgo residual y aceptación"
 ],
 "IOB": [
  "Alcance y servicios",
  "Métricas, logs y trazas",
  "Alertas y umbrales",
  "Dashboards y retención",
  "Responsables y runbooks"
 ],
 "IRL": [
  "Objetivos de disponibilidad",
  "Modos de falla",
  "Redundancia y alta disponibilidad",
  "Degradación y tolerancia a fallos",
  "Pruebas de resiliencia"
 ],
 "ISD": [
  "SLI y SLO",
  "Presupuesto de error",
  "RTO y RPO",
  "Estrategia de recuperación",
  "Pruebas de DR y responsables"
 ],
 "IAC": [
  "Alcance y entornos",
  "Módulos y recursos",
  "Variables y secretos",
  "Estado y backend",
  "Validación y políticas"
 ],
 "IDP": [
  "Alcance y entornos",
  "Prerrequisitos y ventanas",
  "Pasos y orden",
  "Verificación posterior",
  "Criterios de go/no-go"
 ],
 "IRB": [
  "Disparadores",
  "Pasos de reversión",
  "Datos y estado",
  "Verificación",
  "Responsables y comunicación"
 ],
 "IAR": [
  "Alcance revisado",
  "Hallazgos",
  "Cumplimiento frente a requisitos",
  "Acciones correctivas",
  "Decisión de revisión"
 ],
 "IHO": [
  "Destinatarios y alcance",
  "Artefactos entregados",
  "Decisiones y ADR",
  "Restricciones y pendientes",
  "Aceptación"
 ],
 "IXP": [
  "Iniciativa y modo",
  "Tareas y dependencias",
  "Gates",
  "Responsables",
  "Estado general"
 ],
 "IXL": [
  "Eventos",
  "Resultados por tarea",
  "Evidencias",
  "Errores y bloqueos"
 ],
 "IGR": [
  "Gates definidos",
  "Prerrequisitos",
  "Aprobaciones",
  "Excepciones"
 ],
 "ADR": [
  "Contexto",
  "Decisión",
  "Alternativas consideradas",
  "Consecuencias",
  "Estado y revisión"
 ]
}
def validate(path):
    s=Path(path).read_text(encoding="utf8").replace("\r\n","\n")
    m=re.match(r"\A---\n(.*?)\n---\n",s,re.S)
    if not m: raise ValueError("Missing frontmatter")
    data=yaml.safe_load(m.group(1))
    if not isinstance(data,dict): raise ValueError("Missing frontmatter")
    for k in ("type","id","title","description","version","status","owner","classification","tags","generated","sources","pack","skill"):
        if k not in data: raise ValueError("Missing "+k)
    if data["type"] not in SECTIONS: raise ValueError("Unapproved type "+str(data["type"]))
    if data["status"] not in ("draft","stable","deprecated"): raise ValueError("Invalid status")
    if "by" not in data["generated"] or "at" not in data["generated"]: raise ValueError("Invalid generated")
    if "{{" in s: raise ValueError("Unrendered template placeholders")
    body=s[m.end():]
    for h in SECTIONS[data["type"]]:
        if not re.search(r"^## "+re.escape(h)+r"\s*$",body,re.M): raise ValueError("Missing section: "+h)
    return True
if __name__=="__main__":
    validate(sys.argv[1]); print("VALID")
