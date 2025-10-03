import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { weatherQuerySchema, type WeatherQuery, type WeatherPredictionResponse } from "@shared/schema";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import WeatherMap from "@/components/weather-map";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Weather() {
  const { toast } = useToast();
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lng: number; name?: string } | null>(null);
  const [prediction, setPrediction] = useState<WeatherPredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [mlStatus, setMlStatus] = useState<"checking" | "online" | "offline">("checking");
  
  const form = useForm<WeatherQuery>({
    resolver: zodResolver(weatherQuerySchema),
    defaultValues: {
      latitude: 0,
      longitude: 0,
      date: new Date().toISOString().split('T')[0]
    }
  });

  // Check ML backend status on mount
  useEffect(() => {
    checkMlStatus();
  }, []);

  const checkMlStatus = async () => {
    try {
      const response = await fetch('/api/ml-status');
      if (response.ok) {
        setMlStatus("online");
      } else {
        setMlStatus("offline");
      }
    } catch (error) {
      setMlStatus("offline");
    }
  };

  const handleLocationSelect = (lat: number, lng: number) => {
    setSelectedLocation({ lat, lng, name: `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}` });
    form.setValue('latitude', lat);
    form.setValue('longitude', lng);
  };

  const onSubmit = async (data: WeatherQuery) => {
    setIsLoading(true);
    setPrediction(null);
    
    try {
      // Parse the date
      const dateObj = new Date(data.date);
      const day = dateObj.getDate();
      const month = dateObj.getMonth() + 1; // JavaScript months are 0-indexed
      const year = dateObj.getFullYear();

      // Call the prediction API
      const response = await fetch(
        `/api/predict?lat=${data.latitude}&lon=${data.longitude}&day=${day}&month=${month}&year=${year}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to get prediction");
      }

      const result: WeatherPredictionResponse = await response.json();
      setPrediction(result);

      toast({
        title: "Prediction Complete ✓",
        description: result.rain_predicted === 1 
          ? `High chance of rain (${(result.rain_probability * 100).toFixed(1)}%)`
          : `Low chance of rain (${(result.rain_probability * 100).toFixed(1)}%)`,
      });
    } catch (error) {
      console.error("Prediction error:", error);
      toast({
        title: "Prediction Failed",
        description: error instanceof Error ? error.message : "Please ensure the ML backend is running",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Set current date as default
  useEffect(() => {
    const today = new Date().toISOString().split('T')[0];
    form.setValue('date', today);
  }, [form]);

  return (
    <div className="container mx-auto px-4 md:px-6 py-8 md:py-12">
      <div className="max-w-7xl mx-auto">
        
        {/* Page Header */}
        <div className="text-center mb-8 md:mb-12">
          <h1 className="font-space font-bold text-2xl sm:text-3xl md:text-4xl lg:text-6xl mb-3 md:mb-4 bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent" data-testid="title-weather">
            Weather Prediction Portal
          </h1>
          <p className="text-sm md:text-base lg:text-lg text-muted-foreground max-w-2xl mx-auto px-4" data-testid="text-weather-description">
            Select a location on the map or enter coordinates manually to access NASA weather predictions
          </p>
          
          {/* ML Backend Status Badge */}
          <div className="mt-4 flex justify-center">
            <Badge variant={mlStatus === "online" ? "default" : mlStatus === "offline" ? "destructive" : "secondary"}>
              <i className={`fas fa-circle mr-2 ${mlStatus === "online" ? "text-green-500" : "text-red-500"}`}></i>
              ML Backend: {mlStatus === "checking" ? "Checking..." : mlStatus === "online" ? "Online" : "Offline"}
            </Badge>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-6 md:gap-8">
          
          {/* Left Column: Input Form */}
          <div className="space-y-4 md:space-y-6">
            
            {/* Coordinate Input Card */}
            <div className="gradient-card rounded-2xl p-4 md:p-6 lg:p-8">
              <h2 className="font-space font-semibold text-lg md:text-xl lg:text-2xl mb-4 md:mb-6 flex items-center">
                <i className="fas fa-map-pin text-accent mr-2 md:mr-3 text-lg md:text-xl"></i>
                <span className="hidden sm:inline">Location Coordinates</span>
                <span className="sm:hidden">Coordinates</span>
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
                    <div className="gradient-card rounded-lg p-3 md:p-4 flex items-center justify-between">
                      <div className="flex items-center min-w-0 flex-1">
                        <i className="fas fa-location-dot text-accent text-lg md:text-xl mr-2 md:mr-3 flex-shrink-0"></i>
                        <div className="min-w-0 flex-1">
                          <div className="text-xs md:text-sm text-muted-foreground">Selected Location</div>
                          <div className="font-semibold text-sm md:text-base truncate" data-testid="text-selected-location">
                            {selectedLocation?.name || "Click map to select"}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Date Input */}
                  <div className="gradient-card rounded-xl p-4 md:p-6">
                    <h3 className="font-space font-semibold text-lg md:text-xl mb-3 md:mb-4 flex items-center">
                      <i className="fas fa-calendar-alt text-secondary mr-2 md:mr-3 text-lg md:text-xl"></i>
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
                    disabled={isLoading || mlStatus === "offline"}
                    className="btn-hover w-full bg-gradient-to-r from-accent to-primary text-white px-6 md:px-8 py-3 md:py-4 rounded-xl font-space font-semibold text-base md:text-lg flex items-center justify-center space-x-2 md:space-x-3 disabled:opacity-50 disabled:cursor-not-allowed"
                    data-testid="button-submit-weather"
                  >
                    {isLoading ? (
                      <>
                        <i className="fas fa-spinner fa-spin"></i>
                        <span>Processing...</span>
                      </>
                    ) : (
                      <>
                        <i className="fas fa-cloud-sun"></i>
                        <span className="hidden sm:inline">Get Weather Prediction</span>
                        <span className="sm:hidden">Get Prediction</span>
                        <i className="fas fa-arrow-right"></i>
                      </>
                    )}
                  </Button>
                </form>
              </Form>
            </div>

            {/* Prediction Results */}
            {prediction && (
              <Card className="gradient-card border-2 border-primary/30">
                <CardHeader>
                  <CardTitle className="flex items-center text-2xl">
                    <i className={`fas ${prediction.rain_predicted === 1 ? 'fa-cloud-rain text-blue-500' : 'fa-sun text-yellow-500'} mr-3`}></i>
                    Prediction Results
                  </CardTitle>
                  <CardDescription>
                    Based on XGBoost ML model with {(prediction.model_info.model_accuracy * 100).toFixed(1)}% accuracy
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Rain Prediction */}
                  <div className="text-center p-6 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-xl">
                    <div className="text-5xl font-bold mb-2">
                      {prediction.rain_predicted === 1 ? (
                        <span className="text-blue-400">Rain Expected</span>
                      ) : (
                        <span className="text-yellow-400">No Rain</span>
                      )}
                    </div>
                    <div className="text-2xl text-muted-foreground">
                      {(prediction.rain_probability * 100).toFixed(1)}% probability
                    </div>
                  </div>

                  {/* Details Grid */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-secondary/20 rounded-lg">
                      <div className="text-sm text-muted-foreground">Season</div>
                      <div className="text-lg font-semibold flex items-center">
                        <i className={`fas ${
                          prediction.season === 'Winter' ? 'fa-snowflake' :
                          prediction.season === 'Spring' ? 'fa-leaf' :
                          prediction.season === 'Summer' ? 'fa-sun' :
                          'fa-wind'
                        } mr-2`}></i>
                        {prediction.season}
                      </div>
                    </div>

                    <div className="p-4 bg-secondary/20 rounded-lg">
                      <div className="text-sm text-muted-foreground">Confidence</div>
                      <div className="text-lg font-semibold">
                        {(prediction.confidence * 100).toFixed(1)}%
                      </div>
                    </div>

                    <div className="p-4 bg-secondary/20 rounded-lg col-span-2">
                      <div className="text-sm text-muted-foreground">Location</div>
                      <div className="text-base font-semibold">
                        {prediction.location.latitude.toFixed(4)}°, {prediction.location.longitude.toFixed(4)}°
                      </div>
                    </div>
                  </div>

                  {/* Model Info */}
                  <div className="p-4 bg-accent/10 rounded-lg border border-accent/30">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Model Threshold:</span>
                      <span className="font-semibold">{prediction.model_info.threshold.toFixed(2)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Column: Interactive Map */}
          <WeatherMap 
            onLocationSelect={handleLocationSelect}
            selectedLocation={selectedLocation}
          />
        </div>

        {/* Additional Info Section */}
        <div className="mt-8 md:mt-12 gradient-card rounded-2xl p-4 md:p-6 lg:p-8">
          <h3 className="font-space font-semibold text-lg md:text-xl lg:text-2xl mb-4 md:mb-6 flex items-center">
            <i className="fas fa-satellite text-secondary mr-2 md:mr-3 text-lg md:text-xl"></i>
            NASA Data Sources
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
            <div className="flex items-start space-x-3 md:space-x-4" data-testid="info-modis">
              <div className="bg-primary/20 p-2 md:p-3 rounded-lg flex-shrink-0">
                <i className="fas fa-satellite-dish text-primary text-lg md:text-xl"></i>
              </div>
              <div className="min-w-0 flex-1">
                <h4 className="font-semibold mb-1 text-sm md:text-base">MODIS Satellites</h4>
                <p className="text-xs md:text-sm text-muted-foreground">Real-time atmospheric data from Terra and Aqua satellites</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 md:space-x-4" data-testid="info-geos">
              <div className="bg-secondary/20 p-2 md:p-3 rounded-lg flex-shrink-0">
                <i className="fas fa-cloud text-secondary text-lg md:text-xl"></i>
              </div>
              <div className="min-w-0 flex-1">
                <h4 className="font-semibold mb-1 text-sm md:text-base">GEOS-5 Models</h4>
                <p className="text-xs md:text-sm text-muted-foreground">Advanced atmospheric simulation and prediction models</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 md:space-x-4" data-testid="info-archives">
              <div className="bg-accent/20 p-2 md:p-3 rounded-lg flex-shrink-0">
                <i className="fas fa-database text-accent text-lg md:text-xl"></i>
              </div>
              <div className="min-w-0 flex-1">
                <h4 className="font-semibold mb-1 text-sm md:text-base">Historical Archives</h4>
                <p className="text-xs md:text-sm text-muted-foreground">Decades of climate and weather pattern data</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
