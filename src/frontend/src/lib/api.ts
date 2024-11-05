import axios from "axios";
import { DensityFeatureCollection } from "./types";

const apiClient = axios.create({
    baseURL: "http://localhost:6006/api",
});

export const api = {
    getDensity: async () => {
        const resp = await apiClient.get("density", {
        });
        return resp.data as DensityFeatureCollection
    }
};