import { expect, test } from '../fixtures/auth'

test.describe('AIチャット (SC-05)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/chat')
  })

  test('チャット画面が表示される', async ({ page }) => {
    await expect(page).toHaveURL(/\/chat/)
    await expect(page.getByRole('heading', { name: 'AIチャット' })).toBeVisible()
  })

  test('テキスト入力エリアと送信ボタンが表示される', async ({ page }) => {
    await expect(page.getByPlaceholder(/質問を入力/)).toBeVisible()
    await expect(page.getByRole('button', { name: '送信' })).toBeVisible()
  })

  test('会話クリアボタンが表示される', async ({ page }) => {
    await expect(page.getByRole('button', { name: '会話をクリア' })).toBeVisible()
  })
})
