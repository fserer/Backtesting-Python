import { cn } from "../lib/utils"

interface MenuProps {
  currentPage: string;
  onPageChange: (page: string) => void;
}

const menuItems = [
  { id: "backtesting", label: "Backtesting" },
  { id: "strategies", label: "Estrategias" },
  { id: "hyperliquid", label: "Hyperliquid" },
  { id: "datasets", label: "Datasets" },
]

export function Menu({ currentPage, onPageChange }: MenuProps) {
  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <nav className="flex space-x-8" aria-label="Tabs">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onPageChange(item.id)}
              className={cn(
                "relative py-4 px-1 text-sm font-medium transition-all duration-300 ease-in-out",
                "hover:text-blue-600 focus:outline-none focus:text-blue-600",
                "before:absolute before:bottom-0 before:left-0 before:right-0 before:h-0.5",
                "before:bg-blue-600 before:transform before:scale-x-0 before:transition-transform before:duration-300",
                "hover:before:scale-x-100",
                currentPage === item.id ? "text-blue-600 before:scale-x-100" : "text-gray-500",
              )}
            >
              <span className="relative z-10 transition-transform duration-200 hover:scale-105">{item.label}</span>

              {/* Efecto de brillo en hover */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-50 to-transparent opacity-0 transition-opacity duration-300 hover:opacity-100 rounded-lg" />

              {/* Indicador activo con animación */}
              {currentPage === item.id && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-400 to-blue-600 animate-pulse" />
              )}
            </button>
          ))}
        </nav>
      </div>
    </div>
  )
}
