import { useState } from "react";
import { useLocation } from "wouter";
import { Link } from "wouter";

export default function Navigation() {
  const [location] = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <nav className="relative z-10 p-4 md:p-6" data-testid="navigation">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-2 md:space-x-3">
          <i className="fas fa-satellite text-accent text-xl md:text-2xl"></i>
          <span className="font-space font-bold text-lg md:text-xl">NASA Weather</span>
        </div>
        
        {/* Desktop Navigation */}
        <div className="hidden md:flex space-x-4">
          <Link href="/" data-testid="nav-home">
            <button className={`px-4 py-2 rounded-lg transition-all hover:bg-white/10 ${location === '/' ? 'bg-white/20' : ''}`}>
              <i className="fas fa-home mr-2"></i>Home
            </button>
          </Link>
          <Link href="/weather" data-testid="nav-weather">
            <button className={`px-4 py-2 rounded-lg transition-all hover:bg-white/10 ${location === '/weather' ? 'bg-white/20' : ''}`}>
              <i className="fas fa-cloud-sun mr-2"></i>Weather
            </button>
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button 
          className="md:hidden p-2 rounded-lg hover:bg-white/10 transition-all"
          onClick={toggleMenu}
          data-testid="mobile-menu-toggle"
        >
          <i className={`fas ${isMenuOpen ? 'fa-times' : 'fa-bars'} text-xl`}></i>
        </button>
      </div>

      {/* Mobile Navigation Menu */}
      {isMenuOpen && (
        <div className="md:hidden absolute left-0 right-0 top-full bg-background/95 backdrop-blur-md border-t border-white/10 shadow-lg">
          <div className="container mx-auto p-4 space-y-2">
            <Link href="/" data-testid="nav-home-mobile">
              <button 
                className={`w-full text-left px-4 py-3 rounded-lg transition-all hover:bg-white/10 ${location === '/' ? 'bg-white/20' : ''}`}
                onClick={() => setIsMenuOpen(false)}
              >
                <i className="fas fa-home mr-3"></i>Home
              </button>
            </Link>
            <Link href="/weather" data-testid="nav-weather-mobile">
              <button 
                className={`w-full text-left px-4 py-3 rounded-lg transition-all hover:bg-white/10 ${location === '/weather' ? 'bg-white/20' : ''}`}
                onClick={() => setIsMenuOpen(false)}
              >
                <i className="fas fa-cloud-sun mr-3"></i>Weather
              </button>
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
