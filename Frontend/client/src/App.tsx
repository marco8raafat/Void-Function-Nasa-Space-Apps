import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Home from "@/pages/home";
import Weather from "@/pages/weather";
import NotFound from "@/pages/not-found";
import Navigation from "@/components/navigation";
import AnimatedBackground from "@/components/animated-background";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/weather" component={Weather} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <div className="min-h-screen gradient-weather text-foreground overflow-x-hidden">
          <AnimatedBackground />
          <div className="relative z-10">
            <Navigation />
            <div className="page-transition">
              <Router />
            </div>
          </div>
          <footer className="relative z-10 mt-20 py-8 border-t border-white/10">
            <div className="container mx-auto px-6">
              <div className="flex flex-col md:flex-row justify-between items-center">
                <div className="mb-4 md:mb-0">
                  <p className="text-muted-foreground text-sm">
                    © 2024 Void Function Team | NASA Space App Cairo
                  </p>
                </div>
                <div className="flex space-x-6">
                  <a href="#" className="text-muted-foreground hover:text-accent transition-colors" data-testid="link-github">
                    <i className="fab fa-github text-xl"></i>
                  </a>
                  <a href="#" className="text-muted-foreground hover:text-accent transition-colors" data-testid="link-twitter">
                    <i className="fab fa-twitter text-xl"></i>
                  </a>
                  <a href="#" className="text-muted-foreground hover:text-accent transition-colors" data-testid="link-linkedin">
                    <i className="fab fa-linkedin text-xl"></i>
                  </a>
                </div>
              </div>
            </div>
          </footer>
        </div>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
