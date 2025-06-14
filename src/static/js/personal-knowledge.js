/**
 * 个人知识库管理 JavaScript
 * Personal Knowledge Base Management
 */

// 全局变量
let currentSection = 'overview';
let currentUser = null;
let documents = [];
let chatHistory = [];

// 初始化
document.addEventListener('DOMContentLoaded', function () {
    initializePage();
    loadUserInfo();
    loadOverviewData();
    setupEventListeners();
});

// 初始化页面
function initializePage() {
    console.log('个人知识库页面初始化...');

    // 设置拖拽上传
    setupDragAndDrop();

    // 设置搜索输入框回车事件
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                searchDocuments();
            }
        });
    }

    // 设置聊天输入框回车事件
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 上传表单
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUpload);
    }

    // 文件输入框
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }

    // 上传区域点击
    const uploadArea = document.getElementById('upload-area');
    if (uploadArea) {
        uploadArea.addEventListener('click', function () {
            fileInput.click();
        });
    }
}

// 设置拖拽上传
function setupDragAndDrop() {
    const uploadArea = document.getElementById('upload-area');
    if (!uploadArea) return;

    uploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function (e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        this.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const fileInput = document.getElementById('file-input');
            fileInput.files = files;
            handleFileSelect({ target: fileInput });
        }
    });
}

// 切换页面部分
function showSection(sectionName) {
    // 隐藏所有部分
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });

    // 移除所有侧边栏项目的活动状态
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.classList.remove('active');
    });

    // 显示选中的部分
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.classList.remove('hidden');
    }

    // 激活对应的侧边栏项目
    const activeItem = document.querySelector(`[onclick="showSection('${sectionName}')"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }

    currentSection = sectionName;

    // 根据部分加载相应数据
    switch (sectionName) {
        case 'overview':
            loadOverviewData();
            break;
        case 'documents':
            loadDocuments();
            break;
        case 'search':
            // 搜索页面不需要预加载
            break;
        case 'ai-chat':
            loadChatHistory();
            break;
        case 'categories':
            loadCategories();
            break;
        case 'settings':
            loadSettings();
            break;
    }
}

// 加载用户信息
async function loadUserInfo() {
    try {
        // 这里应该从后端获取用户信息
        // 暂时使用模拟数据
        currentUser = {
            id: 1,
            username: '用户',
            email: 'user@example.com'
        };

        const userInfoElement = document.getElementById('user-info');
        if (userInfoElement) {
            userInfoElement.textContent = `欢迎，${currentUser.username}`;
        }
    } catch (error) {
        console.error('加载用户信息失败:', error);
    }
}

// 加载概览数据
async function loadOverviewData() {
    try {
        // 这里应该从后端API获取统计数据
        // 暂时使用模拟数据
        const stats = {
            totalDocuments: 0,
            totalSize: 0,
            totalCategories: 0,
            totalChats: 0
        };

        // 更新统计卡片
        updateElement('total-documents', stats.totalDocuments);
        updateElement('total-size', `${stats.totalSize} MB`);
        updateElement('total-categories', stats.totalCategories);
        updateElement('total-chats', stats.totalChats);

        // 加载最近活动
        loadRecentActivities();

        // 加载分类概览
        loadCategoryOverview();

    } catch (error) {
        console.error('加载概览数据失败:', error);
    }
}

// 加载最近活动
async function loadRecentActivities() {
    try {
        const container = document.getElementById('recent-activities');
        if (!container) return;

        // 模拟数据
        const activities = [];

        if (activities.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-history text-3xl mb-2"></i>
                    <p>暂无活动记录</p>
                </div>
            `;
        } else {
            container.innerHTML = activities.map(activity => `
                <div class="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50">
                    <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <i class="fas fa-${activity.icon} text-blue-600 text-sm"></i>
                    </div>
                    <div class="flex-1">
                        <p class="text-sm font-medium text-gray-900">${activity.title}</p>
                        <p class="text-xs text-gray-500">${activity.time}</p>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载最近活动失败:', error);
    }
}

// 加载分类概览
async function loadCategoryOverview() {
    try {
        const container = document.getElementById('category-overview');
        if (!container) return;

        // 模拟数据
        const categories = [];

        if (categories.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500 col-span-full">
                    <i class="fas fa-folder-open text-3xl mb-2"></i>
                    <p>暂无文档分类</p>
                </div>
            `;
        } else {
            container.innerHTML = categories.map(category => `
                <div class="text-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer">
                    <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                        <i class="fas fa-${category.icon} text-blue-600"></i>
                    </div>
                    <p class="text-sm font-medium text-gray-900">${category.name}</p>
                    <p class="text-xs text-gray-500">${category.count} 个文档</p>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载分类概览失败:', error);
    }
}

// 处理文件选择
function handleFileSelect(event) {
    const files = event.target.files;
    if (!files.length) return;

    const fileList = document.getElementById('file-list');
    const placeholder = document.getElementById('upload-placeholder');

    if (files.length === 1) {
        // 单个文件
        const file = files[0];
        placeholder.style.display = 'none';
        fileList.style.display = 'block';
        fileList.innerHTML = `
            <div class="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                <i class="fas fa-file text-blue-600"></i>
                <div class="flex-1">
                    <p class="font-medium text-gray-900">${file.name}</p>
                    <p class="text-sm text-gray-500">${formatFileSize(file.size)}</p>
                </div>
                <button type="button" onclick="clearFileSelection()" class="text-red-600 hover:text-red-800">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    } else {
        // 多个文件
        placeholder.style.display = 'none';
        fileList.style.display = 'block';
        fileList.innerHTML = Array.from(files).map((file, index) => `
            <div class="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                <i class="fas fa-file text-blue-600"></i>
                <div class="flex-1">
                    <p class="font-medium text-gray-900">${file.name}</p>
                    <p class="text-sm text-gray-500">${formatFileSize(file.size)}</p>
                </div>
                <button type="button" onclick="removeFile(${index})" class="text-red-600 hover:text-red-800">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }
}

// 清除文件选择
function clearFileSelection() {
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const placeholder = document.getElementById('upload-placeholder');

    fileInput.value = '';
    fileList.style.display = 'none';
    placeholder.style.display = 'block';
}

// 处理文档上传
async function handleUpload(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const files = formData.getAll('file');

    if (!files.length || files[0].size === 0) {
        showNotification('请选择要上传的文件', 'error');
        return;
    }

    const progressContainer = document.getElementById('upload-progress');
    const progressBar = document.getElementById('upload-progress-bar');
    const statusText = document.getElementById('upload-status');
    const submitButton = form.querySelector('button[type="submit"]');

    try {
        // 显示进度
        progressContainer.classList.remove('hidden');
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>上传中...';

        // 模拟上传进度
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress > 90) progress = 90;
            progressBar.style.width = `${progress}%`;
            statusText.textContent = `上传中... ${Math.round(progress)}%`;
        }, 200);

        // 发送到后端
        const response = await fetch('/api/personal-knowledge/upload', {
            method: 'POST',
            body: formData
        });

        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        statusText.textContent = '处理中...';

        const data = await response.json();

        if (data.success) {
            showNotification('文档上传成功！', 'success');
            resetUploadForm();

            // 刷新相关数据
            loadOverviewData();
            if (currentSection === 'documents') {
                loadDocuments();
            }
        } else {
            throw new Error(data.error || '上传失败');
        }

    } catch (error) {
        console.error('上传失败:', error);
        showNotification(error.message || '文档上传失败，请稍后重试', 'error');
    } finally {
        // 重置UI
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-upload mr-2"></i>上传文档';

        setTimeout(() => {
            progressContainer.classList.add('hidden');
            progressBar.style.width = '0%';
        }, 2000);
    }
}

// 重置上传表单
function resetUploadForm() {
    const form = document.getElementById('upload-form');
    if (form) {
        form.reset();
        clearFileSelection();
    }
}

// 加载文档列表
async function loadDocuments() {
    try {
        const container = document.getElementById('documents-table');
        if (!container) return;

        container.innerHTML = `
            <div class="text-center py-12">
                <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600 mx-auto"></div>
                <p class="text-gray-500 mt-4">加载文档列表...</p>
            </div>
        `;

        const response = await fetch('/api/personal-knowledge/documents');
        const data = await response.json();

        if (data.success && data.documents && data.documents.length > 0) {
            container.innerHTML = `
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">文档</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">分类</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">大小</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">上传时间</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${data.documents.map(doc => `
                            <tr class="hover:bg-gray-50">
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="flex items-center">
                                        <i class="fas fa-file-alt text-gray-400 mr-3"></i>
                                        <div>
                                            <div class="text-sm font-medium text-gray-900">${doc.original_filename}</div>
                                            <div class="text-sm text-gray-500">${doc.content_summary || '无描述'}</div>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                                        ${getCategoryName(doc.category)}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    ${formatFileSize(doc.file_size)}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    ${formatDate(doc.upload_time)}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    <button onclick="askDocumentQuestion('${doc.doc_id}', '${doc.original_filename}')" class="text-blue-600 hover:text-blue-900 mr-3">
                                        <i class="fas fa-question-circle mr-1"></i>问答
                                    </button>
                                    <button onclick="deleteDocument('${doc.doc_id}')" class="text-red-600 hover:text-red-900">
                                        <i class="fas fa-trash mr-1"></i>删除
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = `
                <div class="text-center py-12">
                    <i class="fas fa-folder-open text-4xl text-gray-400 mb-4"></i>
                    <p class="text-lg text-gray-500 mb-2">暂无文档</p>
                    <p class="text-sm text-gray-400">点击上传文档开始构建你的知识库</p>
                </div>
            `;
        }

    } catch (error) {
        console.error('加载文档列表失败:', error);
        const container = document.getElementById('documents-table');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-12">
                    <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
                    <p class="text-lg text-gray-500">加载失败</p>
                    <p class="text-sm text-gray-400">请稍后重试</p>
                </div>
            `;
        }
    }
}

// 搜索文档
async function searchDocuments() {
    const searchInput = document.getElementById('search-input');
    const query = searchInput.value.trim();

    if (!query) {
        showNotification('请输入搜索关键词', 'error');
        return;
    }

    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;

    try {
        resultsContainer.innerHTML = `
            <div class="p-8 text-center">
                <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600 mx-auto"></div>
                <p class="text-gray-500 mt-4">搜索中...</p>
            </div>
        `;

        const response = await fetch(`/api/personal-knowledge/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success && data.results && data.results.length > 0) {
            resultsContainer.innerHTML = `
                <div class="p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">
                        找到 ${data.results.length} 个相关结果
                    </h3>
                    <div class="space-y-4">
                        ${data.results.map(result => `
                            <div class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-all">
                                <div class="flex justify-between items-start mb-2">
                                    <h4 class="font-medium text-gray-900">${result.original_filename}</h4>
                                    <span class="text-xs text-gray-500">${formatDate(result.upload_time)}</span>
                                </div>
                                <p class="text-sm text-gray-600 mb-3">${result.content_summary || '无描述'}</p>
                                <div class="flex justify-between items-center">
                                    <div class="flex space-x-2">
                                        <span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">${getCategoryName(result.category)}</span>
                                        ${result.tags ? result.tags.map(tag => `<span class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">${tag}</span>`).join('') : ''}
                                    </div>
                                    <button onclick="askDocumentQuestion('${result.doc_id}', '${result.original_filename}')" class="text-blue-600 hover:text-blue-800 text-sm">
                                        <i class="fas fa-question-circle mr-1"></i>问答
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            resultsContainer.innerHTML = `
                <div class="p-8 text-center text-gray-500">
                    <i class="fas fa-search text-4xl mb-4"></i>
                    <p class="text-lg mb-2">未找到相关结果</p>
                    <p class="text-sm">尝试使用不同的关键词或上传更多文档</p>
                </div>
            `;
        }

    } catch (error) {
        console.error('搜索失败:', error);
        resultsContainer.innerHTML = `
            <div class="p-8 text-center text-gray-500">
                <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
                <p class="text-lg">搜索失败</p>
                <p class="text-sm">请稍后重试</p>
            </div>
        `;
    }
}

// 发送AI消息
async function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();

    if (!message) return;

    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) return;

    // 添加用户消息
    addChatMessage('user', message);
    chatInput.value = '';

    // 添加AI思考状态
    const thinkingId = addChatMessage('ai', '正在思考...', true);

    try {
        const response = await fetch('/api/personal-knowledge/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                history: chatHistory.slice(-10) // 只发送最近10条消息
            })
        });

        const data = await response.json();

        // 移除思考状态
        document.getElementById(thinkingId).remove();

        if (data.success) {
            addChatMessage('ai', data.response);

            // 如果有相关文档，显示引用
            if (data.related_documents && data.related_documents.length > 0) {
                const references = data.related_documents.map(doc =>
                    `<span class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-1 mb-1">${doc.filename}</span>`
                ).join('');
                addChatMessage('system', `参考文档：${references}`);
            }
        } else {
            addChatMessage('ai', '抱歉，我现在无法回答这个问题。请稍后再试。');
        }

    } catch (error) {
        console.error('发送消息失败:', error);
        document.getElementById(thinkingId).remove();
        addChatMessage('ai', '抱歉，发生了错误。请稍后再试。');
    }
}

// 添加聊天消息
function addChatMessage(type, content, isTemporary = false) {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) return;

    const messageId = isTemporary ? `temp-${Date.now()}` : null;
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-3';
    if (messageId) messageDiv.id = messageId;

    if (type === 'user') {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
                <i class="fas fa-user text-white text-sm"></i>
            </div>
            <div class="bg-green-100 rounded-lg p-3 max-w-md">
                <p class="text-sm">${content}</p>
            </div>
        `;
        chatHistory.push({ type: 'user', content: content });
    } else if (type === 'ai') {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <i class="fas fa-robot text-white text-sm"></i>
            </div>
            <div class="bg-gray-100 rounded-lg p-3 max-w-md">
                <p class="text-sm">${content}</p>
            </div>
        `;
        if (!isTemporary) {
            chatHistory.push({ type: 'ai', content: content });
        }
    } else if (type === 'system') {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center">
                <i class="fas fa-info text-white text-sm"></i>
            </div>
            <div class="bg-gray-50 rounded-lg p-3 max-w-md">
                <div class="text-xs text-gray-600">${content}</div>
            </div>
        `;
    }

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return messageId;
}

// 基于文档提问
function askDocumentQuestion(docId, filename) {
    showSection('ai-chat');

    // 预填充问题
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.value = `请基于文档"${filename}"回答我的问题：这个文档的主要内容是什么？`;
        chatInput.focus();
    }
}

// 删除文档
async function deleteDocument(docId) {
    if (!confirm('确定要删除这个文档吗？此操作不可撤销。')) {
        return;
    }

    try {
        const response = await fetch(`/api/personal-knowledge/delete/${docId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showNotification('文档删除成功', 'success');

            // 刷新相关数据
            loadOverviewData();
            if (currentSection === 'documents') {
                loadDocuments();
            }
        } else {
            throw new Error(data.error || '删除失败');
        }
    } catch (error) {
        console.error('删除文档失败:', error);
        showNotification(error.message || '删除文档失败，请稍后重试', 'error');
    }
}

// 刷新文档列表
function refreshDocuments() {
    if (currentSection === 'documents') {
        loadDocuments();
    }
    showNotification('文档列表已刷新', 'info');
}

// 导出文档
function exportDocuments() {
    // 这里可以实现文档导出功能
    showNotification('导出功能开发中...', 'info');
}

// 筛选文档
function filterDocuments() {
    // 这里可以实现文档筛选功能
    showNotification('筛选功能开发中...', 'info');
}

// 加载聊天历史
function loadChatHistory() {
    // 聊天历史已经在内存中维护
}

// 加载分类
async function loadCategories() {
    try {
        // 加载分类列表
        await loadCategoriesList();
        // 加载标签云
        await loadTagsCloud();
    } catch (error) {
        console.error('加载分类失败:', error);
        showNotification('加载分类信息失败', 'error');
    }
}

// 加载分类列表
async function loadCategoriesList() {
    try {
        const container = document.getElementById('categories-list');
        if (!container) return;

        const response = await fetch('/api/personal-knowledge/categories');
        const data = await response.json();

        if (data.success && data.categories && data.categories.length > 0) {
            container.innerHTML = data.categories.map(category => `
                <div class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-blue-300 cursor-pointer"
                     onclick="showCategoryDetails('${category.name}')">
                    <div class="flex items-center space-x-3">
                        <div class="w-4 h-4 rounded-full" style="background-color: ${category.color}"></div>
                        <div>
                            <p class="font-medium text-gray-900">${category.display_name}</p>
                            <p class="text-sm text-gray-500">${category.description}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="text-lg font-semibold text-gray-900">${category.count}</p>
                        <p class="text-xs text-gray-500">个文档</p>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-folder text-3xl mb-2"></i>
                    <p>暂无分类</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('加载分类列表失败:', error);
    }
}

// 加载标签云
async function loadTagsCloud() {
    try {
        const container = document.getElementById('tags-cloud');
        if (!container) return;

        const response = await fetch('/api/personal-knowledge/tags');
        const data = await response.json();

        if (data.success && data.tags && data.tags.length > 0) {
            container.innerHTML = `
                <div class="flex flex-wrap gap-2">
                    ${data.tags.map(tag => `
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 hover:bg-blue-200 cursor-pointer"
                              onclick="searchByTag('${tag.name}')">
                            ${tag.name}
                            <span class="ml-1 text-xs">(${tag.count})</span>
                        </span>
                    `).join('')}
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-tags text-3xl mb-2"></i>
                    <p>暂无标签</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('加载标签云失败:', error);
    }
}

// 显示分类详情
async function showCategoryDetails(categoryName) {
    try {
        const response = await fetch(`/api/personal-knowledge/categories/${categoryName}/documents`);
        const data = await response.json();

        if (data.success) {
            const detailsContainer = document.getElementById('category-details');
            const titleElement = document.getElementById('category-title');
            const descriptionElement = document.getElementById('category-description');
            const documentsContainer = document.getElementById('category-documents');

            titleElement.textContent = data.category;
            descriptionElement.textContent = `包含 ${data.count} 个文档`;

            if (data.documents && data.documents.length > 0) {
                documentsContainer.innerHTML = data.documents.map(doc => `
                    <div class="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                        <div class="flex items-center space-x-3">
                            <i class="fas fa-file-alt text-gray-400"></i>
                            <div>
                                <p class="font-medium text-gray-900">${doc.original_filename}</p>
                                <p class="text-sm text-gray-500">${formatDate(doc.upload_time)}</p>
                            </div>
                        </div>
                        <div class="flex space-x-2">
                            <button onclick="askDocumentQuestion('${doc.doc_id}', '${doc.original_filename}')" 
                                    class="text-blue-600 hover:text-blue-800 text-sm">
                                <i class="fas fa-question-circle"></i>
                            </button>
                        </div>
                    </div>
                `).join('');
            } else {
                documentsContainer.innerHTML = `
                    <div class="text-center py-8 text-gray-500">
                        <p>该分类下暂无文档</p>
                    </div>
                `;
            }

            detailsContainer.classList.remove('hidden');
        }
    } catch (error) {
        console.error('加载分类详情失败:', error);
        showNotification('加载分类详情失败', 'error');
    }
}

// 关闭分类详情
function closeCategoryDetails() {
    const detailsContainer = document.getElementById('category-details');
    if (detailsContainer) {
        detailsContainer.classList.add('hidden');
    }
}

// 按标签搜索
function searchByTag(tagName) {
    showSection('search');
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = tagName;
        searchDocuments();
    }
}

// 加载设置
async function loadSettings() {
    try {
        const response = await fetch('/api/personal-knowledge/settings');
        const data = await response.json();

        if (data.success) {
            const settings = data.settings;

            // 填充设置表单
            document.getElementById('settings-ai-style').value = settings.ai_style || 'detailed';
            document.getElementById('settings-knowledge-scope').value = settings.knowledge_scope || 'all';
            document.getElementById('settings-preferred-provider').value = settings.ai_preferences?.preferred_provider || 'auto';
            document.getElementById('settings-response-length').value = settings.ai_preferences?.response_length || 'medium';

            document.getElementById('settings-auto-categorize').checked = settings.auto_categorize || false;
            document.getElementById('settings-smart-tags').checked = settings.smart_tags || false;
            document.getElementById('settings-include-sources').checked = settings.ai_preferences?.include_sources || false;
            document.getElementById('settings-explain-reasoning').checked = settings.ai_preferences?.explain_reasoning || false;

            document.getElementById('settings-upload-success').checked = settings.notifications?.upload_success || false;
            document.getElementById('settings-ai-response').checked = settings.notifications?.ai_response || false;
            document.getElementById('settings-daily-summary').checked = settings.notifications?.daily_summary || false;

            document.getElementById('settings-default-visibility').value = settings.privacy?.default_visibility || 'private';
            document.getElementById('settings-allow-sharing').checked = settings.privacy?.allow_sharing || false;
        }
    } catch (error) {
        console.error('加载设置失败:', error);
        showNotification('加载设置失败', 'error');
    }
}

// 保存设置
async function saveSettings() {
    try {
        const settings = {
            ai_style: document.getElementById('settings-ai-style').value,
            knowledge_scope: document.getElementById('settings-knowledge-scope').value,
            auto_categorize: document.getElementById('settings-auto-categorize').checked,
            smart_tags: document.getElementById('settings-smart-tags').checked,
            notifications: {
                upload_success: document.getElementById('settings-upload-success').checked,
                ai_response: document.getElementById('settings-ai-response').checked,
                daily_summary: document.getElementById('settings-daily-summary').checked
            },
            privacy: {
                default_visibility: document.getElementById('settings-default-visibility').value,
                allow_sharing: document.getElementById('settings-allow-sharing').checked
            },
            ai_preferences: {
                preferred_provider: document.getElementById('settings-preferred-provider').value,
                response_length: document.getElementById('settings-response-length').value,
                include_sources: document.getElementById('settings-include-sources').checked,
                explain_reasoning: document.getElementById('settings-explain-reasoning').checked
            }
        };

        const response = await fetch('/api/personal-knowledge/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });

        const data = await response.json();

        if (data.success) {
            showSettingsStatus('设置保存成功！', 'success');
        } else {
            throw new Error(data.error || '保存失败');
        }
    } catch (error) {
        console.error('保存设置失败:', error);
        showSettingsStatus('保存设置失败', 'error');
    }
}

// 重置设置
async function resetSettings() {
    if (!confirm('确定要重置所有设置为默认值吗？')) {
        return;
    }

    try {
        const response = await fetch('/api/personal-knowledge/settings/reset', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showSettingsStatus('设置已重置为默认值', 'success');
            // 重新加载设置
            setTimeout(() => {
                loadSettings();
            }, 1000);
        } else {
            throw new Error(data.error || '重置失败');
        }
    } catch (error) {
        console.error('重置设置失败:', error);
        showSettingsStatus('重置设置失败', 'error');
    }
}

// 显示设置状态
function showSettingsStatus(message, type) {
    const statusContainer = document.getElementById('settings-status');
    const messageElement = document.getElementById('settings-message');

    if (statusContainer && messageElement) {
        messageElement.textContent = message;

        // 更新样式
        statusContainer.className = 'mt-4';
        if (type === 'success') {
            statusContainer.innerHTML = `
                <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                    <i class="fas fa-check-circle mr-2"></i>
                    <span>${message}</span>
                </div>
            `;
        } else {
            statusContainer.innerHTML = `
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    <i class="fas fa-exclamation-circle mr-2"></i>
                    <span>${message}</span>
                </div>
            `;
        }

        statusContainer.classList.remove('hidden');

        // 3秒后自动隐藏
        setTimeout(() => {
            statusContainer.classList.add('hidden');
        }, 3000);
    }
}

// 工具函数
function updateElement(id, content) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = content;
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getCategoryName(category) {
    const categoryNames = {
        'personal': '个人学习',
        'research': '研究资料',
        'course': '课程笔记',
        'reference': '参考文献',
        'project': '项目文档',
        'teaching': '教学资料',
        'other': '其他'
    };
    return categoryNames[category] || category;
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transition-all duration-300`;

    // 设置样式
    switch (type) {
        case 'success':
            notification.className += ' bg-green-500 text-white';
            break;
        case 'error':
            notification.className += ' bg-red-500 text-white';
            break;
        case 'warning':
            notification.className += ' bg-yellow-500 text-white';
            break;
        default:
            notification.className += ' bg-blue-500 text-white';
    }

    notification.innerHTML = `
        <div class="flex items-center space-x-2">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    // 自动消失
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}
