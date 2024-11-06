import { Button } from "@/components/ui/button"
import { Ghost } from 'lucide-react'
import { Link } from "react-router-dom"

export default function NotFound() {
    return (
        <div className="flex flex-col items-center justify-center h-[60vh] bg-background text-foreground">
            <div className="text-center space-y-5">
                <div className="flex justify-center space-x-2 text-primary">
                    <Ghost className="h-24 w-24" />
                </div>
                <h1 className="text-4xl font-bold">404 - Page Not Found</h1>
                <p className="text-xl text-muted-foreground">Oops! The page you're looking for has vanished into thin air.</p>
                <Button asChild className="mt-8">
                    <Link to="/">
                        Back to starting page
                    </Link>
                </Button>
            </div>
        </div>
    )
}