import axios from "axios";
import * as aq from "arquero";
import { DensityPoint } from "./types";

const apiClient = axios.create({});


if (import.meta.env.DEV) {
    apiClient.defaults.baseURL = "http://localhost:8000/api";
} else {
    apiClient.defaults.baseURL = "/api";
}

export const api = {
    getDensity: async () => {
        const resp = await apiClient.get("density", {
            responseType: "arraybuffer",
        });
        const rawData = new Uint8Array(resp.data);
        return aq.fromArrow(rawData).objects() as DensityPoint[];
    }
};