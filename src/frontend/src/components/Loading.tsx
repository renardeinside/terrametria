import { Loader } from "lucide-react";

const Loading = () => {
    return (<div className="flex flex-col space-y-4 justify-center items-center min-h-[50vh]">
        <Loader className="animate-pulse h-10 w-10" />
        <p className="font-medium tracking-tighter text-xl">
            Loading density data
        </p>
    </div>)
}
export default Loading;