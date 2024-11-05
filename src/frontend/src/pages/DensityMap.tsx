import Loading from "@/components/Loading";
import { Suspense, useState } from "react";
import { GeoJsonLayer } from '@deck.gl/layers';

import { LightingEffect, AmbientLight, _SunLight as SunLight, MapViewState, PickingInfo } from '@deck.gl/core';
import { Map } from 'react-map-gl/maplibre';
import DeckGL from '@deck.gl/react';
import { BASEMAP } from '@deck.gl/carto';
import { useTheme } from "@/components/theme-provider";
import { DensityFeatureCollection, FeatureProps } from "@/lib/types";
import { useAtomValue } from "jotai";
import { $densityFeatureCollection } from "@/lib/stores";

const DensityMapView: React.FC<
    { densityData: DensityFeatureCollection }
> = ({ densityData }) => {
    const { theme } = useTheme();
    const INITIAL_VIEW_STATE: MapViewState = {
        latitude: 45.1109,
        longitude: 6.6821,
        zoom: 4,
        maxZoom: 16,
        pitch: 45,
        bearing: 10
    };

    const ambientLight = new AmbientLight({
        color: [255, 255, 255],
        intensity: 1.0
    });

    const dirLight = new SunLight({
        timestamp: Date.UTC(2019, 7, 1, 22),
        color: [255, 255, 255],
        intensity: 1.0,
        _shadow: true
    });

    const [effects] = useState(() => {
        const lightingEffect = new LightingEffect({ ambientLight, dirLight });
        lightingEffect.shadowColor = [0, 0, 0, 0.5];
        return [lightingEffect];
    });

    const layers = [
        new GeoJsonLayer<FeatureProps>({
            id: 'geojson',
            data: densityData,
            opacity: 0.1,
            stroked: false,
            filled: true,
            extruded: true,
            wireframe: true,
            getElevation: f => {
                return f.properties.density * 5
            },
            getFillColor: f => {
                const density = f.properties.density;
                const r = Math.min(255, density * 10);
                const g = Math.min(255, 255 - density * 10);
                const b = 128;
                return [r, g, b];
            },
            // getLineColor: [255, 255, 255],
            pickable: true,
            autoHighlight: true,
        })
    ]

    const getTooltip = (info: PickingInfo) => {
        return info.object ? {
            html: `
                <div>Country: ${info.object.properties.name_engl}</div>
                <div>Locality: ${info.object.properties.long_label}</div>
                <div>Density per m2: ${info.object.properties.density}</div>
            `,
            style: {
                backgroundColor: theme === "dark" ? 'black' : 'white',
                color: theme === "dark" ? 'white' : 'black',
                fontSize: '12px',
                fontFamily: 'Monospace',
                padding: '4px',
            }
        } : null;
    }

    return (
        <div className="w-full mx-10">
            <div className="h-[calc(100vh-120px)] w-[calc(90vw)] relative">
                <DeckGL
                    controller={true}
                    effects={effects}
                    initialViewState={INITIAL_VIEW_STATE}
                    layers={layers}
                    getTooltip={getTooltip}
                >
                    <Map reuseMaps mapStyle={
                        theme === "dark" ? BASEMAP.DARK_MATTER : BASEMAP.POSITRON
                    } />
                </DeckGL>
            </div>
        </div>
    )

}
const DensityMapInternals = () => {
    const densityFeatureCollection = useAtomValue($densityFeatureCollection);
    return (
        <DensityMapView densityData={densityFeatureCollection} />
    )
}


const DensityMap = () => {
    return (
        <Suspense fallback={<Loading />}>
            <DensityMapInternals />
        </Suspense>
    );
}
export default DensityMap;