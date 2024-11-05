import Loading from "@/components/Loading";
import { Suspense, useState } from "react";
import { GeoJsonLayer } from '@deck.gl/layers';

import { LightingEffect, AmbientLight, _SunLight as SunLight, MapViewState } from '@deck.gl/core';
import { Map } from 'react-map-gl/maplibre';
import DeckGL from '@deck.gl/react';
import { BASEMAP } from '@deck.gl/carto';
import { useTheme } from "@/components/theme-provider";
import { FeatureProps } from "@/lib/types";

const DensityMapView = () => {
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
            data: 'http://0.0.0.0:6006/api/density',
            opacity: 0.8,
            stroked: false,
            filled: true,
            extruded: true,
            wireframe: true,
            getElevation: f => f.properties.density * 100,
            getLineColor: [255, 255, 255],
        })
    ]

    return (
        <div className="w-full mx-10">
            <div className="h-[calc(100vh-120px)] w-[calc(90vw)] relative rounded-md">
                <DeckGL
                    controller={true}
                    effects={effects}
                    initialViewState={INITIAL_VIEW_STATE}
                    layers={layers}
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

    return (
        <DensityMapView />
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