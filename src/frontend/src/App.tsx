import { ThemeProvider } from "@/components/theme-provider";
import { BrowserRouter } from "react-router-dom";
import { Routes, Route } from "react-router-dom";
import Index from "@/pages/Index";
import NavBar from "@/components/Navbar";
import DensityMap from "@/pages/DensityMap";
import NotFound from "@/pages/NotFound";

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <div className="max-w-screen-2xl mx-auto">
          <NavBar />

          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/map" element={<DensityMap />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </ThemeProvider>

    </BrowserRouter>
  );
}

export default App;