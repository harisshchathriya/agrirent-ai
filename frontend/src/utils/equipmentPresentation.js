export function validateOptionalImageUrl(value) {
  const imageUrl = value.trim();
  if (!imageUrl) return "";
  if (imageUrl.length > 255) {
    return "Image URL must be 255 characters or fewer.";
  }
  try {
    const parsed = new URL(imageUrl);
    if (!["http:", "https:"].includes(parsed.protocol)) throw new Error("scheme");
  } catch {
    return "Enter a valid HTTP or HTTPS image URL.";
  }
  return "";
}

export function shouldShowEquipmentImage(src, failedSrc) {
  return Boolean(src && failedSrc !== src);
}

export function getDemandDisplayState(data) {
  if (!data) return "empty";
  if (data.insufficient_history) return "insufficient";
  if (!data.historical_period_count) return "empty";
  if (data.forecast_available && data.forecasts?.length) return "forecast";
  return "historical";
}
