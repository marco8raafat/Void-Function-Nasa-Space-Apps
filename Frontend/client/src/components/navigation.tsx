import { useLocation } from "wouter";
import { Link } from "wouter";

export default function Navigation() {
  const [location] = useLocation();

  return (
    <nav className="relative z-10 p-6" data-testid="navigation">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <i className="fas fa-satellite text-accent text-2xl"></i>
          <span className="font-space font-bold text-xl">NASA Weather</span>
        </div>
        <div className="flex space-x-4">
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
      </div>
    </nav>
  );
}
