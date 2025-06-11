// 初始管理员账户
const ADMIN_CREDENTIALS = {
    username: 'admin',
    password: 'admin123'
};

// DOM元素
const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginButton = document.getElementById('loginButton');

// 事件监听
loginForm.addEventListener('submit', handleLogin);

// 检查登录状态
checkLoginStatus();

// 处理登录
async function handleLogin() {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!username || !password) {
        showNotification('请输入用户名和密码', 'error');
        return;
    }

    try {
        loginButton.disabled = true;
        loginButton.textContent = '登录中...';

        // 模拟网络延迟
        await new Promise(resolve => setTimeout(resolve, 500));

        if (validateCredentials(username, password)) {
            // 设置登录状态
            setLoginStatus(true);
            showNotification('登录成功', 'success');
            
            // 延迟跳转到管理后台
            setTimeout(() => {
                window.location.href = 'admin.html';
            }, 1000);
        } else {
            showNotification('用户名或密码错误', 'error');
            passwordInput.value = '';
        }
    } catch (error) {
        showNotification('登录失败，请重试', 'error');
    } finally {
        loginButton.disabled = false;
        loginButton.textContent = '登录';
    }
}

// 验证用户名和密码
function validateCredentials(username, password) {
    return username === ADMIN_CREDENTIALS.username && 
           password === ADMIN_CREDENTIALS.password;
}

// 设置登录状态
function setLoginStatus(isLoggedIn) {
    if (isLoggedIn) {
        const loginData = {
            timestamp: Date.now(),
            username: usernameInput.value.trim()
        };
        localStorage.setItem('adminLoginStatus', JSON.stringify(loginData));
    } else {
        localStorage.removeItem('adminLoginStatus');
    }
}

// 检查登录状态
function checkLoginStatus() {
    const loginData = localStorage.getItem('adminLoginStatus');
    
    if (loginData) {
        try {
            const { timestamp, username } = JSON.parse(loginData);
            const currentTime = Date.now();
            
            // 检查登录是否在24小时内
            if (currentTime - timestamp < 24 * 60 * 60 * 1000) {
                // 如果已登录且在登录页面，则跳转到管理后台
                if (window.location.pathname.endsWith('login.html')) {
                    window.location.href = 'admin.html';
                }
                return true;
            }
        } catch (error) {
            console.error('登录状态解析错误:', error);
        }
    }
    
    return false;
}

// 通知系统
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // 自动消失
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 添加样式
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: var(--border-radius);
        background-color: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    }

    .notification.success {
        background-color: #d4edda;
        color: #155724;
    }

    .notification.error {
        background-color: #f8d7da;
        color: #721c24;
    }

    .notification.fade-out {
        animation: fadeOut 0.3s ease;
    }

    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
`;
document.head.appendChild(style);
