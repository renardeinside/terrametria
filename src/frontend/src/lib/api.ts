import axios from "axios";
import * as aq from 'arquero';

const apiClient = axios.create({
    baseURL: "http://localhost:6006/api",
});

export const api = {
    getDensity: async () => {
        const resp = await apiClient.get("density", {
            responseType: "arraybuffer",
        });
        const rawData = new Uint8Array(resp.data);
        return aq.fromArrow(rawData)
    }
};