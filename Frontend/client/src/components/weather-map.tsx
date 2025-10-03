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

    // Custom marker icon
    const customIcon = L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-cyan.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
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

    // Custom marker icon
    const customIcon = L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-cyan.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
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
      <div className="gradient-card rounded-2xl p-8">
        <h2 className="font-space font-semibold text-2xl mb-6 flex items-center">
          <i className="fas fa-globe text-accent mr-3"></i>
          Interactive Earth Map
        </h2>
        
        <div className="mb-4">
          <p className="text-sm text-muted-foreground">
            <i className="fas fa-info-circle mr-2"></i>
            Click anywhere on the map to select a location. The coordinates will auto-fill in the form.
          </p>
        </div>

        {/* Map Container */}
        <div 
          ref={mapRef} 
          className="h-96 shadow-2xl rounded-lg" 
          data-testid="map-container"
          style={{ height: '400px' }}
        ></div>

        {/* Map Controls */}
        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            <i className="fas fa-mouse-pointer mr-2"></i>
            Click to pin location
          </div>
          <button 
            onClick={handleReset}
            className="px-4 py-2 bg-muted/50 hover:bg-muted rounded-lg transition-all text-sm"
            data-testid="button-reset-map"
          >
            <i className="fas fa-redo mr-2"></i>Reset
          </button>
        </div>
      </div>

      {/* Quick Location Presets */}
      <div className="gradient-card rounded-2xl p-8">
        <h3 className="font-space font-semibold text-xl mb-4">Quick Locations</h3>
        <div className="grid grid-cols-2 gap-3">
          <button 
            onClick={() => handleQuickLocation(30.0444, 31.2357, 'Cairo, Egypt')} 
            className="px-4 py-3 bg-muted/50 hover:bg-muted rounded-lg transition-all text-left"
            data-testid="button-location-cairo"
          >
            <i className="fas fa-city mr-2 text-accent"></i>
            <span className="font-medium">Cairo</span>
          </button>
          <button 
            onClick={() => handleQuickLocation(40.7128, -74.0060, 'New York, USA')} 
            className="px-4 py-3 bg-muted/50 hover:bg-muted rounded-lg transition-all text-left"
            data-testid="button-location-newyork"
          >
            <i className="fas fa-city mr-2 text-accent"></i>
            <span className="font-medium">New York</span>
          </button>
          <button 
            onClick={() => handleQuickLocation(51.5074, -0.1278, 'London, UK')} 
            className="px-4 py-3 bg-muted/50 hover:bg-muted rounded-lg transition-all text-left"
            data-testid="button-location-london"
          >
            <i className="fas fa-city mr-2 text-accent"></i>
            <span className="font-medium">London</span>
          </button>
          <button 
            onClick={() => handleQuickLocation(35.6762, 139.6503, 'Tokyo, Japan')} 
            className="px-4 py-3 bg-muted/50 hover:bg-muted rounded-lg transition-all text-left"
            data-testid="button-location-tokyo"
          >
            <i className="fas fa-city mr-2 text-accent"></i>
            <span className="font-medium">Tokyo</span>
          </button>
        </div>
      </div>
    </div>
  );
}
