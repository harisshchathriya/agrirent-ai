import api from "../api/axios";
import { getErrorMessage } from "./apiUtils";

async function request(callback, fallbackMessage) {
  try {
    const response = await callback();
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error, fallbackMessage));
  }
}

export const createBooking = async (bookingData) =>
  request(
    () => api.post("/bookings", bookingData),
    "Failed to create booking."
  );

export const getMyBookings = async () =>
  request(
    () => api.get("/bookings"),
    "Failed to load bookings."
  );

export const getBookingById = async (id) =>
  request(
    () => api.get(`/bookings/${id}`),
    "Failed to load booking."
  );

export const updateBookingStatus = async (id, status) =>
  request(
    () =>
      api.put(`/bookings/${id}/status`, {
        status,
      }),
    "Failed to update booking."
  );

export const deleteBooking = async (id) =>
  request(
    () => api.delete(`/bookings/${id}`),
    "Failed to delete booking."
  );

export const getOwnerBookings = async () =>
  request(
    () => api.get("/bookings/owner/bookings"),
    "Failed to load owner bookings."
  );

export const getPendingOwnerBookings = async () =>
  request(
    () => api.get("/bookings/owner/bookings/pending"),
    "Failed to load pending owner bookings."
  );

export const approveBooking = async (id) =>
  request(
    () => api.put(`/bookings/owner/bookings/${id}/approve`),
    "Failed to approve booking."
  );

export const rejectBooking = async (id) =>
  request(
    () => api.put(`/bookings/owner/bookings/${id}/reject`),
    "Failed to reject booking."
  );

export const completeBooking = async (id) =>
  request(
    () => api.put(`/bookings/owner/bookings/${id}/complete`),
    "Failed to complete booking."
  );

export const cancelBooking = async (id) =>
  request(
    () => api.put(`/bookings/owner/bookings/${id}/cancel`),
    "Failed to cancel booking."
  );
