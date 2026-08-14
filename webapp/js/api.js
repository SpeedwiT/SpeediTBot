/**
 * ProxiMan Mini App - API Client
 * ارتباط با Backend و Telegram Web App
 */

class ProxiManAPI {
    constructor() {
        this.baseURL = '/api';
        this.tg = window.Telegram?.WebApp;
        this.user = null;
        this.init();
    }

    init() {
        if (this.tg) {
            this.tg.ready();
            this.tg.expand();
            const initData = this.tg.initDataUnsafe;
            this.user = initData?.user || null;
        }
    }

    /**
     * دریافت هدرهای احراز هویت
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (this.tg?.initData) {
            headers['X-Telegram-Init-Data'] = this.tg.initData;
        }
        return headers;
    }

    /**
     * GET request
     */
    async get(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: this.getHeaders(),
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`GET ${endpoint} error:`, error);
            return null;
        }
    }

    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data),
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`POST ${endpoint} error:`, error);
            return null;
        }
    }

    /**
     * دریافت اطلاعات کاربر
     */
    async getUser(telegramId) {
        return this.get(`/users/${telegramId}`);
    }

    /**
     * دریافت لیست محصولات
     */
    async getProducts() {
        return this.get('/products');
    }

    /**
     * دریافت لیست دسته‌بندی‌ها
     */
    async getCategories() {
        return this.get('/categories');
    }

    /**
     * دریافت لیست کارت‌های بانکی
     */
    async getBankCards() {
        return this.get('/cards');
    }

    /**
     * ساخت سفارش جدید
     */
    async createOrder(orderData) {
        return this.post('/orders', orderData);
    }

    /**
     * دریافت سفارشات کاربر
     */
    async getUserOrders(userId) {
        return this.get(`/orders?user_id=${userId}`);
    }

    /**
     * تایید تراکنش
     */
    async verifyTransaction(txId, approve) {
        return this.post(`/transactions/${txId}/verify`, { approve });
    }

    /**
     * دریافت آمار سیستم
     */
    async getStats() {
        return this.get('/stats');
    }

    /**
     * ارسال پیام به ربات
     */
    sendBotMessage(message) {
        if (this.tg) {
            this.tg.sendData(JSON.stringify({
                action: 'message',
                text: message,
            }));
        }
    }

    /**
     * باز کردن لینک خارجی
     */
    openLink(url) {
        if (this.tg) {
            this.tg.openLink(url);
        } else {
            window.open(url, '_blank');
        }
    }

    /**
     * نمایش نوتیفیکیشن تلگرام
     */
    showAlert(message) {
        if (this.tg) {
            this.tg.showAlert(message);
        } else {
            alert(message);
        }
    }

    /**
     * نمایش پاپ‌آپ تایید
     */
    showConfirm(message, callback) {
        if (this.tg) {
            this.tg.showConfirm(message, callback);
        } else {
            callback(confirm(message));
        }
    }
}

// Global API instance
window.api = new ProxiManAPI();
