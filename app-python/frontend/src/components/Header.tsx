import { Zap } from "lucide-react"

interface HeaderProps {
  currentUser?: any;
  onProfileClick?: () => void;
  onLogout?: () => void;
}

export function Header({ currentUser, onProfileClick, onLogout }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">TradeSigma Pro</h1>
            <p className="text-sm text-gray-600">Advanced Backtesting Platform</p>
          </div>
        </div>
        
        {currentUser && (
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              Bienvenido,{" "}
              <button
                onClick={onProfileClick}
                className="text-blue-600 hover:text-blue-800 font-medium underline"
              >
                {currentUser.username}
              </button>
            </span>
            <button
              onClick={onLogout}
              className="px-4 py-2 text-sm bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            >
              Cerrar Sesión
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
