import Loading from "@/components/Loading";
import { Suspense, useState } from "react";

import { LightingEffect, AmbientLight } from '@deck.gl/core';
import { Map } from 'react-map-gl/maplibre';
import DeckGL from '@deck.gl/react';
import { BASEMAP } from '@deck.gl/carto';
import { useTheme } from "@/components/theme-provider";
import { useAtomValue } from "jotai";
import { $densityData, $mapSettings } from "@/lib/stores";
import { AdjustFunction, DensityPoint } from "@/lib/types";
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import MapControls from "@/components/MapControls";

function adjuster(value: number, adjustFunction: AdjustFunction): number {
    switch (adjustFunction) {
        case AdjustFunction.NONE:
            return value;
        case AdjustFunction.SQRT:
            return Math.sqrt(value);
        case AdjustFunction.LOG:
            return Math.log(value);
        case AdjustFunction.EXP:
            return Math.exp(value);
        default:
            throw new Error("Unknown adjust function");
    }
}

const DensityMapView: React.FC<
    { densityData: DensityPoint[] }
> = ({ densityData }) => {
    const { theme } = useTheme();
    const mapSettings = useAtomValue($mapSettings);

    const ambientLight = new AmbientLight({
        color: [255, 255, 255],
        intensity: 1.0
    });


    const [effects] = useState(() => {
        const lightingEffect = new LightingEffect({ ambientLight });
        return [lightingEffect];
    });

    const layers = [
        new H3HexagonLayer<DensityPoint>({
            id: 'h3-hexagon-layer',
            data: densityData,
            pickable: true,
            filled: true,
            extruded: true,
            elevationScale: mapSettings.elevation,
            opacity: mapSettings.opacity,
            coverage: mapSettings.coverage,
            getHexagon: (d) => d.hex,
            wireframe: false,
            getFillColor: (_) => {
                const hex = mapSettings.fillColor;
                const r = parseInt(hex.slice(1, 3), 16);
                const g = parseInt(hex.slice(3, 5), 16);
                const b = parseInt(hex.slice(5, 7), 16);
                return [r, g, b, 255];
            },
            getElevation: (d) => {
                return adjuster(d.value, mapSettings.adjustFunction);
            },
            material: {
                shininess: 100,
                ambient: 1,
                diffuse: 0.5,
            },
            updateTriggers: {
                getFillColor: [mapSettings.fillColor],
                getElevation: [mapSettings.adjustFunction]
            }
        })
    ];

    return (
        <div className="h-[calc(100vh-120px)] w-[calc(78vw)] relative">
            <DeckGL
                controller={true}
                effects={effects}
                width={"100%"}
                height={"100%"}
                initialViewState={{
                    // "geographic" center of Germany
                    latitude: 51.1657,
                    longitude: 10.4515,
                    zoom: 5.2,
                    maxZoom: 16,
                    pitch: 50,
                    bearing: -10
                }}
                layers={layers}
            >
                <Map reuseMaps mapStyle={
                    theme === "dark" ? BASEMAP.DARK_MATTER : BASEMAP.POSITRON
                } />
            </DeckGL>
        </div>
    )

}
const DensityMapInternals = () => {
    const densityData = useAtomValue($densityData);
    return (
        <div className="flex flex-row w-full">
            <DensityMapView densityData={densityData} />
            <MapControls />
        </div>
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