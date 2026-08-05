export function getErrorMessage(error, fallbackMessage) {
  return (
    error?.response?.data?.detail ||
    error?.message ||
    fallbackMessage
  );
}

export async function requestData(callback, fallbackMessage) {
  try {
    const response = await callback();
    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(error, fallbackMessage),
      { cause: error }
    );
  }
}
