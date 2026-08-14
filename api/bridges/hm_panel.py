"""HM Panel Bridge - اتصال به پنل HMPanel (neoauroraproject/hmpanel)"""

from typing import Any, Dict, List, Optional
import aiohttp
import time


class HMPanelBridge:
    """
    پل ارتباطی با HM Panel - سیستم مدیریت پنل‌های 3x-ui
    
    HM Panel یک لایه مدیریت حرفه‌ای روی پنل‌های 3x-ui است که با NestJS نوشته شده
    و API REST مناسبی دارد.
    
    ساختار API:
    - Base URL: http://host:port/api/v1
    - Auth: Bearer Token
    - Endpoints: /admins, /clients, /inbounds, /panels, /system
    """

    def __init__(self, panel):
        self.panel = panel
        # HM Panel پورت پیش‌فرض 3001 دارد
        self.base_url = f"http://{panel.host}:{panel.port}/api/v1"
        self._session: Optional[aiohttp.ClientSession] = None
        self._token: Optional[str] = None
        self._token_expire: float = 0

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"Content-Type": "application/json"},
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        auth: bool = True,
    ) -> Dict[str, Any]:
        """ارسال درخواست به API"""
        session = await self.get_session()
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}
        
        if auth and self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            if method == "GET":
                async with session.get(url, headers=headers) as resp:
                    return await resp.json()
            elif method == "POST":
                async with session.post(url, json=data, headers=headers) as resp:
                    return await resp.json()
            elif method == "PUT":
                async with session.put(url, json=data, headers=headers) as resp:
                    return await resp.json()
            elif method == "DELETE":
                async with session.delete(url, headers=headers) as resp:
                    return await resp.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========== Auth ==========

    async def authenticate(self) -> bool:
        """احراز هویت و دریافت توکن از HM Panel"""
        session = await self.get_session()
        url = f"{self.base_url}/auth/login"
        payload = {
            "username": self.panel.username,
            "password": self.panel.password,
        }
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._token = data.get("access_token") or data.get("token")
                    self._token_expire = time.time() + 3600  # 1 hour
                    return True
        except Exception:
            pass
        return False

    async def test_connection(self) -> Dict[str, Any]:
        """تست اتصال به پنل"""
        start = time.time()
        try:
            ok = await self.authenticate()
            latency = int((time.time() - start) * 1000)
            if ok:
                return {"success": True, "latency": latency}
            return {"success": False, "error": "Authentication failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========== Admin Management ==========

    async def get_admins(self) -> Dict[str, Any]:
        """دریافت لیست ادمین‌ها از پنل"""
        if not self._token:
            await self.authenticate()
        return await self._request("GET", "/admins")

    async def get_admin(self, admin_id: int) -> Dict[str, Any]:
        """دریافت اطلاعات یک ادمین"""
        if not self._token:
            await self.authenticate()
        return await self._request("GET", f"/admins/{admin_id}")

    async def create_admin(self, admin_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ساخت ادمین جدید در پنل
        
        admin_data = {
            "username": "admin_name",
            "password": "admin_pass",
            "email": "admin@example.com",
            "role": "admin",  # admin, reseller
            "maxClients": 100,
            "maxTraffic": 100,  # GB
            "expireAt": "2025-12-31",
            "isActive": True,
        }
        """
        if not self._token:
            await self.authenticate()
        return await self._request("POST", "/admins", admin_data)

    async def update_admin(self, admin_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """بروزرسانی ادمین"""
        if not self._token:
            await self.authenticate()
        return await self._request("PUT", f"/admins/{admin_id}", data)

    async def delete_admin(self, admin_id: int) -> bool:
        """حذف ادمین"""
        if not self._token:
            await self.authenticate()
        result = await self._request("DELETE", f"/admins/{admin_id}")
        return result.get("success", False)

    # ========== Client (User) Management ==========

    async def get_clients(self, panel_id: Optional[int] = None) -> Dict[str, Any]:
        """دریافت لیست کاربران (کلاینت‌ها)"""
        if not self._token:
            await self.authenticate()
        path = "/clients"
        if panel_id:
            path += f"?panelId={panel_id}"
        return await self._request("GET", path)

    async def get_client(self, client_id: str) -> Dict[str, Any]:
        """دریافت اطلاعات یک کاربر"""
        if not self._token:
            await self.authenticate()
        return await self._request("GET", f"/clients/{client_id}")

    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ساخت کاربر جدید (کلاینت)
        
        client_data = {
            "inboundId": 1,
            "username": "user_name",
            "traffic": 50,  # GB
            "expire": "2025-12-31",
            "maxConnections": 2,
            "enable": True,
        }
        """
        if not self._token:
            await self.authenticate()
        return await self._request("POST", "/clients", client_data)

    async def update_client(self, client_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """بروزرسانی کاربر"""
        if not self._token:
            await self.authenticate()
        return await self._request("PUT", f"/clients/{client_id}", data)

    async def delete_client(self, client_id: str) -> bool:
        """حذف کاربر"""
        if not self._token:
            await self.authenticate()
        result = await self._request("DELETE", f"/clients/{client_id}")
        return result.get("success", False)

    async def reset_client_traffic(self, client_id: str) -> Dict[str, Any]:
        """ریست ترافیک کاربر"""
        if not self._token:
            await self.authenticate()
        return await self._request("POST", f"/clients/{client_id}/reset-traffic")

    async def get_client_subscription(self, client_id: str) -> str:
        """دریافت لینک سابسکریپشن کاربر"""
        if not self._token:
            await self.authenticate()
        result = await self._request("GET", f"/clients/{client_id}/subscription")
        return result.get("subscriptionLink", "")

    # ========== Panel Management ==========

    async def get_panels(self) -> Dict[str, Any]:
        """دریافت لیست پنل‌های 3x-ui متصل"""
        if not self._token:
            await self.authenticate()
        return await self._request("GET", "/panels")

    async def get_panel(self, panel_id: int) -> Dict[str, Any]:
        """دریافت اطلاعات یک پنل"""
        if not self._token:
            await self.authenticate()
        return await self._request("GET", f"/panels/{panel_id}")

    async def sync_panel(self, panel_id: int) -> Dict[str, Any]:
        """همگام‌سازی پنل"""
        if not self._token:
            await self.authenticate()
        return await self._request("POST", f"/panels/{panel_id}/sync")

    # ========== Inbound Management ==========

    async def get_inbounds(self, panel_id: Optional[int] = None) -> Dict[str, Any]:
        """دریافت لیست اینباندها"""
        if not self._token:
            await self.authenticate()
        path = "/inbounds"
        if panel_id:
            path += f"?panelId={panel_id}"
        return await self._request("GET", path)

    async def create_inbound(self, panel_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """ساخت اینباند جدید"""
        if not self._token:
            await self.authenticate()
        return await self._request("POST", f"/panels/{panel_id}/inbounds", data)

    # ========== System Stats ==========

    async def get_system_stats(self) -> Dict[str, Any]:
        """دریافت آمار کلی سیستم"""
        if not self._token:
            await self.authenticate()
        return await self._request("GET", "/system")

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """دریافت آمار داشبورد"""
        if not self._token:
            await self.authenticate()
        return await self._request("GET", "/system/dashboard")

    async def get_panel_status(self) -> Dict[str, Any]:
        """دریافت وضعیت پنل‌ها"""
        if not self._token:
            await self.authenticate()
        return await self._request("GET", "/system/panel-status")

    # ========== Bulk Operations ==========

    async def bulk_delete_clients(self, client_ids: List[str]) -> Dict[str, Any]:
        """حذف گروهی کاربران"""
        if not self._token:
            await self.authenticate()
        return await self._request("POST", "/clients/bulk-delete", {"ids": client_ids})

    async def bulk_create_clients(self, clients: List[Dict]) -> Dict[str, Any]:
        """ساخت گروهی کاربران"""
        if not self._token:
            await self.authenticate()
        return await self._request("POST", "/clients/bulk-create", {"clients": clients})


def get_hm_panel_bridge(panel) -> HMPanelBridge:
    """ایجاد bridge برای HM Panel"""
    return HMPanelBridge(panel)
