let currentChatId = null;
let currentUserId = 1; // Для демо

// Загрузити товари
function loadProducts() {
    filterProducts();
}

// Фільтрувати товари
function filterProducts() {
    const name = document.getElementById('searchName').value;
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;
    const category = document.getElementById('categoryFilter').value;
    
    let url = '/api/products?';
    if (name) url += `name=${name}&`;
    if (minPrice) url += `min_price=${minPrice}&`;
    if (maxPrice) url += `max_price=${maxPrice}&`;
    if (category) url += `category=${category}&`;
    
    fetch(url)
        .then(response => response.json())
        .then(products => {
            const productsList = document.getElementById('productsList');
            productsList.innerHTML = '';
            
            if (products.length === 0) {
                productsList.innerHTML = '<p>Товари не знайдені</p>';
                return;
            }
            
            products.forEach(product => {
                const card = document.createElement('div');
                card.className = 'product-card';
                card.innerHTML = `
                    <div class="product-header">
                        <div>Товар ID: ${product.id}</div>
                    </div>
                    <div class="product-info">
                        <div class="product-name">${product.name}</div>
                        <div class="product-price">${product.price} грн</div>
                        <div class="product-category">${product.category}</div>
                        <p>${product.description || 'Опис не вказано'}</p>
                        <button class="product-button" onclick="startChat(${product.id}, ${product.seller_id})">Купити</button>
                    </div>
                `;
                productsList.appendChild(card);
            });
        })
        .catch(error => console.error('Ошибка:', error));
}

// Почати чат
function startChat(productId, sellerId) {
    fetch('/api/chat/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            buyer_id: currentUserId,
            seller_id: sellerId,
            product_id: productId
        })
    })
    .then(response => response.json())
    .then(data => {
        currentChatId = data.chat_id;
        openChat();
        loadMessages();
    })
    .catch(error => console.error('Ошибка:', error));
}

// Открити чат
function openChat() {
    document.getElementById('chatModal').classList.remove('hidden');
}

// Закрити чат
function closeChat() {
    document.getElementById('chatModal').classList.add('hidden');
}

// Загрузити повідомлення
function loadMessages() {
    if (!currentChatId) return;
    
    fetch(`/api/chat/${currentChatId}/messages`)
        .then(response => response.json())
        .then(messages => {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = '';
            
            messages.forEach(msg => {
                const msgDiv = document.createElement('div');
                msgDiv.className = `message ${msg.sender_id === currentUserId ? 'sent' : 'received'}`;
                msgDiv.innerHTML = `
                    <div>${msg.content}</div>
                    <div class="message-time">${new Date(msg.created_at).toLocaleTimeString()}</div>
                `;
                chatMessages.appendChild(msgDiv);
            });
            
            chatMessages.scrollTop = chatMessages.scrollHeight;
        })
        .catch(error => console.error('Ошибка:', error));
}

// Відправити повідомлення
function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const content = messageInput.value.trim();
    
    if (!content || !currentChatId) return;
    
    fetch(`/api/chat/${currentChatId}/message`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            sender_id: currentUserId,
            content: content
        })
    })
    .then(response => response.json())
    .then(data => {
        messageInput.value = '';
        loadMessages();
    })
    .catch(error => console.error('Ошибка:', error));
}

// При завантаженні сторінки
window.addEventListener('DOMContentLoaded', loadProducts);

// Оновлювати повідомлення кожні 2 секунди
setInterval(() => {
    if (currentChatId) {
        loadMessages();
    }
}, 2000);
