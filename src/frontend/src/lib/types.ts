import type { Feature, Geometry } from 'geojson';

export interface CountryRecord {
    cntr_id: string;
    nuts_id: string;
    area_id: number;
    density: number;
    long_label: string;
    geometry: Geometry;
    properties: {
        CNTR_CODE: string;
        COAST_TYPE?: string;
        LEVL_CODE: number;
        MOUNT_TYPE?: string;
        NAME_LATN: string;
        NUTS_ID: string;
        NUTS_NAME: string;
        URBN_TYPE?: string;
    },
    cntr_name_nat: string;
    cntr_name_engl: string;
}

export interface FeatureProps {
    density: number;
    name: string;
}

export type FeatureWithProps = Feature<Geometry, FeatureProps>;