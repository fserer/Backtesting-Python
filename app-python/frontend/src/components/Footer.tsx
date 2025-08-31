import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-100 border-t border-gray-200 mt-auto">
      <div className="px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="text-sm text-gray-600 mb-4 md:mb-0">
            <p>&copy; 2025 TradeSigma Pro</p>
            <p className="text-xs text-gray-400">Built with ❤️ from Andorra</p>
          </div>
          <div className="flex space-x-6 text-sm text-gray-600">
            <a href="mailto:fserer@gmail.com" className="hover:text-gray-900 transition-colors">
              Contacto
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
