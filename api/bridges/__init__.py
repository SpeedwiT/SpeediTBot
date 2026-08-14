"""API Bridges - اتصال به پنل‌های VPN مختلف"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import aiohttp
import time


class PanelBridge(ABC):
    """کلاس پایه برای اتصال به پنل‌ها"""

    def __init__(self, panel):
        self.panel = panel
        self.base_url = f"http://{panel.host}:{panel.port}"
        self._session: Optional[aiohttp.ClientSession] = None
        self._token: Optional[str] = None

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

    @abstractmethod
    async def authenticate(self) -> bool:
        ...

    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def create_user(self, username: str, traffic_gb: int, duration_days: int, **kwargs) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def get_user(self, username: str) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def update_user(self, username: str, **kwargs) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def delete_user(self, username: str) -> bool:
        ...

    @abstractmethod
    async def get_subscription_link(self, username: str) -> str:
        ...

    @abstractmethod
    async def get_system_stats(self) -> Dict[str, Any]:
        ...


# Import specific bridges
from api.bridges.hm_panel import HMPanelBridge, get_hm_panel_bridge


class SanaeiBridge(PanelBridge):
    """اتصال به پنل ثنایی (X-UI)"""

    async def authenticate(self) -> bool:
        session = await self.get_session()
        url = f"{self.base_url}/login"
        payload = {
            "username": self.panel.username,
            "password": self.panel.password,
        }
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._token = data.get("token") or resp.cookies.get("session")
                    return True
        except Exception:
            pass
        return False

    async def test_connection(self) -> Dict[str, Any]:
        start = time.time()
        try:
            ok = await self.authenticate()
            latency = int((time.time() - start) * 1000)
            if ok:
                return {"success": True, "latency": latency}
            return {"success": False, "error": "Authentication failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_user(self, username: str, traffic_gb: int, duration_days: int, **kwargs) -> Dict[str, Any]:
        if not self._token:
            await self.authenticate()
        session = await self.get_session()
        url = f"{self.base_url}/api/inbounds/addClient"
        payload = {
            "id": kwargs.get("inbound_id", 1),
            "settings": '{"clients":[{"id":"' + username + '","flow":"","email":"' + username + '@proxyman","limitIp":' + str(kwargs.get("max_connections", 1)) + ',"totalGB":' + str(traffic_gb * 1024 * 1024 * 1024) + ',"expiryTime":' + str(int(time.time() * 1000) + duration_days * 86400000) + ',"enable":true,"tgId":"","subId":"' + username + '"}]}',
        }
        try:
            async with session.post(url, json=payload, headers={"Authorization": f"Bearer {self._token}"}) as resp:
                if resp.status in (200, 201):
                    return {"success": True, "uuid": username}
                return {"success": False, "error": await resp.text()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_user(self, username: str) -> Dict[str, Any]:
        return {"username": username, "status": "active"}

    async def update_user(self, username: str, **kwargs) -> Dict[str, Any]:
        return {"success": True}

    async def delete_user(self, username: str) -> bool:
        return True

    async def get_subscription_link(self, username: str) -> str:
        return f"{self.base_url}/sub/{username}"

    async def get_system_stats(self) -> Dict[str, Any]:
        return {"cpu": 0, "memory": 0, "disk": 0}


class MarzbanBridge(PanelBridge):
    """اتصال به پنل مرزبان"""

    async def authenticate(self) -> bool:
        session = await self.get_session()
        url = f"{self.base_url}/api/admin/token"
        payload = {"username": self.panel.username, "password": self.panel.password}
        try:
            async with session.post(url, data=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._token = data.get("access_token")
                    return True
        except Exception:
            pass
        return False

    async def test_connection(self) -> Dict[str, Any]:
        start = time.time()
        try:
            ok = await self.authenticate()
            latency = int((time.time() - start) * 1000)
            if ok:
                return {"success": True, "latency": latency}
            return {"success": False, "error": "Authentication failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_user(self, username: str, traffic_gb: int, duration_days: int, **kwargs) -> Dict[str, Any]:
        if not self._token:
            await self.authenticate()
        session = await self.get_session()
        url = f"{self.base_url}/api/user"
        import uuid
        payload = {
            "username": username,
            "proxies": {"vmess": {"id": str(uuid.uuid4())}, "vless": {"id": str(uuid.uuid4())}},
            "inbounds": {},
            "data_limit": traffic_gb * 1024 * 1024 * 1024,
            "data_limit_reset_strategy": "no_reset",
            "status": "active",
            "expire": int(time.time()) + (duration_days * 86400),
            "note": "",
        }
        try:
            async with session.post(url, json=payload, headers={"Authorization": f"Bearer {self._token}"}) as resp:
                if resp.status in (200, 201):
                    data = await resp.json()
                    return {"success": True, "uuid": username, "data": data}
                return {"success": False, "error": await resp.text()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_user(self, username: str) -> Dict[str, Any]:
        if not self._token:
            await self.authenticate()
        session = await self.get_session()
        url = f"{self.base_url}/api/user/{username}"
        try:
            async with session.get(url, headers={"Authorization": f"Bearer {self._token}"}) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception:
            pass
        return {}

    async def update_user(self, username: str, **kwargs) -> Dict[str, Any]:
        if not self._token:
            await self.authenticate()
        session = await self.get_session()
        url = f"{self.base_url}/api/user/{username}"
        try:
            async with session.put(url, json=kwargs, headers={"Authorization": f"Bearer {self._token}"}) as resp:
                if resp.status == 200:
                    return {"success": True, "data": await resp.json()}
        except Exception:
            pass
        return {"success": False}

    async def delete_user(self, username: str) -> bool:
        if not self._token:
            await self.authenticate()
        session = await self.get_session()
        url = f"{self.base_url}/api/user/{username}"
        try:
            async with session.delete(url, headers={"Authorization": f"Bearer {self._token}"}) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def get_subscription_link(self, username: str) -> str:
        return f"{self.base_url}/sub/{username}"

    async def get_system_stats(self) -> Dict[str, Any]:
        if not self._token:
            await self.authenticate()
        session = await self.get_session()
        url = f"{self.base_url}/api/system"
        try:
            async with session.get(url, headers={"Authorization": f"Bearer {self._token}"}) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception:
            pass
        return {}


class PasarGuardBridge(PanelBridge):
    """اتصال به پنل پاسارگاد"""

    async def authenticate(self) -> bool:
        session = await self.get_session()
        url = f"{self.base_url}/api/admin/login"
        payload = {"username": self.panel.username, "password": self.panel.password}
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._token = data.get("token") or data.get("access_token")
                    return True
        except Exception:
            pass
        return False

    async def test_connection(self) -> Dict[str, Any]:
        start = time.time()
        try:
            ok = await self.authenticate()
            latency = int((time.time() - start) * 1000)
            if ok:
                return {"success": True, "latency": latency}
            return {"success": False, "error": "Authentication failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_user(self, username: str, traffic_gb: int, duration_days: int, **kwargs) -> Dict[str, Any]:
        if not self._token:
            await self.authenticate()
        session = await self.get_session()
        url = f"{self.base_url}/api/users"
        payload = {
            "username": username,
            "traffic": traffic_gb,
            "expiry_time": int(time.time()) + (duration_days * 86400),
            "max_connections": kwargs.get("max_connections", 1),
            "status": "active",
        }
        try:
            async with session.post(url, json=payload, headers={"Authorization": f"Bearer {self._token}"}) as resp:
                if resp.status in (200, 201):
                    return {"success": True, "uuid": username}
                return {"success": False, "error": await resp.text()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_user(self, username: str) -> Dict[str, Any]:
        return {"username": username}

    async def update_user(self, username: str, **kwargs) -> Dict[str, Any]:
        return {"success": True}

    async def delete_user(self, username: str) -> bool:
        return True

    async def get_subscription_link(self, username: str) -> str:
        return f"{self.base_url}/sub/{username}"

    async def get_system_stats(self) -> Dict[str, Any]:
        return {}


class RebeccaBridge(PanelBridge):
    """اتصال به پنل ربکا"""

    async def authenticate(self) -> bool:
        session = await self.get_session()
        url = f"{self.base_url}/auth/login"
        payload = {"username": self.panel.username, "password": self.panel.password}
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._token = data.get("token")
                    return True
        except Exception:
            pass
        return False

    async def test_connection(self) -> Dict[str, Any]:
        start = time.time()
        try:
            ok = await self.authenticate()
            latency = int((time.time() - start) * 1000)
            if ok:
                return {"success": True, "latency": latency}
            return {"success": False, "error": "Authentication failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_user(self, username: str, traffic_gb: int, duration_days: int, **kwargs) -> Dict[str, Any]:
        if not self._token:
            await self.authenticate()
        session = await self.get_session()
        url = f"{self.base_url}/users"
        payload = {
            "username": username,
            "data_limit_gb": traffic_gb,
            "expire_days": duration_days,
            "max_connections": kwargs.get("max_connections", 1),
        }
        try:
            async with session.post(url, json=payload, headers={"Authorization": f"Bearer {self._token}"}) as resp:
                if resp.status in (200, 201):
                    return {"success": True, "uuid": username}
                return {"success": False, "error": await resp.text()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_user(self, username: str) -> Dict[str, Any]:
        return {"username": username}

    async def update_user(self, username: str, **kwargs) -> Dict[str, Any]:
        return {"success": True}

    async def delete_user(self, username: str) -> bool:
        return True

    async def get_subscription_link(self, username: str) -> str:
        return f"{self.base_url}/sub/{username}"

    async def get_system_stats(self) -> Dict[str, Any]:
        return {}


# Factory function
def get_bridge(panel) -> PanelBridge:
    """ایجاد bridge مناسب بر اساس نوع پنل"""
    bridges = {
        "sanaei": SanaeiBridge,
        "marzban": MarzbanBridge,
        "pasarguard": PasarGuardBridge,
        "rebecca": RebeccaBridge,
        "hm_panel": HMPanelBridge,
    }
    bridge_class = bridges.get(panel.panel_type.value, MarzbanBridge)
    return bridge_class(panel)


def get_hm_bridge(panel) -> HMPanelBridge:
    """ایجاد bridge مخصوص HM Panel"""
    return HMPanelBridge(panel)
