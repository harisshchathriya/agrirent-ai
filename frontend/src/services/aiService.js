import api from "../api/axios";
import { requestData } from "./apiUtils";

export const getRecommendations = (limit = 5) =>
  requestData(
    () => api.get("/ai/recommendations", { params: { limit } }),
    "Failed to load equipment recommendations."
  );

export const getDemandTrends = () =>
  requestData(
    () => api.get("/ai/demand-trends"),
    "Failed to load demand trends."
  );
