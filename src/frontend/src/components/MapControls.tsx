import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardFooter, CardTitle } from "@/components/ui/card"
import { useAtom } from 'jotai'
import { $mapSettings } from '@/lib/stores'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AdjustFunction } from "@/lib/types"
import { Info } from "lucide-react"
import { Link } from "react-router-dom"

export default function MapControls() {
    const [mapSettings, setMapSettings] = useAtom($mapSettings);

    function getAdjustFunctionName(adjustFunction: AdjustFunction): string {
        switch (adjustFunction) {
            case AdjustFunction.NONE:
                return "No adjustment";
            case AdjustFunction.SQRT:
                return "Square Root";
            case AdjustFunction.LOG:
                return "Logarithm";
            case AdjustFunction.EXP:
                return "Exponential";
        }
    }

    return (
        <Card className="w-72 max-w-md mx-auto !border-none !shadow-none">
            <CardTitle className="text-xl font-medium text-balance text-right pr-6 mb-4">Germany population density map</CardTitle>
            <CardContent className="space-y-6">
                <div className="space-y-2 text-right">
                    <Label htmlFor="coverage" className="text-lg font-medium">
                        Coverage
                    </Label>
                    <Slider
                        id="coverage"
                        min={0}
                        max={1}
                        step={0.01}
                        value={[mapSettings.coverage]}
                        onValueChange={(value) => setMapSettings({ ...mapSettings, coverage: value[0] })}
                        className="w-full"
                    />
                    <p className="text-sm text-muted-foreground text-right">{mapSettings.coverage.toFixed(3)}</p>
                </div>

                <div className="space-y-2 text-right">
                    <Label htmlFor="opacity" className="text-lg font-medium">
                        Opacity
                    </Label>
                    <Slider
                        id="opacity"
                        min={0}
                        max={1}
                        step={0.001}
                        value={[mapSettings.opacity]}
                        onValueChange={(value) => setMapSettings({ ...mapSettings, opacity: value[0] })}
                        className="w-full"
                    />
                    <p className="text-sm text-muted-foreground text-right">{mapSettings.opacity.toFixed(3)}</p>
                </div>

                <div className="space-y-2 text-right">
                    <Label htmlFor="elevation" className="text-lg font-medium">
                        Elevation Scale
                    </Label>
                    <Slider
                        id="elevation"
                        min={1}
                        max={10000}
                        step={1}
                        value={[mapSettings.elevation]}
                        onValueChange={(value) => setMapSettings({ ...mapSettings, elevation: value[0] })}
                        className="w-full"
                    />
                    <p className="text-sm text-muted-foreground text-right">{mapSettings.elevation}</p>
                </div>

                <div className="space-y-2 text-right">
                    <Label htmlFor="detalization" className="text-lg font-medium">
                        Adjustment function
                    </Label>
                    <Select value={mapSettings.adjustFunction} onValueChange={
                        (value) => setMapSettings({ ...mapSettings, adjustFunction: value as AdjustFunction })
                    }>
                        <SelectTrigger>
                            <SelectValue placeholder="Select adjustment function" />
                        </SelectTrigger>
                        <SelectContent>
                            {[
                                AdjustFunction.NONE,
                                AdjustFunction.SQRT,
                                AdjustFunction.LOG,
                                AdjustFunction.EXP,
                            ].map((level) => (
                                <SelectItem key={level} value={level.toString()}>
                                    {getAdjustFunctionName(level)}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <div className="space-y-2 text-right">
                    <Label htmlFor="fillColor" className="text-lg font-medium">
                        Fill Color
                    </Label>
                    <div className="flex items-center space-x-2">
                        <input
                            type="color"
                            id="fillColor"
                            value={mapSettings.fillColor}
                            onChange={(e) => setMapSettings({ ...mapSettings, fillColor: e.target.value })}
                            className="w-12 h-12 rounded-md cursor-pointer"
                        />
                        <span className="text-sm font-medium">{mapSettings.fillColor}</span>
                    </div>
                </div>

            </CardContent>
            <CardFooter className="flex flex-row justify-start border-t pt-4">
                <div className="text-xs text-muted-foreground">
                    <Info className="mr-1 h-4 w-4 float-left" />
                    <span className="text-balance">
                        Source data loaded from HDX (Humanitarian Data Exchange)
                        and is provided by Meta.
                        <br/>Please read more about the data
                        <Link to="https://dataforgood.facebook.com/dfg/docs/high-resolution-population-density-maps-demographic-estimates-documentation" className="text-primary-foreground"> here</Link>.
                    </span>
                </div>
            </CardFooter>
        </Card>
    )
}