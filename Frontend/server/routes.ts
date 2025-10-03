import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";

export async function registerRoutes(app: Express): Promise<Server> {
  // Proxy route to FastAPI ML backend
  app.get("/api/predict", async (req, res) => {
    try {
      const { lat, lon, day, month, year } = req.query;
      
      // Validate required parameters
      if (!lat || !lon || !day || !month || !year) {
        return res.status(400).json({ 
          error: "Missing required parameters",
          required: ["lat", "lon", "day", "month", "year"]
        });
      }

      // Call FastAPI backend
      const apiUrl = `http://localhost:8000/predict?lat=${lat}&lon=${lon}&day=${day}&month=${month}&year=${year}`;
      const response = await fetch(apiUrl);
      
      if (!response.ok) {
        throw new Error(`FastAPI returned status ${response.status}`);
      }
      
      const data = await response.json();
      res.json(data);
    } catch (error) {
      console.error("Error calling prediction API:", error);
      res.status(500).json({ 
        error: "Failed to get weather prediction",
        message: error instanceof Error ? error.message : "Unknown error",
        hint: "Make sure the FastAPI server is running on port 8000"
      });
    }
  });

  // Health check for ML backend
  app.get("/api/ml-status", async (req, res) => {
    try {
      const response = await fetch("http://localhost:8000/");
      const data = await response.json();
      res.json({ status: "connected", ml_backend: data });
    } catch (error) {
      res.status(503).json({ 
        status: "disconnected", 
        error: "ML backend not available",
        hint: "Start the FastAPI server with: python api_server.py"
      });
    }
  });

  // Get model information
  app.get("/api/model-info", async (req, res) => {
    try {
      const response = await fetch("http://localhost:8000/model-info");
      const data = await response.json();
      res.json(data);
    } catch (error) {
      res.status(503).json({ 
        error: "ML backend not available" 
      });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}
