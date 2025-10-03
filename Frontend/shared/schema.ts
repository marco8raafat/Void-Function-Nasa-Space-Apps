import { z } from "zod";

export const weatherQuerySchema = z.object({
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Date must be in YYYY-MM-DD format"),
});

export const locationSchema = z.object({
  name: z.string(),
  latitude: z.number(),
  longitude: z.number(),
});

export const weatherPredictionResponseSchema = z.object({
  rain_probability: z.number(),
  rain_predicted: z.number(),
  season: z.string(),
  season_code: z.number(),
  confidence: z.number(),
  location: z.object({
    latitude: z.number(),
    longitude: z.number(),
  }),
  date: z.object({
    day: z.number(),
    month: z.number(),
    year: z.number(),
  }),
  model_info: z.object({
    threshold: z.number(),
    model_accuracy: z.number(),
  }),
});

export type WeatherQuery = z.infer<typeof weatherQuerySchema>;
export type Location = z.infer<typeof locationSchema>;
export type WeatherPredictionResponse = z.infer<typeof weatherPredictionResponseSchema>;
