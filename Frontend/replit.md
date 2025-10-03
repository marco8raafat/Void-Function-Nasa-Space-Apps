# NASA Weather Prediction Platform

## Overview

This is a full-stack web application built for the NASA Space App Cairo hackathon by the Void Function Team. The platform leverages NASA datasets to predict weather patterns with advanced forecasting capabilities. It features an interactive Earth mapping interface using Leaflet, allowing users to select locations and query weather predictions. The application combines satellite data visualization with a modern, space-themed user interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework & Build System**
- **React 18 with TypeScript**: Component-based UI development with type safety
- **Vite**: Modern build tool providing fast HMR (Hot Module Replacement) and optimized production builds
- **Wouter**: Lightweight client-side routing (~1KB alternative to React Router)

**UI Component System**
- **shadcn/ui with Radix UI**: Headless, accessible component primitives with custom styling
- **Tailwind CSS**: Utility-first CSS framework with custom design system
- **CSS Variables**: Dark mode support with space-themed color palette (cyan, blue, purple gradients)
- **Custom Fonts**: Space Grotesk, Inter, and Orbitron for sci-fi aesthetic

**State Management & Data Fetching**
- **TanStack Query (React Query)**: Server state management with caching, background refetching disabled by default (staleTime: Infinity)
- **React Hook Form**: Form state management with Zod schema validation
- **Custom hooks**: useIsMobile, useToast for reusable functionality

**Map Integration**
- **Leaflet**: Interactive map library for location selection
- **OpenStreetMap tiles**: Base map layer
- **Custom markers**: Cyan-colored markers for selected locations

### Backend Architecture

**Server Framework**
- **Express.js**: Minimal REST API server
- **TypeScript with ESM**: Modern module system with type safety
- **Vite Middleware Mode**: Development server with HMR integration

**API Design Pattern**
- REST endpoints prefixed with `/api`
- Request/response logging middleware
- JSON body parsing with raw body preservation
- CORS and error handling built-in

**Storage Layer**
- **Memory-based storage**: In-memory implementation (MemStorage) for development
- **IStorage interface**: Abstraction layer for future database integration
- Schema defined separately in shared folder for type safety

### Data Storage Solutions

**Database Configuration**
- **PostgreSQL with Drizzle ORM**: Configured but not yet implemented
- **Neon Database**: Serverless PostgreSQL provider (@neondatabase/serverless)
- **Schema location**: `shared/schema.ts` using Drizzle-Zod for validation
- **Migration system**: Drizzle Kit with migrations output to `./migrations`

**Data Models**
- `WeatherQuery`: Latitude (-90 to 90), Longitude (-180 to 180), Date (YYYY-MM-DD format)
- `Location`: Name, Latitude, Longitude coordinates

### Authentication & Authorization

**Current State**: No authentication implemented
- Public access to all features
- No user sessions or authentication middleware
- Ready for future implementation (session store configured with connect-pg-simple)

### Design Patterns & Principles

**Component Organization**
- **Atomic Design**: UI components separated by complexity (ui/, components/)
- **Path Aliases**: `@/` for client src, `@shared/` for shared code, `@assets/` for assets
- **Separation of Concerns**: Client, server, and shared code in distinct directories

**Code Quality**
- **TypeScript Strict Mode**: Enhanced type checking
- **Module Resolution**: Bundler mode for modern import resolution
- **Build Strategy**: Vite for client, esbuild for server (ESM output)

**Development Workflow**
- Development: tsx server with Vite dev server
- Production: Pre-built static assets served by Express
- Type checking: Separate `tsc` check command

## External Dependencies

### Third-Party Services
- **NASA APIs**: Weather and satellite data (integration pending)
- **OpenStreetMap**: Map tile provider via Leaflet
- **Google Fonts**: Custom typography (Space Grotesk, Inter, Orbitron)
- **Font Awesome**: Icon library for UI elements

### Database & Infrastructure
- **Neon Database**: Serverless PostgreSQL (configured via DATABASE_URL)
- **Drizzle ORM**: Type-safe database toolkit with PostgreSQL dialect
- **Connect-pg-simple**: PostgreSQL session store (configured but unused)

### Key Libraries
- **Validation**: Zod for schema validation, @hookform/resolvers for form integration
- **UI Framework**: Radix UI primitives (30+ component packages)
- **Utilities**: clsx, tailwind-merge for className management, date-fns for date handling
- **Development**: Replit plugins for cartographer, dev banner, and runtime error handling

### Build & Development Tools
- **Vite**: Frontend build tool with React plugin
- **esbuild**: Server bundling for production
- **tsx**: TypeScript execution for development
- **PostCSS**: CSS processing with Tailwind and Autoprefixer