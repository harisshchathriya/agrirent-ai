import api from "../api/axios";
import { requestData } from "./apiUtils";

export const getEquipment = async () =>
  requestData(
    () => api.get("/equipment"),
    "Failed to load equipment."
  );

export const getEquipmentById = async (id) =>
  requestData(
    () => api.get(`/equipment/${id}`),
    "Failed to load equipment details."
  );

export const createEquipment = async (equipmentData) =>
  requestData(
    () => api.post("/equipment", equipmentData),
    "Failed to create equipment."
  );

export const updateEquipment = async (id, equipmentData) =>
  requestData(
    () => api.put(`/equipment/${id}`, equipmentData),
    "Failed to update equipment."
  );

export const deleteEquipment = async (id) =>
  requestData(
    () => api.delete(`/equipment/${id}`),
    "Failed to delete equipment."
  );
