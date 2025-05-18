class Waves {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' 
      ? document.querySelector(container) 
      : container;
      
    // 默认选项
    this.options = {
      lineColor: options.lineColor || '#fff',
      backgroundColor: options.backgroundColor || 'rgba(255, 255, 255, 0.2)',
      waveSpeedX: options.waveSpeedX || 0.02,
      waveSpeedY: options.waveSpeedY || 0.01,
      waveAmpX: options.waveAmpX || 40,
      waveAmpY: options.waveAmpY || 20,
      friction: options.friction || 0.9,
      tension: options.tension || 0.01,
      maxCursorMove: options.maxCursorMove || 120,
      xGap: options.xGap || 12,
      yGap: options.yGap || 36
    };

    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    this.points = [];
    this.mouse = { x: 0, y: 0, moved: false };
    
    this.init();
  }

  init() {
    // 设置Canvas
    this.container.appendChild(this.canvas);
    this.canvas.style.position = 'absolute';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.canvas.style.zIndex = '-1';
    this.canvas.style.pointerEvents = 'none';
    
    // 调整尺寸
    this.resize();
    window.addEventListener('resize', () => this.resize());
    
    // 鼠标/触摸事件
    this.container.addEventListener('mousemove', e => this.mouseMove(e));
    this.container.addEventListener('touchmove', e => this.touchMove(e));
    
    // 创建波浪点
    this.createPoints();
    
    // 开始动画
    this.animate();
  }

  resize() {
    const rect = this.container.getBoundingClientRect();
    this.width = rect.width;
    this.height = rect.height;
    
    // 设置Canvas尺寸，考虑设备像素比
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);
    
    // 重新创建点
    this.createPoints();
  }

  createPoints() {
    this.points = [];
    
    // 创建网格点
    const xCount = Math.ceil(this.width / this.options.xGap) + 1;
    const yCount = Math.ceil(this.height / this.options.yGap) + 1;
    
    for (let y = 0; y < yCount; y++) {
      for (let x = 0; x < xCount; x++) {
        this.points.push({
          x: x * this.options.xGap,
          y: y * this.options.yGap,
          originX: x * this.options.xGap,
          originY: y * this.options.yGap,
          vx: 0,
          vy: 0
        });
      }
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
    
    // 更新点的位置
    this.updatePoints();
    
    // 绘制波浪线
    this.drawWaves();
  }

  updatePoints() {
    this.points.forEach(point => {
      // 计算点到鼠标的距离
      if (this.mouse.moved) {
        const dx = this.mouse.x - point.x;
        const dy = this.mouse.y - point.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const maxDist = this.options.maxCursorMove;
        
        if (dist < maxDist) {
          const force = (1 - dist / maxDist) * this.options.maxCursorMove;
          point.vx += -dx * force * 0.01;
          point.vy += -dy * force * 0.01;
        }
      }
      
      // 应用张力（将点拉回原始位置）
      point.vx += (point.originX - point.x) * this.options.tension;
      point.vy += (point.originY - point.y) * this.options.tension;
      
      // 应用摩擦力
      point.vx *= this.options.friction;
      point.vy *= this.options.friction;
      
      // 应用波浪效果
      point.vx += Math.sin(point.originY * this.options.waveSpeedY) * this.options.waveAmpX;
      point.vy += Math.sin(point.originX * this.options.waveSpeedX) * this.options.waveAmpY;
      
      // 更新点的位置
      point.x += point.vx;
      point.y += point.vy;
    });
  }

  drawWaves() {
    const xCount = Math.ceil(this.width / this.options.xGap) + 1;
    const yCount = Math.ceil(this.height / this.options.yGap) + 1;
    
    // 设置绘图样式
    this.ctx.strokeStyle = this.options.lineColor;
    this.ctx.fillStyle = this.options.backgroundColor;
    this.ctx.lineWidth = 1;
    
    // 绘制水平线
    for (let y = 0; y < yCount; y++) {
      this.ctx.beginPath();
      
      for (let x = 0; x < xCount; x++) {
        const point = this.points[y * xCount + x];
        
        if (x === 0) {
          this.ctx.moveTo(point.x, point.y);
        } else {
          const prevPoint = this.points[y * xCount + (x - 1)];
          const midX = (prevPoint.x + point.x) / 2;
          const midY = (prevPoint.y + point.y) / 2;
          
          // 使用二次贝塞尔曲线使线条更平滑
          this.ctx.quadraticCurveTo(prevPoint.x, prevPoint.y, midX, midY);
        }
      }
      
      this.ctx.stroke();
    }
    
    // 绘制垂直线
    for (let x = 0; x < xCount; x++) {
      this.ctx.beginPath();
      
      for (let y = 0; y < yCount; y++) {
        const point = this.points[y * xCount + x];
        
        if (y === 0) {
          this.ctx.moveTo(point.x, point.y);
        } else {
          const prevPoint = this.points[(y - 1) * xCount + x];
          const midX = (prevPoint.x + point.x) / 2;
          const midY = (prevPoint.y + point.y) / 2;
          
          this.ctx.quadraticCurveTo(prevPoint.x, prevPoint.y, midX, midY);
        }
      }
      
      this.ctx.stroke();
    }
  }
}

// 导出类
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
  module.exports = Waves;
} else {
  window.Waves = Waves;
} 