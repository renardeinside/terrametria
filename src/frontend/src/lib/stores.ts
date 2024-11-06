import { atom } from "jotai"
import { api } from "./api"
import { AdjustFunction, MapSettings } from "./types";

export const $densityData = atom(async () => {
    return api.getDensity()
});

export const $mapSettings = atom({
    coverage: 0.15,
    opacity: 0.17,
    elevation: 1200,
    fillColor: "#a01818",
    adjustFunction: AdjustFunction.EXP
} as MapSettings);