import { atom } from "jotai"
import { api } from "./api"

export const $densityFeatureCollection = atom(async () => {
    return api.getDensity()
});