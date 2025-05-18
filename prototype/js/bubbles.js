class Bubbles {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' 
      ? document.querySelector(container) 
      : container;
      
    // Default options
    this.options = {
      bubbleCount: options.bubbleCount || 40,
      bubbleColors: options.bubbleColors || ['rgba(255, 255, 255, 0.3)', 'rgba(240, 240, 250, 0.4)', 'rgba(230, 230, 250, 0.3)'],
      minSize: options.minSize || 3,
      maxSize: options.maxSize || 12,
      speed: options.speed || 0.5,
      backgroundColor: options.backgroundColor || 'transparent',
      responsive: options.responsive !== undefined ? options.responsive : true,
      maxCursorInfluence: options.maxCursorInfluence || 80
    };

    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    this.bubbles = [];
    this.mouse = { x: 0, y: 0, moved: false };
    
    this.init();
  }

  init() {
    // Set up Canvas
    this.container.appendChild(this.canvas);
    this.canvas.style.position = 'absolute';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.canvas.style.zIndex = '-1';
    this.canvas.style.pointerEvents = 'none';
    
    // Adjust size
    this.resize();
    window.addEventListener('resize', () => this.resize());
    
    // Mouse/touch events
    this.container.addEventListener('mousemove', e => this.mouseMove(e));
    this.container.addEventListener('touchmove', e => this.touchMove(e));
    
    // Create bubbles
    this.createBubbles();
    
    // Start animation
    this.animate();
  }

  resize() {
    const rect = this.container.getBoundingClientRect();
    this.width = rect.width;
    this.height = rect.height;
    
    // Set Canvas size, considering device pixel ratio
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);
    
    // If responsive, recreate bubbles on resize
    if (this.options.responsive) {
      this.createBubbles();
    }
  }

  createBubbles() {
    this.bubbles = [];
    
    for (let i = 0; i < this.options.bubbleCount; i++) {
      const size = this.options.minSize + Math.random() * (this.options.maxSize - this.options.minSize);
      const colorIndex = Math.floor(Math.random() * this.options.bubbleColors.length);
      
      this.bubbles.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        size: size,
        originalSize: size,
        color: this.options.bubbleColors[colorIndex],
        speedX: (Math.random() - 0.5) * this.options.speed,
        speedY: (Math.random() - 0.5) * this.options.speed,
        opacity: 0.1 + Math.random() * 0.5,
        growing: Math.random() > 0.5
      });
    }
  }

  mouseMove(e) {
    const rect = this.container.getBoundingClientRect();
    this.mouse.x = e.clientX - rect.left;
    this.mouse.y = e.clientY - rect.top;
    this.mouse.moved = true;
  }

  touchMove(e) {
    if (e.touches.length > 0) {
      const rect = this.container.getBoundingClientRect();
      this.mouse.x = e.touches[0].clientX - rect.left;
      this.mouse.y = e.touches[0].clientY - rect.top;
      this.mouse.moved = true;
    }
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    this.ctx.clearRect(0, 0, this.width, this.height);
    
    // Fill background if specified
    if (this.options.backgroundColor !== 'transparent') {
      this.ctx.fillStyle = this.options.backgroundColor;
      this.ctx.fillRect(0, 0, this.width, this.height);
    }
    
    // Update and draw bubbles
    this.updateBubbles();
    this.drawBubbles();
  }

  updateBubbles() {
    this.bubbles.forEach(bubble => {
      // Cursor influence
      if (this.mouse.moved) {
        const dx = this.mouse.x - bubble.x;
        const dy = this.mouse.y - bubble.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const maxDist = this.options.maxCursorInfluence;
        
        if (dist < maxDist) {
          // Bubbles move away from cursor
          const force = (1 - dist / maxDist) * 2;
          bubble.x -= dx * force * 0.05;
          bubble.y -= dy * force * 0.05;
          
          // Bubbles grow slightly when near cursor
          bubble.size = bubble.originalSize * (1 + (force * 0.5));
        } else {
          // Return to original size gradually
          bubble.size += (bubble.originalSize - bubble.size) * 0.1;
        }
      }
      
      // Move bubbles
      bubble.x += bubble.speedX;
      bubble.y += bubble.speedY;
      
      // Gentle pulsing effect
      if (bubble.growing) {
        bubble.size += 0.03;
        if (bubble.size > bubble.originalSize * 1.2) {
          bubble.growing = false;
        }
      } else {
        bubble.size -= 0.03;
        if (bubble.size < bubble.originalSize * 0.8) {
          bubble.growing = true;
        }
      }
      
      // Wrap around edges
      if (bubble.x < -bubble.size) bubble.x = this.width + bubble.size;
      if (bubble.x > this.width + bubble.size) bubble.x = -bubble.size;
      if (bubble.y < -bubble.size) bubble.y = this.height + bubble.size;
      if (bubble.y > this.height + bubble.size) bubble.y = -bubble.size;
    });
  }

  drawBubbles() {
    this.bubbles.forEach(bubble => {
      this.ctx.beginPath();
      this.ctx.arc(bubble.x, bubble.y, bubble.size, 0, Math.PI * 2);
      this.ctx.fillStyle = bubble.color;
      this.ctx.globalAlpha = bubble.opacity;
      this.ctx.fill();
      
      // Add a subtle highlight to give 3D effect
      const gradient = this.ctx.createRadialGradient(
        bubble.x - bubble.size * 0.3, 
        bubble.y - bubble.size * 0.3, 
        0, 
        bubble.x, 
        bubble.y, 
        bubble.size
      );
      gradient.addColorStop(0, 'rgba(255, 255, 255, 0.5)');
      gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
      
      this.ctx.beginPath();
      this.ctx.arc(bubble.x, bubble.y, bubble.size, 0, Math.PI * 2);
      this.ctx.fillStyle = gradient;
      this.ctx.globalAlpha = bubble.opacity * 0.7;
      this.ctx.fill();
      
      this.ctx.globalAlpha = 1;
    });
  }
}

// Export class
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
  module.exports = Bubbles;
} else {
  window.Bubbles = Bubbles;
} 