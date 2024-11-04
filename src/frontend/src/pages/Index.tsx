import { cn } from "@/lib/utils";
import AnimatedGridPattern from "@/components/ui/animated-grid-pattern";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

function Index() {
    return (
        <div className="relative flex flex-col space-y-4 h-[calc(90vh)] w-full items-center justify-center overflow-hidden bg-background">
            <p className="z-10 whitespace-pre-wrap text-center text-8xl font-medium tracking-tighter text-black dark:text-white">
                Terrametria
            </p>
            <p className="z-10 text-center font-normal">
                Interactive UI for population density data
            </p>

            <Link to="/map" className="z-10">
                <Button className="z-10" size={"lg"}>
                    Get Started
                </Button>
            </Link>
            <AnimatedGridPattern
                numSquares={50}
                maxOpacity={0.1}
                duration={3}
                repeatDelay={1}
                className={cn(
                    "[mask-image:radial-gradient(600px_circle_at_center,white,transparent)]",
                    "inset-x-0 inset-y-[-30%] h-[150%] skew-y-12",
                )}
            />
        </div>
    );
}

export default Index;