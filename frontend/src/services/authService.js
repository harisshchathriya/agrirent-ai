import api from "../api/axios";
import { getErrorMessage } from "./apiUtils";

export const registerUser = async (userData) => {
  try {
    const response = await api.post("/auth/register", userData);
    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(error, "Failed to register user.")
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
      getErrorMessage(error, "Invalid email or password.")
    );
  }
};

export const getCurrentUser = async () => {
  try {
    const response = await api.get("/auth/users/me");
    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(error, "Failed to load current user.")
    );
  }
};
