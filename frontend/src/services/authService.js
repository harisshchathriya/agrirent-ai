import api from "../api/axios";
import {
  getErrorMessage,
  requestData,
} from "./apiUtils";

export const registerUser = async (userData) => {
  try {
    const response = await api.post("/auth/register", userData);
    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(error, "Failed to register user."),
      { cause: error }
    );
  }
};

export const loginUser = async (email, password) => {
  const formData = new URLSearchParams();

  formData.append("username", email);
  formData.append("password", password);

  try {
    const response = await api.post(
      "/auth/login",
      formData,
      {
        headers: {
          "Content-Type":
            "application/x-www-form-urlencoded",
        },
      }
    );

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(error, "Invalid email or password."),
      { cause: error }
    );
  }
};

export const requestPasswordReset = async (email) =>
  requestData(
    () => api.post("/auth/forgot-password", { email }),
    "Unable to request a password reset."
  );

export const resetPassword = async (token, newPassword) =>
  requestData(
    () => api.post("/auth/reset-password", {
      token,
      new_password: newPassword,
    }),
    "Invalid or expired password reset link."
  );

export const getCurrentUser = async () =>
  requestData(
    () => api.get("/auth/users/me"),
    "Failed to load current user."
  );
