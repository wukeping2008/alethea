// 检查登录状态
function checkLoginStatus() {
    const loginData = localStorage.getItem('adminLoginStatus');
    
    if (!loginData) {
        window.location.href = 'login.html';
        return false;
    }

    try {
        const { timestamp } = JSON.parse(loginData);
        const currentTime = Date.now();
        
        // 检查登录是否在24小时内
        if (currentTime - timestamp > 24 * 60 * 60 * 1000) {
            localStorage.removeItem('adminLoginStatus');
            window.location.href = 'login.html';
            return false;
        }
    } catch (error) {
        console.error('登录状态解析错误:', error);
        window.location.href = 'login.html';
        return false;
    }
    
    return true;
}

// 初始化检查
if (!checkLoginStatus()) {
    throw new Error('未登录');
}

// 退出登录
document.getElementById('logoutButton').addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('adminLoginStatus');
    showNotification('已退出登录', 'success');
    setTimeout(() => {
        window.location.href = 'login.html';
    }, 1000);
});

// DOM元素
const documentUpload = document.getElementById('documentUpload');
const uploadButton = document.getElementById('uploadButton');
const documentsList = document.getElementById('documentsList');
const totalDocuments = document.getElementById('totalDocuments');
const lastUpdate = document.getElementById('lastUpdate');
const updateKnowledgeBase = document.getElementById('updateKnowledgeBase');

// 状态管理
let uploadInProgress = false;
let documents = [];

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadDocuments();
    setupEventListeners();
});

// 设置事件监听
function setupEventListeners() {
    uploadButton.addEventListener('click', handleUpload);
    updateKnowledgeBase.addEventListener('click', handleKnowledgeBaseUpdate);
    
    // 拖拽上传
    const uploadBox = document.querySelector('.upload-box');
    
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.classList.add('drag-over');
    });
    
    uploadBox.addEventListener('dragleave', () => {
        uploadBox.classList.remove('drag-over');
    });
    
    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            documentUpload.files = files;
            handleUpload();
        }
    });
}

// 处理文件上传
async function handleUpload() {
    if (uploadInProgress) return;
    
    const files = documentUpload.files;
    if (!files.length) {
        showNotification('请选择要上传的文件', 'error');
        return;
    }

    uploadInProgress = true;
    updateUploadUI(true);

    try {
        // 这里应该连接到实际的后端API
        // 示例中使用模拟上传
        await simulateFileUpload(files);
        
        showNotification('文件上传成功', 'success');
        await loadDocuments(); // 重新加载文档列表
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        uploadInProgress = false;
        updateUploadUI(false);
        documentUpload.value = ''; // 清空文件选择
    }
}

// 模拟文件上传
function simulateFileUpload(files) {
    return new Promise((resolve) => {
        setTimeout(() => {
            // 模拟添加新文档到列表
            Array.from(files).forEach(file => {
                documents.push({
                    id: Date.now(),
                    name: file.name,
                    size: file.size,
                    uploadDate: new Date().toISOString()
                });
            });
            resolve();
        }, 1500);
    });
}

// 加载文档列表
async function loadDocuments() {
    try {
        // 这里应该从后端API获取文档列表
        // 示例中使用模拟数据
        await simulateLoadDocuments();
        renderDocumentsList();
        updateStats();
    } catch (error) {
        showNotification('加载文档列表失败', 'error');
    }
}

// 模拟加载文档
function simulateLoadDocuments() {
    return new Promise((resolve) => {
        setTimeout(() => {
            // 使用已存在的documents数组
            resolve();
        }, 500);
    });
}

// 渲染文档列表
function renderDocumentsList() {
    if (!documents.length) {
        documentsList.innerHTML = '<p class="no-documents">暂无上传的文档</p>';
        return;
    }

    documentsList.innerHTML = documents.map(doc => `
        <div class="document-item">
            <div class="document-info">
                <span class="document-name">${doc.name}</span>
                <span class="document-size">${formatFileSize(doc.size)}</span>
            </div>
            <div class="document-actions">
                <span class="document-date">${formatDate(doc.uploadDate)}</span>
                <button onclick="deleteDocument(${doc.id})" class="delete-btn">删除</button>
            </div>
        </div>
    `).join('');
}

// 更新统计信息
function updateStats() {
    totalDocuments.textContent = documents.length;
    lastUpdate.textContent = documents.length ? 
        formatDate(Math.max(...documents.map(d => new Date(d.uploadDate)))) : 
        '暂无更新';
}

// 删除文档
async function deleteDocument(id) {
    try {
        // 这里应该调用后端API删除文档
        // 示例中直接从数组中删除
        documents = documents.filter(doc => doc.id !== id);
        renderDocumentsList();
        updateStats();
        showNotification('文档已删除', 'success');
    } catch (error) {
        showNotification('删除文档失败', 'error');
    }
}

// 更新知识库
async function handleKnowledgeBaseUpdate() {
    const button = updateKnowledgeBase;
    if (button.disabled) return;

    try {
        button.disabled = true;
        button.textContent = '更新中...';
        
        // 这里应该调用后端API更新知识库
        await simulateKnowledgeBaseUpdate();
        
        showNotification('知识库更新成功', 'success');
    } catch (error) {
        showNotification('知识库更新失败', 'error');
    } finally {
        button.disabled = false;
        button.textContent = '更新知识库';
    }
}

// 模拟知识库更新
function simulateKnowledgeBaseUpdate() {
    return new Promise((resolve) => {
        setTimeout(resolve, 2000);
    });
}

// 工具函数
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(date) {
    return new Date(date).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function updateUploadUI(isUploading) {
    uploadButton.disabled = isUploading;
    uploadButton.textContent = isUploading ? '上传中...' : '上传文件';
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
    .document-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        border-bottom: 1px solid #eee;
    }

    .document-info {
        flex: 1;
    }

    .document-name {
        font-weight: 500;
        margin-right: 10px;
    }

    .document-size {
        color: #666;
        font-size: 0.9em;
    }

    .document-actions {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .document-date {
        color: #666;
        font-size: 0.9em;
    }

    .delete-btn {
        padding: 5px 10px;
        background-color: var(--accent-color);
        font-size: 14px;
    }

    .delete-btn:hover {
        background-color: #c0392b;
    }

    .no-documents {
        text-align: center;
        color: #666;
        padding: 20px;
    }

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

    .drag-over {
        background-color: #f8f9fa;
        border-color: var(--secondary-color);
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
