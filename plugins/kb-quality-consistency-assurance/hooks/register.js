// KB-QCA v1.1.0: observe-only; does not approve, rewrite or block tool calls.
// No file reads, network requests, process execution or external state writes.
// Each signal keeps its rule, time, call number and a redacted command: verbs, flags and protected branch names only.
let inspected = 0;
let alerts = [];
const MAX_ALERTS = 100;
const STATUS_ROWS = 10;
const MAX_DETAIL = 80;
const PANE = 'kb-qca-risks';
const PROTECTED_BRANCHES = ['main', 'master', 'develop'];
// Pistas de secreto o de dato sensible: URLs, usuario@host y asignaciones (token=, key=).
const SENSITIVE = /:\/\/|@|=/;
// Argumentos de cada invocación de `cmd` en la cadena (hasta ; & | o salto de línea). No ejecuta ni lee nada.
function invocations(raw, cmdSource) {
  const re = new RegExp('(?:^|[;&|(]\\s*)' + cmdSource + '\\s+([^;&|\\n]*)', 'gi');
  return [...raw.matchAll(re)].map(m => m[1].trim().split(/\s+/).filter(Boolean));
}
// rm con recursión y fuerza, con las banderas en cualquier orden o forma: -rf, -fr, -r -f, -Rf, --recursive --force.
function isDestructiveRm(raw) {
  return invocations(raw, '(?:sudo\\s+(?:-\\S+\\s+)*)?rm').some(args => {
    const flags = args.filter(a => a.startsWith('-') && a !== '--');
    const short = flags.filter(a => !a.startsWith('--')).join('').replace(/-/g, '');
    const recursive = /[rR]/.test(short) || flags.includes('--recursive');
    const force = /f/.test(short) || flags.includes('--force');
    return recursive && force;
  });
}
// git push que toca una rama protegida: main, HEAD:main, +main, refs/heads/main, --delete main, :main.
function pushesToProtected(raw) {
  return invocations(raw, 'git\\s+push').some(args =>
    args.filter(a => !a.startsWith('-')).some(ref => {
      const target = ref.replace(/^\+/, '').split(':').pop().replace(/^refs\/heads\//, '');
      return PROTECTED_BRANCHES.includes(target);
    }));
}
// Cada regla dice qué detecta, por qué importa y qué hacer. Mantener el orden: la primera que coincide da la etiqueta.
const RULES = [
  {
    id: 'R-01',
    label: 'Git force push',
    test: raw => /\bgit\s+push\b[^\n]*?(?:--force(?:-with-lease)?|\s-f(?:\s|$))/i.test(raw),
    why: 'Reescribe la historia de la rama remota y puede perder commits de otras personas.',
    action: 'Usa --force-with-lease solo en tu rama y confirma que nadie más trabaja en ella.',
  },
  {
    id: 'R-02',
    label: 'Git history rewrite',
    test: raw => /\bgit\s+(?:reset\s+--hard|filter-branch)\b/i.test(raw),
    why: 'Descarta cambios locales o reescribe commits existentes.',
    action: 'Revisa git status y git log antes; para deshacer un commit publicado, prefiere git revert.',
  },
  {
    id: 'R-03',
    label: 'Destructive filesystem command',
    test: isDestructiveRm,
    why: 'Borra archivos de forma recursiva y forzada, sin confirmación.',
    action: 'Revisa la ruta objetivo antes de ejecutar y evita -f si no es necesario.',
  },
  {
    id: 'R-04',
    label: 'Direct publish to protected branch',
    test: pushesToProtected,
    why: 'Publica directamente en una rama protegida, sin Merge Request.',
    action: 'Sube a una rama de trabajo y abre un Merge Request.',
  },
];
export function classifyRule(raw) {
  return typeof raw === 'string' ? RULES.find(rule => rule.test(raw)) ?? null : null;
}
export function classify(raw) {
  return classifyRule(raw)?.label ?? null;
}
function isProtectedTarget(word) {
  return PROTECTED_BRANCHES.includes(word.split(':').pop().replace(/^\+/, ''));
}
// Detalle seguro de un comando: verbos, banderas y ramas protegidas. El resto de argumentos se cuenta, no se muestra.
export function redact(raw, rule) {
  const segment = raw.split(/[;&|\n]/).find(part => rule.test(part)) ?? raw;
  const words = segment.trim().split(/\s+/).filter(Boolean);
  const kept = [];
  let hidden = 0;
  words.forEach((word, i) => {
    const plain = !SENSITIVE.test(word);
    const verb = i < 2 && !word.startsWith('-') && plain;
    const flag = word.startsWith('-') && plain;
    const target = plain && isProtectedTarget(word);
    if (verb || flag || target) kept.push(word);
    else hidden += 1;
  });
  const detail = kept.join(' ') + (hidden ? ` · ${hidden} argumento(s) oculto(s)` : '');
  return detail.length > MAX_DETAIL ? detail.slice(0, MAX_DETAIL - 1) + '…' : detail;
}
function inspect(event) {
  const tool = String(event?.tool || '');
  const raw = event?.command ?? event?.input?.command ?? event?.args?.command ?? '';
  // Observe only Bash command strings. The detail is redacted before it is kept.
  if (tool !== 'Bash' || typeof raw !== 'string') return null;
  const rule = classifyRule(raw);
  return rule ? { rule, detail: redact(raw, rule) } : null;
}
// Señales agrupadas por regla, la más frecuente primero.
function groups() {
  return RULES.map(rule => ({ rule, hits: alerts.filter(a => a.ruleId === rule.id) }))
    .filter(group => group.hits.length)
    .sort((a, b) => b.hits.length - a.hits.length);
}
function formatAlert(alert) {
  const time = new Date(alert.at).toLocaleTimeString('es-PE', { hour12: false });
  return `llamada #${alert.call} · ${time} · ${alert.ruleId} · ${alert.detail}`;
}
export function statusText(all = false) {
  const shown = all ? alerts : alerts.slice(-STATUS_ROWS);
  const hidden = alerts.length - shown.length;
  return [
    'KB-QCA Quality Gate Monitor — observation only',
    `Tool calls observed: ${inspected}; potential risks: ${alerts.length}`,
    ...groups().map(({ rule, hits }) => `• ${hits.length}× ${rule.label} (${rule.id}): ${rule.why} ${rule.action}`),
    ...(shown.length ? ['', `Señales ${all ? 'todas' : 'recientes'}:`, ...shown.map(a => `  ${formatAlert(a)}`)] : []),
    ...(hidden > 0 ? [`(${hidden} anteriores: /kb-quality-status all)`] : []),
    '',
    'G1 Structure | G2 References | G3 Semantics | G4 Cross-artifact | G5 Impact | G6 Publication',
    'Gate status: not loaded (no verified orchestrator run-state connection).',
    'This mod never approves or blocks publication. GitLab CI and human approvals remain authoritative.'
  ].join('\n');
}
export function register(on) {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'kb-quality-status', description: 'Show KB-QCA tool risk observations and gate handoff guidance' });
    await $.command.register({ name: 'kb-quality-risks', description: 'Open the KB-QCA risk signals pane' });
    return next(e);
  });
  on('tool.call', async ($, e, next) => {
    inspected += 1;
    const hit = inspect(e);
    if (hit) {
      alerts.push({ ruleId: hit.rule.id, call: inspected, at: Date.now(), detail: hit.detail });
      if (alerts.length > MAX_ALERTS) alerts.shift();
    }
    $.ui.invalidate('ui.render');
    return next(e);
  });
  on('command.run', { command: 'kb-quality-status' }, async (_, e) => ({
    text: statusText(String(e?.args ?? '').trim() === 'all')
  }));
  on('command.run', { command: 'kb-quality-risks' }, async $ => {
    await $.ui.open({ id: PANE, title: 'KB-QCA · señales' });
    return { text: 'Panel de señales KB-QCA abierto.' };
  });
  // Panel: observación de solo lectura. Muestra reglas, acción sugerida y las señales recientes.
  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e);
    const room = Math.max(1, (e.viewport?.rows ?? 24) - 8);
    return h(Box, { flexDirection: 'column' },
      h(Text, { dimColor: true }, `Solo observación · ${inspected} llamadas · ${alerts.length} señales`),
      ...groups().map(({ rule, hits }) => h(Box, { key: rule.id, flexDirection: 'column' },
        h(Text, { bold: true }, `${hits.length}× ${rule.label} (${rule.id})`),
        h(Text, { dimColor: true }, rule.why),
        h(Text, { dimColor: true }, `Acción: ${rule.action}`))),
      h(Text, { bold: true }, 'Señales recientes'),
      ...(alerts.length
        ? alerts.slice(-room).map(a => h(Text, { key: `${a.call}-${a.ruleId}` }, formatAlert(a)))
        : [h(Text, { dimColor: true }, 'Sin señales.')]));
  });
  on('ui.render', { component: 'Spinner' }, async ($, e, next) => {
    const [top] = groups();
    const suffix = ` · KB-QCA: ${alerts.length} risk signal(s)${top ? ` · ${top.hits.length}× ${top.rule.label}` : ''}`;
    return next({ ...e, props: { ...e.props, suffix } });
  });
}
