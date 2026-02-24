import { expect, test } from '@playwright/test'

const apiBase = process.env.E2E_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
const appBase = process.env.E2E_BASE_URL || 'http://127.0.0.1:3000'
const bearerToken = process.env.E2E_API_BEARER_TOKEN || ''
const projectId = process.env.E2E_EDITOR_PROJECT_ID || ''

test.describe('OpenCut integration @editor-integration', () => {
  test('editor route is reachable', async ({ request }) => {
    test.skip(!projectId, 'Set E2E_EDITOR_PROJECT_ID to run editor route checks')

    const response = await request.get(`${appBase}/editor/${projectId}?diag=1`)
    expect(response.status() < 500).toBeTruthy()
  })

  test('backend contracts are reachable with bearer token', async ({ request }) => {
    test.skip(!bearerToken || !projectId, 'Set E2E_API_BEARER_TOKEN and E2E_EDITOR_PROJECT_ID to run API checks')

    const authHeaders = {
      Authorization: `Bearer ${bearerToken}`,
      'X-Request-ID': `pw_${Date.now()}`,
    }

    const me = await request.get(`${apiBase}/auth/me`, { headers: authHeaders })
    expect(me.status()).toBe(200)

    const project = await request.get(`${apiBase}/projects/${projectId}`, {
      headers: authHeaders,
    })
    expect(project.status()).toBe(200)

    const assets = await request.get(`${apiBase}/projects/${projectId}/assets?project_only=true`, {
      headers: authHeaders,
    })
    expect(assets.status()).toBe(200)
  })
})
