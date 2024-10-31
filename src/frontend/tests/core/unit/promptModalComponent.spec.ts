import { expect, test } from "@playwright/test";

test("PromptTemplateComponent", async ({ page }) => {
  await page.goto("/");
  await page.waitForSelector('[data-testid="mainpage_title"]', {
    timeout: 30000,
  });

  await page.waitForSelector('[id="new-project-btn"]', {
    timeout: 30000,
  });

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
    await page.waitForTimeout(3000);
    modalCount = await page.getByTestId("modal-title")?.count();
  }
  await page.waitForSelector('[data-testid="blank-flow"]', {
    timeout: 30000,
  });
  await page.getByTestId("blank-flow").click();
  await page.waitForSelector('[data-testid="extended-disclosure"]', {
    timeout: 30000,
  });
  await page.getByTestId("extended-disclosure").click();
  await page.getByPlaceholder("Search").click();
  await page.getByPlaceholder("Search").fill("prompt");

  await page.waitForTimeout(1000);

  await page
    .locator('//*[@id="promptsPrompt"]')
    .dragTo(page.locator('//*[@id="react-flow-id"]'));
  await page.mouse.up();
  await page.mouse.down();
  await page.getByTestId("fit_view").click();
  await page.getByTestId("zoom_out").click();
  await page.getByTestId("zoom_out").click();
  await page.getByTestId("zoom_out").click();
  await page.getByTestId("promptarea_prompt_template").click();

  await page
    .getByTestId("modal-promptarea_prompt_template")
    .fill("{prompt} example {prompt1}");

  let value = await page
    .getByTestId("modal-promptarea_prompt_template")
    .inputValue();

  if (value != "{prompt} example {prompt1}") {
    expect(false).toBeTruthy();
  }

  let valueBadgeOne = await page.locator('//*[@id="badge0"]').innerText();
  if (valueBadgeOne != "prompt") {
    expect(false).toBeTruthy();
  }

  let valueBadgeTwo = await page.locator('//*[@id="badge1"]').innerText();
  if (valueBadgeTwo != "prompt1") {
    expect(false).toBeTruthy();
  }

  await page.getByTestId("genericModalBtnSave").click();

  await page.getByTestId("textarea_str_prompt").click();
  await page.getByTestId("textarea_str_prompt").fill("prompt_value_!@#!@#");

  value = await page.getByTestId("textarea_str_prompt").inputValue();

  if (value != "prompt_value_!@#!@#") {
    expect(false).toBeTruthy();
  }

  await page.getByTestId("div-generic-node").click();

  await page.getByTestId("more-options-modal").click();
  await page.getByTestId("save-button-modal").click();

  const replace = await page.getByTestId("replace-button").isVisible();

  if (replace) {
    await page.getByTestId("replace-button").click();
  }

  await page.getByTestId("textarea_str_prompt1").click();
  await page
    .getByTestId("textarea_str_prompt1")
    .fill("prompt_name_test_123123!@#!@#");

  value = await page.getByTestId("textarea_str_prompt1").inputValue();

  if (value != "prompt_name_test_123123!@#!@#") {
    expect(false).toBeTruthy();
  }

  await page.getByTestId("more-options-modal").click();
  await page.getByTestId("advanced-button-modal").click();

  value =
    (await page.locator('//*[@id="textarea_str_edit_prompt"]').inputValue()) ??
    "";

  if (value != "prompt_value_!@#!@#") {
    expect(false).toBeTruthy();
  }

  value =
    (await page.locator('//*[@id="textarea_str_edit_prompt1"]').inputValue()) ??
    "";

  if (value != "prompt_name_test_123123!@#!@#") {
    expect(false).toBeTruthy();
  }

  value = await page
    .locator('//*[@id="promptarea_prompt_edit_template"]')
    .innerText();

  if (value != "{prompt} example {prompt1}") {
    expect(false).toBeTruthy();
  }

  await page
    .getByTestId(
      "button_open_text_area_modal_textarea_str_edit_prompt1_advanced",
    )
    .click();
  await page
    .getByTestId("text-area-modal")
    .fill("prompt_edit_test_12312312321!@#$");

  await page.getByText("Finish Editing", { exact: true }).click();

  await page
    .getByTestId(
      "button_open_text_area_modal_textarea_str_edit_prompt_advanced",
    )
    .nth(0)
    .click();
  await page
    .getByTestId("text-area-modal")
    .fill("prompt_edit_test_44444444444!@#$");

  await page.getByText("Finish Editing", { exact: true }).click();

  await page.locator('//*[@id="showtemplate"]').click();
  expect(await page.locator('//*[@id="showtemplate"]').isChecked()).toBeFalsy();

  await page.locator('//*[@id="showprompt"]').click();
  expect(await page.locator('//*[@id="showprompt"]').isChecked()).toBeFalsy();

  await page.locator('//*[@id="showprompt1"]').click();
  expect(await page.locator('//*[@id="showprompt1"]').isChecked()).toBeFalsy();

  await page.locator('//*[@id="showtemplate"]').click();
  expect(
    await page.locator('//*[@id="showtemplate"]').isChecked(),
  ).toBeTruthy();

  await page.locator('//*[@id="showprompt"]').click();
  expect(await page.locator('//*[@id="showprompt"]').isChecked()).toBeTruthy();

  await page.locator('//*[@id="showprompt1"]').click();
  expect(await page.locator('//*[@id="showprompt1"]').isChecked()).toBeTruthy();

  await page.locator('//*[@id="showtemplate"]').click();
  expect(await page.locator('//*[@id="showtemplate"]').isChecked()).toBeFalsy();

  await page.locator('//*[@id="showprompt"]').click();
  expect(await page.locator('//*[@id="showprompt"]').isChecked()).toBeFalsy();

  await page.locator('//*[@id="showprompt1"]').click();
  expect(await page.locator('//*[@id="showprompt1"]').isChecked()).toBeFalsy();

  await page.locator('//*[@id="showtemplate"]').click();
  expect(
    await page.locator('//*[@id="showtemplate"]').isChecked(),
  ).toBeTruthy();

  await page.locator('//*[@id="showprompt"]').click();
  expect(await page.locator('//*[@id="showprompt"]').isChecked()).toBeTruthy();

  await page.getByText("Close").last().click();

  await page.getByTestId("more-options-modal").click();
  await page.getByTestId("advanced-button-modal").click();

  await page.locator('//*[@id="showprompt1"]').click();
  expect(await page.locator('//*[@id="showprompt1"]').isChecked()).toBeTruthy();

  value =
    (await page.locator('//*[@id="textarea_str_edit_prompt"]').inputValue()) ??
    "";

  if (value != "prompt_edit_test_44444444444!@#$") {
    expect(false).toBeTruthy();
  }

  value =
    (await page.locator('//*[@id="textarea_str_edit_prompt1"]').inputValue()) ??
    "";

  if (value != "prompt_edit_test_12312312321!@#$") {
    expect(false).toBeTruthy();
  }

  value = await page
    .locator('//*[@id="promptarea_prompt_edit_template"]')
    .innerText();

  if (value != "{prompt} example {prompt1}") {
    expect(false).toBeTruthy();
  }
});
