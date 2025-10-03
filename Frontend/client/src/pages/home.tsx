import { Link } from "wouter";

export default function Home() {
  return (
    <div className="container mx-auto px-6 py-20">
      <div className="flex flex-col items-center justify-center min-h-[70vh] text-center relative z-10">
        
        {/* Main Title */}
        <h1 className="font-space font-bold text-3xl sm:text-4xl md:text-6xl lg:text-8xl mb-6 md:mb-8 bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent animate-pulse" data-testid="title-main">
          Void Function Team
        </h1>
        
        {/* Subtitle */}
        <h2 className="font-sans font-semibold text-lg sm:text-xl md:text-2xl lg:text-4xl mb-8 md:mb-12 text-muted-foreground" data-testid="title-subtitle">
          Nasa Space App Cairo
        </h2>

        {/* Description Card */}
        <div className="gradient-card rounded-2xl p-6 md:p-8 lg:p-12 max-w-4xl mb-8 md:mb-12 mx-4 md:mx-0">
          <div className="flex items-center justify-center mb-6">
            <i className="fas fa-globe-americas text-4xl md:text-5xl text-accent"></i>
          </div>
          <p className="text-base md:text-lg lg:text-xl text-muted-foreground leading-relaxed mb-6 md:mb-8" data-testid="text-description">
            Harness the power of NASA datasets to predict weather patterns with unprecedented accuracy. 
            Our advanced platform combines satellite data, atmospheric models, and machine learning to deliver 
            precise weather forecasts for any location on Earth.
          </p>
          
          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
            <div className="text-center" data-testid="feature-nasa-data">
              <i className="fas fa-satellite-dish text-2xl md:text-3xl text-primary mb-3"></i>
              <h3 className="font-space font-semibold mb-2 text-sm md:text-base">NASA Data</h3>
              <p className="text-xs md:text-sm text-muted-foreground">Real-time satellite information</p>
            </div>
            <div className="text-center" data-testid="feature-ai-powered">
              <i className="fas fa-brain text-2xl md:text-3xl text-secondary mb-3"></i>
              <h3 className="font-space font-semibold mb-2 text-sm md:text-base">AI Powered</h3>
              <p className="text-xs md:text-sm text-muted-foreground">Machine learning predictions</p>
            </div>
            <div className="text-center" data-testid="feature-global-coverage">
              <i className="fas fa-map-marked-alt text-2xl md:text-3xl text-accent mb-3"></i>
              <h3 className="font-space font-semibold mb-2 text-sm md:text-base">Global Coverage</h3>
              <p className="text-xs md:text-sm text-muted-foreground">Worldwide weather tracking</p>
            </div>
          </div>

          {/* CTA Button */}
          <div className="flex justify-center">
            <Link href="/weather" data-testid="button-start-prediction">
              <button className="btn-hover bg-accent text-accent-foreground px-6 md:px-8 py-3 md:py-4 rounded-xl font-space font-semibold text-base md:text-lg inline-flex items-center space-x-2 md:space-x-3 w-full sm:w-auto">
                <span>Start Weather Prediction</span>
                <i className="fas fa-arrow-right"></i>
              </button>
            </Link>
          </div>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-6 w-full max-w-4xl px-4 md:px-0">
          <div className="gradient-card rounded-xl p-4 md:p-6 text-center" data-testid="stat-accuracy">
            <div className="font-orbitron text-2xl md:text-3xl font-bold text-primary mb-2">99.8%</div>
            <div className="text-xs md:text-sm text-muted-foreground">Accuracy</div>
          </div>
          <div className="gradient-card rounded-xl p-4 md:p-6 text-center" data-testid="stat-countries">
            <div className="font-orbitron text-2xl md:text-3xl font-bold text-secondary mb-2">195+</div>
            <div className="text-xs md:text-sm text-muted-foreground">Countries</div>
          </div>
          <div className="gradient-card rounded-xl p-4 md:p-6 text-center" data-testid="stat-monitoring">
            <div className="font-orbitron text-2xl md:text-3xl font-bold text-accent mb-2">24/7</div>
            <div className="text-xs md:text-sm text-muted-foreground">Monitoring</div>
          </div>
          <div className="gradient-card rounded-xl p-4 md:p-6 text-center" data-testid="stat-datapoints">
            <div className="font-orbitron text-2xl md:text-3xl font-bold text-primary mb-2">1M+</div>
            <div className="text-xs md:text-sm text-muted-foreground">Data Points</div>
          </div>
        </div>
      </div>
    </div>
  );
}
