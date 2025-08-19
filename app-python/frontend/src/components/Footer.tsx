import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-100 border-t border-gray-200 mt-auto">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="text-sm text-gray-600 mb-4 md:mb-0">
            <p>&copy; 2025 Backtesting App. Todos los derechos reservados.</p>
          </div>
          <div className="flex space-x-6 text-sm text-gray-600">
            <a href="#" className="hover:text-gray-900 transition-colors">
              Acerca de
            </a>
            <a href="#" className="hover:text-gray-900 transition-colors">
              Ayuda
            </a>
            <a href="#" className="hover:text-gray-900 transition-colors">
              Contacto
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
