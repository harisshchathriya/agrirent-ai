import api from "../api/axios";
import { getErrorMessage } from "./apiUtils";

export const getEquipment = async () => {
  try {
    const response = await api.get("/equipment");
    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(error, "Failed to load equipment.")
    );
  }
};

export const getEquipmentById = async (id) => {
  try {
    const response = await api.get(`/equipment/${id}`);
    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(error, "Failed to load equipment details.")
    );
  }
};

export const createEquipment = async (equipmentData) => {
  try {
    const response = await api.post("/equipment", equipmentData);
    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(error, "Failed to create equipment.")
    );
  }
};

export const updateEquipment = async (id, equipmentData) => {
  try {
    const response = await api.put(`/equipment/${id}`, equipmentData);
    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(error, "Failed to update equipment.")
    );
  }
};

export const deleteEquipment = async (id) => {
  try {
    const response = await api.delete(`/equipment/${id}`);
    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(error, "Failed to delete equipment.")
    );
  }
};
