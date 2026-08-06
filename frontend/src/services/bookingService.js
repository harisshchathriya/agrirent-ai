import api from "../api/axios";
import { requestData } from "./apiUtils";

export const createBooking = async (bookingData) =>
  requestData(
    () => api.post("/bookings", bookingData),
    "Failed to create booking."
  );

export const getMyBookings = async () =>
  requestData(
    () => api.get("/bookings"),
    "Failed to load bookings."
  );

export const getBookingById = async (id) =>
  requestData(
    () => api.get(`/bookings/${id}`),
    "Failed to load booking."
  );

export const updateBookingStatus = async (id, status) =>
  requestData(
    () =>
      api.put(`/bookings/${id}/status`, {
        status,
      }),
    "Failed to update booking."
  );

export const deleteBooking = async (id) =>
  requestData(
    () => api.delete(`/bookings/${id}`),
    "Failed to delete booking."
  );

export const getOwnerBookings = async () =>
  requestData(
    () => api.get("/bookings/owner/bookings"),
    "Failed to load owner bookings."
  );

export const getPendingOwnerBookings = async () =>
  requestData(
    () => api.get("/bookings/owner/bookings/pending"),
    "Failed to load pending owner bookings."
  );

export const approveBooking = async (id) =>
  requestData(
    () => api.put(`/bookings/owner/bookings/${id}/approve`),
    "Failed to approve booking."
  );

export const rejectBooking = async (id) =>
  requestData(
    () => api.put(`/bookings/owner/bookings/${id}/reject`),
    "Failed to reject booking."
  );

export const completeBooking = async (id) =>
  requestData(
    () => api.put(`/bookings/owner/bookings/${id}/complete`),
    "Failed to complete booking."
  );

export const cancelBooking = async (id) =>
  requestData(
    () =>
      api.put(`/bookings/${id}/status`, {
        status: "cancelled",
      }),
    "Failed to cancel your booking."
  );

export const cancelOwnerBooking = async (id) =>
  requestData(
    () => api.put(`/bookings/owner/bookings/${id}/cancel`),
    "Failed to cancel booking."
  );
