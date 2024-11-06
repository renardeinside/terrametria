export type DensityPoint = {
    hex: string;
    value: number;
}



export enum AdjustFunction {
    NONE = "none",
    SQRT = "sqrt",
    LOG = "log",
    EXP = "exp",
}

export type MapSettings = {
    coverage: number;
    opacity: number;
    elevation: number;
    fillColor: string;
    detalization: string;
    adjustFunction: AdjustFunction;
}