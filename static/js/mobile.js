// 移动端专用JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // 移动端触摸反馈
    const mobileButtons = document.querySelectorAll('.mobile-btn');
    
    mobileButtons.forEach(button => {
        // 触摸开始
        button.addEventListener('touchstart', function(e) {
            this.style.transform = 'scale(0.98) translateY(1px)';
            this.style.transition = 'transform 0.1s ease';
        });
        
        // 触摸结束
        button.addEventListener('touchend', function(e) {
            this.style.transform = '';
            this.style.transition = 'all 0.3s ease';
        });
        
        // 触摸取消（如果手指移出按钮区域）
        button.addEventListener('touchcancel', function(e) {
            this.style.transform = '';
            this.style.transition = 'all 0.3s ease';
        });
    });
    
    // 防止双击缩放
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(event) {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            event.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
    
    // Flash消息自动隐藏
    const flashMessages = document.querySelectorAll('.mobile-flash-message');
    flashMessages.forEach((message, index) => {
        setTimeout(() => {
            message.style.animation = 'mobileFlashOut 0.3s ease-in forwards';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 3000 + (index * 500)); // 每个消息延迟500ms消失
    });
    
    // 添加flash消息淡出动画
    const style = document.createElement('style');
    style.textContent = `
        @keyframes mobileFlashOut {
            from {
                opacity: 1;
                transform: translateY(0);
            }
            to {
                opacity: 0;
                transform: translateY(-20px);
            }
        }
    `;
    document.head.appendChild(style);
    
    // 性能优化：减少动画在低性能设备上的执行
    const isLowPerformanceDevice = () => {
        // 简单的性能检测
        const userAgent = navigator.userAgent.toLowerCase();
        const isOldAndroid = /android [1-4]\./.test(userAgent);
        const isOldIOS = /os [1-9]_/.test(userAgent);
        const isSlowConnection = navigator.connection && navigator.connection.effectiveType && 
                                navigator.connection.effectiveType.includes('2g');
        
        return isOldAndroid || isOldIOS || isSlowConnection;
    };
    
    // 如果是低性能设备，禁用某些动画
    if (isLowPerformanceDevice()) {
        document.body.classList.add('low-performance');
        const styleSheet = document.createElement('style');
        styleSheet.textContent = `
            .low-performance .bg-pixel,
            .low-performance .feature-icon,
            .low-performance .preview-icon {
                animation: none !important;
            }
        `;
        document.head.appendChild(styleSheet);
    }
    
    // 添加点击音效反馈（可选）
    const playClickSound = () => {
        // 创建短促的点击音效
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(600, audioContext.currentTime + 0.1);
        
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
    };
    
    // 为按钮添加音效（用户首次交互后）
    let audioEnabled = false;
    document.addEventListener('touchstart', function enableAudio() {
        audioEnabled = true;
        document.removeEventListener('touchstart', enableAudio);
    }, { once: true });
    
    mobileButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (audioEnabled) {
                try {
                    playClickSound();
                } catch (error) {
                    // 忽略音频错误
                }
            }
        });
    });
});

// 屏幕方向改变时的处理
window.addEventListener('orientationchange', function() {
    // 延迟处理，等待浏览器完成方向切换
    setTimeout(() => {
        // 重新计算视口高度
        document.body.style.height = window.innerHeight + 'px';
        
        // 刷新布局
        window.dispatchEvent(new Event('resize'));
    }, 100);
});
