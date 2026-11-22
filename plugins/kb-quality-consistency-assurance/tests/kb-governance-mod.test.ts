import { expect, test } from 'claude-code/testing'

test('status command exposes observation-only policy', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }))
  await $.tool.call({ tool: 'Bash', command: 'git push --force origin main' })
  const result = await $.command.run({ command: 'kb-quality-status', args: '' })
  expect(result.text).toContain('observation only')
  expect(result.text).toContain('Git force push')
  expect(result.text).toContain('GitLab CI')
})
