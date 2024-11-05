import axios from "axios";
import { FeatureCollection, Geometry } from "geojson";
import { FeatureProps } from "./types";

const apiClient = axios.create({
    baseURL: "http://localhost:6006/api",
});

export const api = {
    getDensity: async () => {
        const resp = await apiClient.get("density", {
        });
        return resp.data as FeatureCollection<Geometry, FeatureProps>
    }
};