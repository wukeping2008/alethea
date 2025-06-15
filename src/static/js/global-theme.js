/**
 * 全局主题管理系统
 * 用于在整个网站中统一管理明亮/暗黑主题
 */

// 全局主题管理器
class GlobalThemeManager {
    constructor() {
        this.storageKey = 'theme';
        this.darkModeClass = 'dark-mode';
        this.init();
    }

    /**
     * 初始化主题管理器
     */
    init() {
        // 应用保存的主题或系统偏好
        this.applyTheme();

        // 监听系统主题变化
        this.watchSystemTheme();

        // 监听localStorage变化（跨标签页同步）
        this.watchStorageChanges();

        // 初始化主题切换按钮（如果存在）
        this.initThemeToggle();
    }

    /**
     * 获取当前主题
     */
    getCurrentTheme() {
        const savedTheme = localStorage.getItem(this.storageKey);
        if (savedTheme) {
            return savedTheme;
        }

        // 检查系统偏好
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        return prefersDark ? 'dark' : 'light';
    }

    /**
     * 应用主题
     */
    applyTheme(theme = null) {
        const targetTheme = theme || this.getCurrentTheme();

        if (targetTheme === 'dark') {
            document.body.classList.add(this.darkModeClass);
        } else {
            document.body.classList.remove(this.darkModeClass);
        }

        // 更新主题切换按钮图标
        this.updateThemeToggleIcon(targetTheme);

        // 触发主题变化事件
        this.dispatchThemeChangeEvent(targetTheme);
    }

    /**
     * 切换主题
     */
    toggleTheme() {
        const currentTheme = this.getCurrentTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        // 保存新主题
        localStorage.setItem(this.storageKey, newTheme);

        // 应用新主题
        this.applyTheme(newTheme);

        // 显示切换通知
        this.showThemeNotification(newTheme);

        return newTheme;
    }

    /**
     * 更新主题切换按钮图标
     */
    updateThemeToggleIcon(theme) {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                if (theme === 'dark') {
                    icon.className = 'fas fa-sun';
                    themeToggle.title = '切换到明亮主题';
                } else {
                    icon.className = 'fas fa-moon';
                    themeToggle.title = '切换到暗黑主题';
                }
            }
        }
    }

    /**
     * 初始化主题切换按钮
     */
    initThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            // 移除可能存在的旧事件监听器
            themeToggle.replaceWith(themeToggle.cloneNode(true));

            // 重新获取元素并添加事件监听器
            const newThemeToggle = document.getElementById('theme-toggle');
            newThemeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
    }

    /**
     * 显示主题切换通知
     */
    showThemeNotification(theme) {
        // 移除已存在的通知
        const existingNotification = document.querySelector('.theme-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const message = theme === 'dark' ? '已切换到暗黑主题 🌙' : '已切换到明亮主题 ☀️';

        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: #2ca58d;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            font-size: 14px;
            font-weight: 500;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;

        document.body.appendChild(notification);

        // 显示动画
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // 自动隐藏
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }, 2000);
    }

    /**
     * 监听系统主题变化
     */
    watchSystemTheme() {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            const savedTheme = localStorage.getItem(this.storageKey);
            if (!savedTheme) {
                // 只有在用户没有手动设置主题时才跟随系统
                const newTheme = e.matches ? 'dark' : 'light';
                this.applyTheme(newTheme);
            }
        });
    }

    /**
     * 监听localStorage变化（跨标签页同步）
     */
    watchStorageChanges() {
        window.addEventListener('storage', (e) => {
            if (e.key === this.storageKey) {
                this.applyTheme(e.newValue);
            }
        });
    }

    /**
     * 触发主题变化事件
     */
    dispatchThemeChangeEvent(theme) {
        const event = new CustomEvent('themechange', {
            detail: { theme }
        });
        window.dispatchEvent(event);
    }

    /**
     * 监听主题变化事件
     */
    onThemeChange(callback) {
        window.addEventListener('themechange', callback);
    }

    /**
     * 获取主题相关的CSS变量
     */
    getThemeVariables(theme = null) {
        const targetTheme = theme || this.getCurrentTheme();

        if (targetTheme === 'dark') {
            return {
                '--bg-primary': '#1a1a2e',
                '--bg-secondary': '#2d2d44',
                '--text-primary': '#eee',
                '--text-secondary': '#ccc',
                '--border-color': '#444',
                '--shadow-color': 'rgba(0, 0, 0, 0.5)'
            };
        } else {
            return {
                '--bg-primary': '#ffffff',
                '--bg-secondary': '#f8f9fa',
                '--text-primary': '#212529',
                '--text-secondary': '#6c757d',
                '--border-color': '#e2e8f0',
                '--shadow-color': 'rgba(0, 0, 0, 0.1)'
            };
        }
    }

    /**
     * 应用主题CSS变量
     */
    applyThemeVariables(theme = null) {
        const variables = this.getThemeVariables(theme);
        const root = document.documentElement;

        Object.entries(variables).forEach(([property, value]) => {
            root.style.setProperty(property, value);
        });
    }
}

// 创建全局主题管理器实例
window.globalThemeManager = new GlobalThemeManager();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function () {
    // 确保主题管理器已初始化
    if (window.globalThemeManager) {
        window.globalThemeManager.applyTheme();
    }
});

// 导出给其他脚本使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GlobalThemeManager;
}
