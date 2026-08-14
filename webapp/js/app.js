/**
 * ProxiMan Mini App - Main Application Logic
 * منطق اصلی مینی‌اپ
 */

document.addEventListener('DOMContentLoaded', () => {
    const app = new ProxiManApp();
    app.init();
});

class ProxiManApp {
    constructor() {
        this.api = window.api;
        this.tg = window.Telegram?.WebApp;
        this.state = {
            user: null,
            categories: [],
            products: [],
            bankCards: [],
            selectedProduct: null,
            selectedCard: null,
            currentCategory: null,
            balance: 0,
        };

        // DOM elements
        this.elements = {
            categoriesList: document.getElementById('categories-list'),
            productsList: document.getElementById('products-list'),
            userBalance: document.getElementById('user-balance'),
            productModal: document.getElementById('product-modal'),
            purchaseModal: document.getElementById('purchase-modal'),
            successModal: document.getElementById('success-modal'),
            cardInfo: document.getElementById('card-info'),
            receiptUpload: document.getElementById('receipt-upload'),
        };
    }

    async init() {
        this.bindEvents();
        await this.loadUser();
        await this.loadCategories();
        await this.loadProducts();
        await this.loadBankCards();
    }

    bindEvents() {
        // Modal close buttons
        document.getElementById('modal-close')?.addEventListener('click', () => {
            this.closeModal('productModal');
        });
        document.getElementById('purchase-close')?.addEventListener('click', () => {
            this.closeModal('purchaseModal');
        });
        document.getElementById('btn-close')?.addEventListener('click', () => {
            this.closeModal('productModal');
        });
        document.getElementById('btn-cancel-pay')?.addEventListener('click', () => {
            this.closeModal('purchaseModal');
        });
        document.getElementById('btn-close-success')?.addEventListener('click', () => {
            this.closeModal('successModal');
        });

        // Buy button
        document.getElementById('btn-buy')?.addEventListener('click', () => {
            this.openPurchaseModal();
        });

        // Confirm payment button
        document.getElementById('btn-confirm-pay')?.addEventListener('click', () => {
            this.initiatePayment();
        });

        // Payment method selection
        document.querySelectorAll('.payment-method').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.payment-method').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.togglePaymentMethod(e.target.dataset.method);
            });
        });

        // Receipt upload
        document.getElementById('receipt-input')?.addEventListener('change', (e) => {
            this.handleReceiptUpload(e);
        });
        document.getElementById('btn-submit-receipt')?.addEventListener('click', () => {
            this.submitReceipt();
        });

        // Copy subscription link
        document.getElementById('btn-copy')?.addEventListener('click', () => {
            this.copyToClipboard('sub-link');
        });
    }

    async loadUser() {
        if (!this.api.user?.id) return;

        const userData = await this.api.getUser(this.api.user.id);
        if (userData) {
            this.state.user = userData;
            this.state.balance = userData.balance || 0;
            this.elements.userBalance.textContent = this.formatPrice(this.state.balance);
        }
    }

    async loadCategories() {
        const categories = await this.api.getCategories();
        if (categories && categories.length > 0) {
            this.state.categories = categories;
            this.renderCategories();
        } else {
            // Default categories if API fails
            this.state.categories = [
                { id: 1, name: 'سرور اروپا', icon: '🇩🇪' },
                { id: 2, name: 'سرور آمریکا', icon: '🇺🇸' },
                { id: 3, name: 'سرور آسیا', icon: '🇯🇵' },
                { id: 4, name: 'سرویس ویژه', icon: '⭐' },
            ];
            this.renderCategories();
        }
    }

    renderCategories() {
        const html = this.state.categories.map(cat => `
            <div class="category-card" data-category-id="${cat.id}">
                <div class="category-icon">${cat.icon || '📦'}</div>
                <div class="category-name">${cat.name}</div>
            </div>
        `).join('');

        this.elements.categoriesList.innerHTML = html;

        // Add click handlers
        this.elements.categoriesList.querySelectorAll('.category-card').forEach(card => {
            card.addEventListener('click', () => {
                const categoryId = card.dataset.categoryId;
                this.selectCategory(categoryId);
            });
        });
    }

    async loadProducts() {
        const products = await this.api.getProducts();
        if (products && products.length > 0) {
            this.state.products = products;
            this.renderProducts(products);
        } else {
            // Default products if API fails
            this.state.products = [
                { id: 1, name: 'وی‌پی یک ماهه اروپا', price: 150000, duration_days: 30, traffic_gb: 50, max_connections: 2, category_id: 1 },
                { id: 2, name: 'وی‌پی دو ماهه اروپا', price: 250000, duration_days: 60, traffic_gb: 100, max_connections: 3, category_id: 1 },
                { id: 3, name: 'وی‌پی یک ماهه آمریکا', price: 200000, duration_days: 30, traffic_gb: 50, max_connections: 2, category_id: 2 },
                { id: 4, name: 'وی‌پی نامحدود ویژه', price: 500000, duration_days: 90, traffic_gb: 0, max_connections: 5, category_id: 4 },
            ];
            this.renderProducts(this.state.products);
        }
    }

    renderProducts(products) {
        if (!products || products.length === 0) {
            this.elements.productsList.innerHTML = '<p style="text-align:center;color:#999;">محصولی یافت نشد</p>';
            return;
        }

        const html = products.map(p => `
            <div class="product-card" data-product-id="${p.id}">
                <div class="product-header">
                    <span class="product-name">${p.name}</span>
                    <span class="product-price">${this.formatPrice(p.price)}</span>
                </div>
                <div class="product-features">
                    <span>📅 ${p.duration_days} روز</span>
                    <span>📊 ${p.traffic_gb === 0 ? 'نامحدود' : p.traffic_gb + ' گیگ'}</span>
                    <span>👥 ${p.max_connections} کاربر</span>
                </div>
            </div>
        `).join('');

        this.elements.productsList.innerHTML = html;

        // Add click handlers
        this.elements.productsList.querySelectorAll('.product-card').forEach(card => {
            card.addEventListener('click', () => {
                const productId = parseInt(card.dataset.productId);
                this.selectProduct(productId);
            });
        });
    }

    selectCategory(categoryId) {
        this.state.currentCategory = categoryId;
        const filtered = this.state.products.filter(p => p.category_id == categoryId);
        this.renderProducts(filtered);
    }

    selectProduct(productId) {
        const product = this.state.products.find(p => p.id === productId);
        if (!product) return;

        this.state.selectedProduct = product;

        // Populate modal
        document.getElementById('modal-title').textContent = product.name;
        document.getElementById('modal-duration').textContent = `${product.duration_days} روز`;
        document.getElementById('modal-traffic').textContent = product.traffic_gb === 0 ? 'نامحدود' : `${product.traffic_gb} گیگابایت`;
        document.getElementById('modal-connections').textContent = `${product.max_connections} کاربر`;
        document.getElementById('modal-price').textContent = this.formatPrice(product.price);

        // Show modal
        this.openModal('productModal');
    }

    openModal(modalName) {
        this.elements[modalName]?.classList.add('active');
    }

    closeModal(modalName) {
        this.elements[modalName]?.classList.remove('active');
    }

    async loadBankCards() {
        const cards = await this.api.getBankCards();
        if (cards && cards.length > 0) {
            this.state.bankCards = cards;
        }
    }

    openPurchaseModal() {
        this.closeModal('productModal');
        this.openModal('purchaseModal');

        // Reset state
        this.state.selectedCard = null;
        this.elements.cardInfo.style.display = 'none';
        this.elements.receiptUpload.style.display = 'none';

        // Render bank cards
        this.renderBankCards();
    }

    renderBankCards() {
        const container = document.getElementById('bank-cards-list');
        if (!this.state.bankCards || this.state.bankCards.length === 0) {
            container.innerHTML = '<p style="text-align:center;color:#999;">کارت بانکی فعالی وجود ندارد</p>';
            return;
        }

        const html = this.state.bankCards.map(card => `
            <div class="bank-card" data-card-id="${card.id}">
                <div class="bank-card-number">${card.card_number}</div>
                <div class="bank-card-holder">${card.card_holder}</div>
                <div style="margin-top:4px;font-size:12px;opacity:0.7;">${card.bank_name || 'بانک'}</div>
            </div>
        `).join('');

        container.innerHTML = html;

        // Add click handlers
        container.querySelectorAll('.bank-card').forEach(card => {
            card.addEventListener('click', () => {
                const cardId = card.dataset.cardId;
                this.selectBankCard(cardId);
            });
        });
    }

    selectBankCard(cardId) {
        const card = this.state.bankCards.find(c => c.id == cardId);
        if (!card) return;

        this.state.selectedCard = card;

        // Show card info
        this.elements.cardInfo.style.display = 'block';
        this.elements.receiptUpload.style.display = 'block';

        // Update card details
        const product = this.state.selectedProduct;
        const details = document.getElementById('card-details');
        details.innerHTML = `
            <p><strong>شماره کارت:</strong> ${card.card_number}</p>
            <p><strong>به نام:</strong> ${card.card_holder}</p>
            <p><strong>مبلغ:</strong> ${this.formatPrice(product.price)}</p>
        `;
    }

    togglePaymentMethod(method) {
        const cardList = document.getElementById('bank-cards-list');
        if (method === 'balance') {
            cardList.innerHTML = '<p style="text-align:center;color:#2ecc71;">از موجودی کیف پول استفاده می‌شود</p>';
            this.elements.cardInfo.style.display = 'none';
            this.elements.receiptUpload.style.display = 'none';
        } else {
            this.renderBankCards();
        }
    }

    async initiatePayment() {
        const product = this.state.selectedProduct;
        if (!product) {
            this.api.showAlert('لطفاً یک محصول انتخاب کنید');
            return;
        }

        const activeMethod = document.querySelector('.payment-method.active')?.dataset.method;

        if (activeMethod === 'balance') {
            // Check balance
            if (this.state.balance < product.price) {
                this.api.showAlert('موجودی کافی نیست. لطفاً ابتدا کیف پول خود را شارژ کنید.');
                return;
            }

            // Create order with balance payment
            const result = await this.api.createOrder({
                user_id: this.state.user?.id,
                product_id: product.id,
                order_type: 'config',
                amount: product.price,
                payment_method: 'balance',
            });

            if (result) {
                this.api.showAlert('✅ خرید با موفقیت انجام شد!');
                this.closeModal('purchaseModal');
            }
        } else {
            // Card-to-card payment
            if (!this.state.selectedCard) {
                this.api.showAlert('لطفاً یک کارت بانکی انتخاب کنید');
                return;
            }

            // Show receipt upload
            this.elements.receiptUpload.style.display = 'block';
            this.api.showAlert('لطفاً ابتدا مبلغ را به کارت انتخاب شده واریز کنید و سپس فیش را آپلود کنید.');
        }
    }

    handleReceiptUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.api.showAlert('لطفاً یک تصویر ارسال کنید');
            event.target.value = '';
            return;
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            this.api.showAlert('حداکثر حجم فایل ۵ مگابایت است');
            event.target.value = '';
            return;
        }

        this.state.receiptFile = file;
    }

    async submitReceipt() {
        if (!this.state.receiptFile) {
            this.api.showAlert('لطفاً ابتدا فیش واریزی را آپلود کنید');
            return;
        }

        const product = this.state.selectedProduct;
        const card = this.state.selectedCard;

        // In real implementation, upload file to server
        // For now, send message to admin via bot
        this.api.sendBotMessage(`📷 فیش واریزی جدید برای محصول "${product.name}" به مبلغ ${this.formatPrice(product.price)}`);

        this.api.showAlert('✅ فیش شما دریافت شد. پس از تایید توسط ادمین، کانفیگ تحویل داده می‌شود.');
        this.closeModal('purchaseModal');
    }

    copyToClipboard(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;

        navigator.clipboard.writeText(element.value).then(() => {
            this.api.showAlert('✅ لینک کپی شد!');
        }).catch(() => {
            // Fallback
            element.select();
            document.execCommand('copy');
            this.api.showAlert('✅ لینک کپی شد!');
        });
    }

    formatPrice(amount) {
        if (!amount) return '۰';
        return amount.toLocaleString('fa-IR');
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.app = new ProxiManApp();
        window.app.init();
    });
} else {
    window.app = new ProxiManApp();
    window.app.init();
}
