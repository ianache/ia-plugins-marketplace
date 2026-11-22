// Ejecutable con `node tests/mod-risk-patterns.test.mjs` (sin dependencias). Cubre los detectores, la redacción y el estado del Mod (D-19).
import assert from 'node:assert/strict';
import { classify, classifyRule, redact, register, statusText } from '../hooks/register.js';

const RM = 'Destructive filesystem command', PUSH = 'Direct publish to protected branch';
const alertas = {
  'rm -rf x': RM, 'rm -fr x': RM, 'rm -r -f x': RM, 'rm -f -r x': RM, 'rm -Rf x': RM, 'rm -fR x': RM,
  'rm --recursive --force x': RM, 'rm -r --force x': RM, 'cd a && rm -fr b': RM, 'sudo rm -fr /tmp/x': RM, 'ls; rm -r -f x': RM,
  'git push origin main': PUSH, 'git push origin master': PUSH, 'git push origin develop': PUSH, 'git push origin HEAD:main': PUSH,
  'git push origin +main': PUSH, 'git push origin --delete main': PUSH, 'git push --delete origin main': PUSH, 'git push origin :main': PUSH,
  'git push origin HEAD:refs/heads/main': PUSH, 'git push origin refs/heads/master': PUSH, 'git push origin feature/x:main': PUSH,
  'git push --force origin x': 'Git force push', 'git push -f': 'Git force push', 'git reset --hard HEAD~1': 'Git history rewrite',
};
const limpios = ['rm -r x', 'rm -f x', 'rm x', 'ls -la', 'git status', 'git push origin feature/x', 'git push origin mainline',
  'git push origin feature/main', 'git push origin HEAD:feature/x', 'git push', 'echo rm -rf', 'git log --oneline'];
for (const [cmd, label] of Object.entries(alertas)) assert.equal(classify(cmd), label, cmd);
for (const cmd of limpios) assert.equal(classify(cmd), null, cmd);
assert.equal(classify(42), null);

// Cada regla tiene id, motivo y acción; la coincidencia devuelve la regla completa.
assert.equal(classifyRule('rm -rf x').id, 'R-03');
assert.equal(classifyRule('git push -f').id, 'R-01');
assert.ok(classifyRule('rm -rf x').why && classifyRule('rm -rf x').action);

// La redacción no muestra URLs, credenciales ni rutas; cuenta lo que oculta.
const forzado = 'git push https://usuario:TOKEN@host/repo.git --force origin main';
const detalle = redact(forzado, classifyRule(forzado));
assert.ok(!detalle.includes('TOKEN') && !detalle.includes('https') && !detalle.includes('host'), detalle);
assert.match(detalle, /--force/);
assert.match(detalle, /main/);
const borrado = redact('rm -rf /tmp/secreto', classifyRule('rm -rf /tmp/secreto'));
assert.ok(!borrado.includes('secreto'), borrado);
assert.match(borrado, /1 argumento\(s\) oculto\(s\)/);

// Estado: agrupado por regla, con la explicación y el conteo; la lista completa solo con `all`.
const handlers = {};
register((event, ...rest) => { (handlers[event] ??= []).push(rest.at(-1)); });
const ui = { invalidate() {} };
const observe = async command => handlers['tool.call'][0]({ ui }, { tool: 'Bash', command }, async e => e);
await observe('rm -rf a');
await observe('rm -rf b');
await observe('git push --force origin main');
const resumen = statusText();
assert.match(resumen, /2× Destructive filesystem command \(R-03\)/);
assert.match(resumen, /1× Git force push \(R-01\)/);
assert.match(resumen, /observation only/);
assert.match(resumen, /GitLab CI/);

// Límite: se conservan las últimas 100 señales y el total queda visible.
for (let i = 0; i < 110; i += 1) await observe('rm -rf z');
assert.match(statusText(), /potential risks: 100/);
assert.match(statusText(true), /Señales todas:/);

console.log(`OK: ${Object.keys(alertas).length} comandos detectados, ${limpios.length} sin alerta, redacción y estado verificados`);
