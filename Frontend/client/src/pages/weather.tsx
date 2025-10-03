import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { weatherQuerySchema, type WeatherQuery } from "@shared/schema";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import WeatherMap from "@/components/weather-map";

export default function Weather() {
  const { toast } = useToast();
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lng: number; name?: string } | null>(null);
  
  const form = useForm<WeatherQuery>({
    resolver: zodResolver(weatherQuerySchema),
    defaultValues: {
      latitude: 0,
      longitude: 0,
      date: new Date().toISOString().split('T')[0]
    }
  });

  const handleLocationSelect = (lat: number, lng: number) => {
    setSelectedLocation({ lat, lng, name: `Lat: ${lat}, Lng: ${lng}` });
    form.setValue('latitude', lat);
    form.setValue('longitude', lng);
  };

  const onSubmit = async (data: WeatherQuery) => {
    try {
      // In a real implementation, this would make an API call to NASA weather services
      console.log('Weather query submitted:', data);
      
      toast({
        title: "Weather Prediction Request Submitted",
        description: `Location: ${data.latitude}, ${data.longitude} | Date: ${data.date}`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to submit weather query. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Set current date as default
  useEffect(() => {
    const today = new Date().toISOString().split('T')[0];
    form.setValue('date', today);
  }, [form]);

  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-7xl mx-auto">
        
        {/* Page Header */}
        <div className="text-center mb-12">
          <h1 className="font-space font-bold text-4xl md:text-6xl mb-4 bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent" data-testid="title-weather">
            Weather Prediction Portal
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto" data-testid="text-weather-description">
            Select a location on the map or enter coordinates manually to access NASA weather predictions
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          
          {/* Left Column: Input Form */}
          <div className="space-y-6">
            
            {/* Coordinate Input Card */}
            <div className="gradient-card rounded-2xl p-8">
              <h2 className="font-space font-semibold text-2xl mb-6 flex items-center">
                <i className="fas fa-map-pin text-accent mr-3"></i>
                Location Coordinates
              </h2>
              
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                  <div className="space-y-4">
                    {/* Latitude Input */}
                    <FormField
                      control={form.control}
                      name="latitude"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="flex items-center">
                            <i className="fas fa-arrows-alt-v mr-2 text-primary"></i>
                            Latitude
                          </FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              placeholder="e.g., 30.0444"
                              step="0.0001"
                              min="-90"
                              max="90"
                              className="input-modern"
                              data-testid="input-latitude"
                              {...field}
                              onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                            />
                          </FormControl>
                          <p className="text-xs text-muted-foreground">Range: -90° to 90°</p>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Longitude Input */}
                    <FormField
                      control={form.control}
                      name="longitude"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="flex items-center">
                            <i className="fas fa-arrows-alt-h mr-2 text-primary"></i>
                            Longitude
                          </FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              placeholder="e.g., 31.2357"
                              step="0.0001"
                              min="-180"
                              max="180"
                              className="input-modern"
                              data-testid="input-longitude"
                              {...field}
                              onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                            />
                          </FormControl>
                          <p className="text-xs text-muted-foreground">Range: -180° to 180°</p>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Location Name Display */}
                    <div className="gradient-card rounded-lg p-4 flex items-center justify-between">
                      <div className="flex items-center">
                        <i className="fas fa-location-dot text-accent text-xl mr-3"></i>
                        <div>
                          <div className="text-sm text-muted-foreground">Selected Location</div>
                          <div className="font-semibold" data-testid="text-selected-location">
                            {selectedLocation?.name || "Click map to select"}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Date Input */}
                  <div className="gradient-card rounded-xl p-6">
                    <h3 className="font-space font-semibold text-xl mb-4 flex items-center">
                      <i className="fas fa-calendar-alt text-secondary mr-3"></i>
                      Query Date
                    </h3>
                    
                    <FormField
                      control={form.control}
                      name="date"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Date</FormLabel>
                          <FormControl>
                            <Input
                              type="date"
                              className="input-modern"
                              data-testid="input-date"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  {/* Submit Button */}
                  <Button 
                    type="submit"
                    className="btn-hover w-full bg-gradient-to-r from-accent to-primary text-white px-8 py-4 rounded-xl font-space font-semibold text-lg flex items-center justify-center space-x-3"
                    data-testid="button-submit-weather"
                  >
                    <i className="fas fa-cloud-sun"></i>
                    <span>Get Weather Prediction</span>
                    <i className="fas fa-arrow-right"></i>
                  </Button>
                </form>
              </Form>
            </div>
          </div>

          {/* Right Column: Interactive Map */}
          <WeatherMap 
            onLocationSelect={handleLocationSelect}
            selectedLocation={selectedLocation}
          />
        </div>

        {/* Additional Info Section */}
        <div className="mt-12 gradient-card rounded-2xl p-8">
          <h3 className="font-space font-semibold text-2xl mb-6 flex items-center">
            <i className="fas fa-satellite text-secondary mr-3"></i>
            NASA Data Sources
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="flex items-start space-x-4" data-testid="info-modis">
              <div className="bg-primary/20 p-3 rounded-lg">
                <i className="fas fa-satellite-dish text-primary text-xl"></i>
              </div>
              <div>
                <h4 className="font-semibold mb-1">MODIS Satellites</h4>
                <p className="text-sm text-muted-foreground">Real-time atmospheric data from Terra and Aqua satellites</p>
              </div>
            </div>
            <div className="flex items-start space-x-4" data-testid="info-geos">
              <div className="bg-secondary/20 p-3 rounded-lg">
                <i className="fas fa-cloud text-secondary text-xl"></i>
              </div>
              <div>
                <h4 className="font-semibold mb-1">GEOS-5 Models</h4>
                <p className="text-sm text-muted-foreground">Advanced atmospheric simulation and prediction models</p>
              </div>
            </div>
            <div className="flex items-start space-x-4" data-testid="info-archives">
              <div className="bg-accent/20 p-3 rounded-lg">
                <i className="fas fa-database text-accent text-xl"></i>
              </div>
              <div>
                <h4 className="font-semibold mb-1">Historical Archives</h4>
                <p className="text-sm text-muted-foreground">Decades of climate and weather pattern data</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
