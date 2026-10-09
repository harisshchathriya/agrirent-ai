import test from "node:test";
import assert from "node:assert/strict";
import {
  getDemandDisplayState,
  shouldShowEquipmentImage,
  validateOptionalImageUrl,
} from "../src/utils/equipmentPresentation.js";

test("optional image URL accepts blank, valid HTTP(S), and rejects invalid values", () => {
  assert.equal(validateOptionalImageUrl(""), "");
  assert.equal(validateOptionalImageUrl("   "), "");
  assert.equal(validateOptionalImageUrl("https://example.com/image.jpg"), "");
  assert.match(validateOptionalImageUrl("ftp://example.com/image.jpg"), /HTTP or HTTPS/);
  assert.match(validateOptionalImageUrl("not a URL"), /HTTP or HTTPS/);
  assert.match(validateOptionalImageUrl(`https://example.com/${"a".repeat(250)}`), /255 characters/);
});

test("equipment image presentation selects the placeholder for missing or failed URLs", () => {
  assert.equal(shouldShowEquipmentImage("", ""), false);
  assert.equal(shouldShowEquipmentImage(null, ""), false);
  assert.equal(shouldShowEquipmentImage("https://example.com/a.jpg", ""), true);
  assert.equal(shouldShowEquipmentImage("https://example.com/a.jpg", "https://example.com/a.jpg"), false);
});

test("demand presentation distinguishes empty, insufficient, historical, and forecast states", () => {
  assert.equal(getDemandDisplayState(null), "empty");
  assert.equal(getDemandDisplayState({ historical_period_count: 0, insufficient_history: true }), "insufficient");
  assert.equal(getDemandDisplayState({ historical_period_count: 1, insufficient_history: true }), "insufficient");
  assert.equal(getDemandDisplayState({ historical_period_count: 6, insufficient_history: false, forecast_available: false }), "historical");
  assert.equal(getDemandDisplayState({ historical_period_count: 6, forecast_available: true, forecasts: [{ category: "Heavy" }] }), "forecast");
});
