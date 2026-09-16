import { expect, test } from '@playwright/test';

test('dashboard demo flow works end to end', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'RiskLens AI' })).toBeVisible();
  await expect(page.getByText('Live Transaction Analyzer')).toBeVisible();

  await page.getByRole('button', { name: 'Safe transaction', exact: true }).click();
  await page.getByRole('button', { name: 'Analyze Transaction' }).click();
  await expect(page.locator('.result')).toContainText('LOW');
  await expect(page.locator('.result')).toContainText('APPROVE');

  await page.getByRole('button', { name: 'Suspicious transaction', exact: true }).click();
  await page.getByRole('button', { name: 'Analyze Transaction' }).click();
  await expect(page.locator('.result')).toContainText('MEDIUM');

  await page.getByRole('button', { name: 'Highly suspicious transaction', exact: true }).click();
  await page.getByRole('button', { name: 'Analyze Transaction' }).click();
  await expect(page.locator('.result')).toContainText('HIGH');
  await expect(page.locator('.result')).toContainText('REVIEW / BLOCK');
  await expect(page.locator('.result li').first()).toBeVisible();

  await expect(page.getByRole('heading', { name: 'Recent Transactions' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'High-Risk Alerts' })).toBeVisible();
  await expect(page.locator('tbody tr').first()).toBeVisible();
  await page.locator('tbody tr').first().click();
  await expect(page.getByText('Transaction details')).toBeVisible();
  await expect(page.getByText('Recommended action')).toBeVisible();
});
