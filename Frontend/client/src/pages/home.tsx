import { Link } from "wouter";

export default function Home() {
  return (
    <div className="container mx-auto px-6 py-20">
      <div className="flex flex-col items-center justify-center min-h-[70vh] text-center relative z-10">
        
        {/* Main Title */}
        <h1 className="font-space font-bold text-6xl md:text-8xl mb-8 bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent animate-pulse" data-testid="title-main">
          Void Function Team
        </h1>
        
        {/* Subtitle */}
        <h2 className="font-sans font-semibold text-2xl md:text-4xl mb-12 text-muted-foreground" data-testid="title-subtitle">
          Nasa Space App Cairo
        </h2>

        {/* Description Card */}
        <div className="gradient-card rounded-2xl p-8 md:p-12 max-w-4xl mb-12">
          <div className="flex items-center justify-center mb-6">
            <i className="fas fa-globe-americas text-5xl text-accent"></i>
          </div>
          <p className="text-lg md:text-xl text-muted-foreground leading-relaxed mb-8" data-testid="text-description">
            Harness the power of NASA datasets to predict weather patterns with unprecedented accuracy. 
            Our advanced platform combines satellite data, atmospheric models, and machine learning to deliver 
            precise weather forecasts for any location on Earth.
          </p>
          
          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center" data-testid="feature-nasa-data">
              <i className="fas fa-satellite-dish text-3xl text-primary mb-3"></i>
              <h3 className="font-space font-semibold mb-2">NASA Data</h3>
              <p className="text-sm text-muted-foreground">Real-time satellite information</p>
            </div>
            <div className="text-center" data-testid="feature-ai-powered">
              <i className="fas fa-brain text-3xl text-secondary mb-3"></i>
              <h3 className="font-space font-semibold mb-2">AI Powered</h3>
              <p className="text-sm text-muted-foreground">Machine learning predictions</p>
            </div>
            <div className="text-center" data-testid="feature-global-coverage">
              <i className="fas fa-map-marked-alt text-3xl text-accent mb-3"></i>
              <h3 className="font-space font-semibold mb-2">Global Coverage</h3>
              <p className="text-sm text-muted-foreground">Worldwide weather tracking</p>
            </div>
          </div>

          {/* CTA Button */}
          <Link href="/weather" data-testid="button-start-prediction">
            <button className="btn-hover bg-accent text-accent-foreground px-8 py-4 rounded-xl font-space font-semibold text-lg inline-flex items-center space-x-3">
              <span>Start Weather Prediction</span>
              <i className="fas fa-arrow-right"></i>
            </button>
          </Link>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 w-full max-w-4xl">
          <div className="gradient-card rounded-xl p-6 text-center" data-testid="stat-accuracy">
            <div className="font-orbitron text-3xl font-bold text-primary mb-2">99.8%</div>
            <div className="text-sm text-muted-foreground">Accuracy</div>
          </div>
          <div className="gradient-card rounded-xl p-6 text-center" data-testid="stat-countries">
            <div className="font-orbitron text-3xl font-bold text-secondary mb-2">195+</div>
            <div className="text-sm text-muted-foreground">Countries</div>
          </div>
          <div className="gradient-card rounded-xl p-6 text-center" data-testid="stat-monitoring">
            <div className="font-orbitron text-3xl font-bold text-accent mb-2">24/7</div>
            <div className="text-sm text-muted-foreground">Monitoring</div>
          </div>
          <div className="gradient-card rounded-xl p-6 text-center" data-testid="stat-datapoints">
            <div className="font-orbitron text-3xl font-bold text-primary mb-2">1M+</div>
            <div className="text-sm text-muted-foreground">Data Points</div>
          </div>
        </div>
      </div>
    </div>
  );
}
