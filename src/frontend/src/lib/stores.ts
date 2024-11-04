import { atom } from "jotai"
import { api } from "./api"
import { CountryRecord, FeatureWithProps } from "./types"

export const $table = atom(async () => {
    return api.getDensity()
})

export const $countryNames = atom(async (get) => {
    const table = await get($table);
    const countries = table.select('cntr_name_engl').dedupe().objects(); // array of unique country names with format [{cntr_name_engl: 'country name'}, {cntr_name_engl: 'country name'}, ...]
    // unwrap the country names from the objects
    return countries.map((country: any) => country.cntr_name_engl) as string[];
})

export const $densityData = atom(async (get) => {
    const table = await get($table);
    const records = table.objects() as CountryRecord[];
    // console.log(records);
    const features = records.map((record) => {
        return {
            type: 'Feature',
            geometry: record.geometry,
            properties: {
                density: record.density,
                name: record.cntr_name_engl
            }
        }
    }) as FeatureWithProps[];
    console.log(features);
    return features;
});