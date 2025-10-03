import { useEffect, useRef } from "react";
import L from "leaflet";

interface WeatherMapProps {
  onLocationSelect: (lat: number, lng: number) => void;
  selectedLocation?: { lat: number; lng: number } | null;
}

export default function WeatherMap({ onLocationSelect, selectedLocation }: WeatherMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    // Initialize Leaflet map
    const map = L.map(mapRef.current).setView([30.0444, 31.2357], 3);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 18
    }).addTo(map);

    // Custom marker icon using a more reliable CDN
    const customIcon = L.icon({
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });

    // Add click event to map
    map.on('click', (e) => {
      const lat = parseFloat(e.latlng.lat.toFixed(4));
      const lng = parseFloat(e.latlng.lng.toFixed(4));
      
      onLocationSelect(lat, lng);
      
      // Remove existing marker
      if (markerRef.current) {
        map.removeLayer(markerRef.current);
      }
      
      // Add new marker
      markerRef.current = L.marker([lat, lng], { icon: customIcon }).addTo(map);
      markerRef.current.bindPopup(`<strong>Selected Location</strong><br>Latitude: ${lat}<br>Longitude: ${lng}`).openPopup();
    });

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
      markerRef.current = null;
    };
  }, [onLocationSelect]);

  useEffect(() => {
    if (!mapInstanceRef.current || !selectedLocation) return;

    const { lat, lng } = selectedLocation;
    
    // Remove existing marker
    if (markerRef.current) {
      mapInstanceRef.current.removeLayer(markerRef.current);
    }

    // Custom marker icon using a more reliable CDN
    const customIcon = L.icon({
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });

    // Add marker and center map
    markerRef.current = L.marker([lat, lng], { icon: customIcon }).addTo(mapInstanceRef.current);
    markerRef.current.bindPopup(`<strong>Selected Location</strong><br>Latitude: ${lat}<br>Longitude: ${lng}`).openPopup();
    mapInstanceRef.current.setView([lat, lng], 6);
  }, [selectedLocation]);

  const handleReset = () => {
    if (!mapInstanceRef.current) return;

    mapInstanceRef.current.setView([30.0444, 31.2357], 3);
    if (markerRef.current) {
      mapInstanceRef.current.removeLayer(markerRef.current);
      markerRef.current = null;
    }
  };

  const handleQuickLocation = (lat: number, lng: number, name: string) => {
    onLocationSelect(lat, lng);
  };

  return (
    <div className="space-y-6">
      {/* Map Card */}
      <div className="gradient-card rounded-2xl p-4 md:p-6 lg:p-8">
        <h2 className="font-space font-semibold text-lg md:text-xl lg:text-2xl mb-4 md:mb-6 flex items-center">
          <i className="fas fa-globe text-accent mr-2 md:mr-3 text-lg md:text-xl"></i>
          <span className="hidden sm:inline">Interactive Earth Map</span>
          <span className="sm:hidden">Earth Map</span>
        </h2>
        
        <div className="mb-3 md:mb-4">
          <p className="text-xs md:text-sm text-muted-foreground">
            <i className="fas fa-info-circle mr-1 md:mr-2"></i>
            <span className="hidden sm:inline">Click anywhere on the map to select a location. The coordinates will auto-fill in the form.</span>
            <span className="sm:hidden">Tap to select location</span>
          </p>
        </div>

        {/* Map Container */}
        <div 
          ref={mapRef} 
          className="h-64 md:h-80 lg:h-96 shadow-2xl rounded-lg" 
          data-testid="map-container"
          style={{ height: 'clamp(250px, 50vh, 400px)' }}
        ></div>

        {/* Map Controls */}
        <div className="mt-3 md:mt-4 flex flex-col sm:flex-row items-center justify-between space-y-2 sm:space-y-0">
          <div className="text-xs md:text-sm text-muted-foreground text-center sm:text-left">
            <i className="fas fa-mouse-pointer mr-1 md:mr-2"></i>
            <span className="hidden sm:inline">Click to pin location</span>
            <span className="sm:hidden">Tap to pin</span>
          </div>
          <button 
            onClick={handleReset}
            className="px-3 md:px-4 py-2 bg-muted/50 hover:bg-muted rounded-lg transition-all text-xs md:text-sm w-full sm:w-auto"
            data-testid="button-reset-map"
          >
            <i className="fas fa-redo mr-1 md:mr-2"></i>Reset
          </button>
        </div>
      </div>

      {/* Quick Location Presets */}
      <div className="gradient-card rounded-2xl p-4 md:p-6 lg:p-8">
        <h3 className="font-space font-semibold text-lg md:text-xl mb-3 md:mb-4">Quick Locations</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 md:gap-3">
          <button 
            onClick={() => handleQuickLocation(30.0444, 31.2357, 'Cairo, Egypt')} 
            className="px-3 md:px-4 py-2 md:py-3 bg-muted/50 hover:bg-muted rounded-lg transition-all text-left"
            data-testid="button-location-cairo"
          >
            <i className="fas fa-city mr-2 text-accent text-sm md:text-base"></i>
            <span className="font-medium text-sm md:text-base">Cairo</span>
          </button>
          <button 
            onClick={() => handleQuickLocation(40.7128, -74.0060, 'New York, USA')} 
            className="px-3 md:px-4 py-2 md:py-3 bg-muted/50 hover:bg-muted rounded-lg transition-all text-left"
            data-testid="button-location-newyork"
          >
            <i className="fas fa-city mr-2 text-accent text-sm md:text-base"></i>
            <span className="font-medium text-sm md:text-base">New York</span>
          </button>
          <button 
            onClick={() => handleQuickLocation(51.5074, -0.1278, 'London, UK')} 
            className="px-3 md:px-4 py-2 md:py-3 bg-muted/50 hover:bg-muted rounded-lg transition-all text-left"
            data-testid="button-location-london"
          >
            <i className="fas fa-city mr-2 text-accent text-sm md:text-base"></i>
            <span className="font-medium text-sm md:text-base">London</span>
          </button>
          <button 
            onClick={() => handleQuickLocation(35.6762, 139.6503, 'Tokyo, Japan')} 
            className="px-3 md:px-4 py-2 md:py-3 bg-muted/50 hover:bg-muted rounded-lg transition-all text-left"
            data-testid="button-location-tokyo"
          >
            <i className="fas fa-city mr-2 text-accent text-sm md:text-base"></i>
            <span className="font-medium text-sm md:text-base">Tokyo</span>
          </button>
        </div>
      </div>
    </div>
  );
}
