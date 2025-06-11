class AdminPanel {
    constructor() {
        this.fileInput = document.getElementById('fileInput');
        this.uploadStatus = document.getElementById('uploadStatus');
        this.fileListContainer = document.getElementById('fileListContainer');
        this.uploadedFiles = new Map();
        this.initializeEventListeners();
        this.loadExistingFiles();
    }

    initializeEventListeners() {
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
    }

    async handleFileSelect(event) {
        const files = Array.from(event.target.files);
        if (files.length === 0) return;

        this.showStatus('正在处理文件...', 'info');

        for (const file of files) {
            try {
                await this.uploadFile(file);
            } catch (error) {
                console.error('上传文件失败:', error);
                this.showStatus(`文件 ${file.name} 上传失败: ${error.message}`, 'error');
            }
        }

        // 清除文件输入以允许重复上传相同文件
        this.fileInput.value = '';
    }

    async uploadFile(file) {
        // 创建FormData对象
        const formData = new FormData();
        formData.append('file', file);

        try {
            // 这里应该是实际的上传API端点
            // const response = await fetch('http://your-api-endpoint/upload', {
            //     method: 'POST',
            //     body: formData
            // });

            // 模拟上传成功
            // 实际项目中，这里应该使用真实的API响应
            const fileId = 'file-' + Date.now();
            const fileInfo = {
                id: fileId,
                name: file.name,
                size: this.formatFileSize(file.size),
                type: file.type,
                uploadDate: new Date().toLocaleString()
            };

            this.uploadedFiles.set(fileId, fileInfo);
            this.updateFileList();
            this.showStatus(`文件 ${file.name} 上传成功！`, 'success');

            // 将文件信息保存到localStorage
            this.saveToLocalStorage();

        } catch (error) {
            throw new Error('上传失败: ' + error.message);
        }
    }

    loadExistingFiles() {
        try {
            const savedFiles = localStorage.getItem('uploadedFiles');
            if (savedFiles) {
                this.uploadedFiles = new Map(JSON.parse(savedFiles));
                this.updateFileList();
            }
        } catch (error) {
            console.error('加载已存在文件失败:', error);
        }
    }

    saveToLocalStorage() {
        try {
            localStorage.setItem('uploadedFiles', 
                JSON.stringify(Array.from(this.uploadedFiles.entries()))
            );
        } catch (error) {
            console.error('保存到localStorage失败:', error);
        }
    }

    updateFileList() {
        if (this.uploadedFiles.size === 0) {
            this.fileListContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <p>暂无上传的文档</p>
                </div>
            `;
            return;
        }

        const fileListHTML = Array.from(this.uploadedFiles.values())
            .map(file => this.createFileItemHTML(file))
            .join('');

        this.fileListContainer.innerHTML = fileListHTML;

        // 添加删除按钮事件监听器
        this.fileListContainer.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const fileId = e.currentTarget.dataset.fileId;
                this.deleteFile(fileId);
            });
        });
    }

    createFileItemHTML(file) {
        return `
            <div class="file-item" id="${file.id}">
                <div class="file-info">
                    <i class="fas fa-file file-icon"></i>
                    <div>
                        <div>${file.name}</div>
                        <small>${file.size} - ${file.uploadDate}</small>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="action-btn delete-btn" data-file-id="${file.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }

    deleteFile(fileId) {
        if (confirm('确定要删除这个文件吗？')) {
            this.uploadedFiles.delete(fileId);
            this.updateFileList();
            this.saveToLocalStorage();
            this.showStatus('文件已删除', 'success');
        }
    }

    showStatus(message, type = 'info') {
        const statusDiv = document.createElement('div');
        statusDiv.className = `status-message ${type}`;
        statusDiv.textContent = message;

        this.uploadStatus.innerHTML = '';
        this.uploadStatus.appendChild(statusDiv);

        // 3秒后自动清除状态消息
        setTimeout(() => {
            statusDiv.remove();
        }, 3000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// 初始化管理面板
document.addEventListener('DOMContentLoaded', () => {
    new AdminPanel();
});
