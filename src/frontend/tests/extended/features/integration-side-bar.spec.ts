import { expect, test } from "@playwright/test";

test(
  "user should be able to see integrations in the sidebar if mvp_components is true",
  { tag: ["@release", "@api", "@workspace"] },
  async ({ page }) => {
    // await page.route("**/api/v1/config", (route) => {
    //   route.fulfill({
    //     status: 200,
    //     contentType: "application/json",
    //     body: JSON.stringify({
    //       feature_flags: {
    //         mvp_components: true,
    //       },
    //     }),
    //     headers: {
    //       "content-type": "application/json",
    //       ...route.request().headers(),
    //     },
    //   });
    // });
    await page.goto("/");
    let modalCount = 0;
    try {
      const modalTitleElement = await page?.getByTestId("modal-title");
      if (modalTitleElement) {
        modalCount = await modalTitleElement.count();
      }
    } catch (error) {
      modalCount = 0;
    }
    while (modalCount === 0) {
      await page.getByText("New Flow", { exact: true }).click();
      await page.waitForSelector('[data-testid="modal-title"]', {
        timeout: 3000,
      });
      modalCount = await page.getByTestId("modal-title")?.count();
    }
    await page.getByTestId("blank-flow").click();
    await page.waitForSelector('[data-testid="shad-sidebar"]', {
      timeout: 30000,
    });
    await expect(page.getByText("Bundles")).toBeVisible();
    await expect(page.getByText("Notion")).toBeVisible();
    await expect(page.getByText("AssemblyAI")).toBeVisible();
  },
);
