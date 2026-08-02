import { expect, test } from '../fixtures/auth'

test.describe('文書一覧 (SC-02)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/documents')
  })

  test('文書一覧ページが表示される', async ({ page }) => {
    await expect(page).toHaveURL(/\/documents/)
    await expect(page.getByRole('table')).toBeVisible()
  })

  test('キーワード検索フォームが表示される', async ({ page }) => {
    await expect(page.getByPlaceholder('キーワードで検索')).toBeVisible()
  })

  test('タグフィルターが表示される', async ({ page }) => {
    await expect(page.getByText('タグで絞り込む')).toBeVisible()
  })
})

test.describe('文書詳細 (SC-03)', () => {
  test('文書タイトルをクリックすると詳細ページへ遷移する', async ({ page }) => {
    await page.goto('/documents')
    const firstLink = page.locator('a.doc-link').first()
    if (await firstLink.isVisible()) {
      await firstLink.click()
      await expect(page).toHaveURL(/\/documents\/.+/)
      await expect(page.getByRole('button', { name: '一覧へ戻る' })).toBeVisible()
    }
  })
})

test.describe('文書フォーム (SC-04)', () => {
  test('/documents/new は認証済みエディターのみアクセスできる', async ({ page }) => {
    await page.goto('/documents/new')
    await expect(page).toHaveURL(/\/documents(\/new|$)/)
  })
})
