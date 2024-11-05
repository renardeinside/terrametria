import { FeatureCollection, Geometry } from "geojson";

export interface FeatureProps {
    density: number;
    long_label: string;
    name_engl: string;
}

export type DensityFeatureCollection = FeatureCollection<Geometry, FeatureProps>;