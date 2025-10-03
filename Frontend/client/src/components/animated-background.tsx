export default function AnimatedBackground() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {/* Animated clouds */}
      <div className="cloud cloud-1"></div>
      <div className="cloud cloud-2"></div>
      <div className="cloud cloud-3"></div>
      
      {/* Twinkling stars */}
      <div className="star" style={{ top: '15%', left: '25%', animationDelay: '0s' }}></div>
      <div className="star" style={{ top: '25%', left: '65%', animationDelay: '1s' }}></div>
      <div className="star" style={{ top: '45%', left: '35%', animationDelay: '2s' }}></div>
      <div className="star" style={{ top: '60%', left: '75%', animationDelay: '1.5s' }}></div>
      <div className="star" style={{ top: '75%', left: '15%', animationDelay: '0.5s' }}></div>
      <div className="star" style={{ top: '35%', left: '85%', animationDelay: '2.5s' }}></div>
    </div>
  );
}
