// 像素风格 JavaScript 效果

document.addEventListener('DOMContentLoaded', function() {
    
    // 检测是否为移动设备
    const isMobile = window.innerWidth <= 768;
    
    // 创建额外的浮动像素效果
    function createRandomPixels() {
        const container = document.querySelector('.floating-pixels');
        
        setInterval(() => {
            const maxPixels = isMobile ? 10 : 20; // 移动端减少像素数量
            if (document.querySelectorAll('.random-pixel').length < maxPixels) {
                const pixel = document.createElement('div');
                pixel.className = 'pixel random-pixel';
                pixel.style.left = Math.random() * 100 + '%';
                pixel.style.animationDuration = (Math.random() * 10 + 5) + 's';
                pixel.style.animationDelay = Math.random() * 2 + 's';
                
                // 随机颜色（可爱橙色系）
                const colors = ['#ff9f40', '#87ceeb', '#ffd700', '#ffb366', '#dda0dd', '#98fb98', '#f0e68c'];
                pixel.style.background = colors[Math.floor(Math.random() * colors.length)];
                pixel.style.boxShadow = `0 0 8px ${pixel.style.background}, 0 0 15px ${pixel.style.background}`;
                
                container.appendChild(pixel);
                
                // 移除完成动画的像素
                setTimeout(() => {
                    if (pixel.parentNode) {
                        pixel.parentNode.removeChild(pixel);
                    }
                }, 15000);
            }
        }, 1000);
    }
    
    // 键盘效果
    document.addEventListener('keydown', function(e) {
        // 创建按键效果
        const keyEffect = document.createElement('div');
        keyEffect.style.position = 'fixed';
        keyEffect.style.top = '50%';
        keyEffect.style.left = '50%';
        keyEffect.style.transform = 'translate(-50%, -50%)';
        keyEffect.style.color = '#ff9f40';
        keyEffect.style.fontSize = '24px';
        keyEffect.style.fontFamily = "'Press Start 2P', monospace";
        keyEffect.style.pointerEvents = 'none';
        keyEffect.style.zIndex = '100';
        keyEffect.style.textShadow = '0 0 10px #ff9f40, 0 0 20px #ffb366';
        keyEffect.textContent = e.key.toUpperCase();
        keyEffect.style.animation = 'keyPress 0.5s ease-out forwards';
        
        document.body.appendChild(keyEffect);
        
        setTimeout(() => {
            if (keyEffect.parentNode) {
                keyEffect.parentNode.removeChild(keyEffect);
            }
        }, 500);
    });
    
    // 鼠标移动效果（桌面端）
    if (!isMobile) {
        document.addEventListener('mousemove', function(e) {
        // 创建跟踪像素
        const tracker = document.createElement('div');
        tracker.style.position = 'fixed';
        tracker.style.left = e.clientX + 'px';
        tracker.style.top = e.clientY + 'px';
        tracker.style.width = '4px';
        tracker.style.height = '4px';
        tracker.style.background = '#ff9f40';
        tracker.style.borderRadius = '50%';
        tracker.style.boxShadow = '0 0 8px #ff9f40, 0 0 15px #ffb366';
        tracker.style.pointerEvents = 'none';
        tracker.style.zIndex = '50';
        tracker.style.animation = 'mouseFade 1s ease-out forwards';
        
        document.body.appendChild(tracker);
        
        setTimeout(() => {
            if (tracker.parentNode) {
                tracker.parentNode.removeChild(tracker);
            }
        }, 1000);
    });
    
    // 启动像素效果
    createRandomPixels();
    
    // 控制台欢迎信息
    console.log(`
    ⚡🔥💀 LaOpen - 炫酷像素世界 💀🔥⚡
    
    ╔═══════════════════════════════════╗
    ║  🚀  欢迎进入数字朋克世界！  🚀   ║
    ║  💎  LaOpen 等待勇者的挑战   💎   ║
    ║  ⚡  准备好感受像素风暴吧！  ⚡   ║
    ╚═══════════════════════════════════╝
    
    🔥 技能指南：
    • 按任意键释放雷电特效 ⌨️⚡
    • 移动鼠标激发橙色能量 🐭🔥
    • 触摸屏幕启动炫酷粒子 📱💥
    
    💀 Coded with Fire & Lightning 💀
    `);
}
});

// 添加按键动画的 CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes keyPress {
        0% {
            opacity: 1;
            transform: translate(-50%, -50%) scale(0.5);
        }
        50% {
            transform: translate(-50%, -50%) scale(1.2);
        }
        100% {
            opacity: 0;
            transform: translate(-50%, -50%) scale(1) translateY(-50px);
        }
    }
    
    @keyframes mouseFade {
        0% {
            opacity: 1;
            transform: scale(1);
        }
        100% {
            opacity: 0;
            transform: scale(0);
        }
    }
`;
document.head.appendChild(style);

// 移动端触摸效果和优化
if (window.innerWidth <= 768) {
    // 添加触摸效果
    document.addEventListener('touchstart', function(e) {
        const touch = e.touches[0];
        createTouchEffect(touch.clientX, touch.clientY);
    }, { passive: true });
    
    function createTouchEffect(x, y) {
        const touchEffect = document.createElement('div');
        touchEffect.style.position = 'fixed';
        touchEffect.style.left = x + 'px';
        touchEffect.style.top = y + 'px';
        touchEffect.style.width = '6px';
        touchEffect.style.height = '6px';
        touchEffect.style.background = '#ff9f40';
        touchEffect.style.borderRadius = '50%';
        touchEffect.style.boxShadow = '0 0 10px #ff9f40, 0 0 20px #ffb366';
        touchEffect.style.pointerEvents = 'none';
        touchEffect.style.zIndex = '50';
        touchEffect.style.animation = 'touchFade 0.8s ease-out forwards';
        
        document.body.appendChild(touchEffect);
        
        setTimeout(() => {
            if (touchEffect.parentNode) {
                touchEffect.parentNode.removeChild(touchEffect);
            }
        }, 800);
    }
    
    // 添加触摸动画样式
    const touchStyle = document.createElement('style');
    touchStyle.textContent = `
        @keyframes touchFade {
            0% {
                opacity: 1;
                transform: scale(0.5);
            }
            50% {
                transform: scale(1.2);
            }
            100% {
                opacity: 0;
                transform: scale(1) translateY(-20px);
            }
        }
    `;
    document.head.appendChild(touchStyle);
}
