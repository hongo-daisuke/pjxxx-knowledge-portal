import { test as base } from '@playwright/test'

/**
 * 認証済みセッションを持つテストフィクスチャ。
 * CI 環境では PLAYWRIGHT_USER / PLAYWRIGHT_PASS 環境変数からログイン情報を取得する。
 */
export const test = base.extend({
  page: async ({ page }, use) => {
    const user = process.env.PLAYWRIGHT_USER
    const pass = process.env.PLAYWRIGHT_PASS

    if (user && pass) {
      await page.goto('/login')
      await page.getByRole('button', { name: 'ログイン' }).click()
      // Cognito Hosted UI にリダイレクトされる想定
      await page.waitForURL(/amazoncognito\.com/, { timeout: 10_000 })
      await page.getByLabel('Username').fill(user)
      await page.getByLabel('Password').fill(pass)
      await page.getByRole('button', { name: 'Sign in' }).click()
      await page.waitForURL('**/documents', { timeout: 15_000 })
    }

    await use(page)
  },
})

export { expect } from '@playwright/test'
