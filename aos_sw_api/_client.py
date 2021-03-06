from typing import Union

import httpx

from aos_sw_api.auth import Auth
from aos_sw_api.authentication import Authentication
from aos_sw_api.cmd import CliCommand
from aos_sw_api.dot1x import Dot1x
from aos_sw_api.ip_address_subnet import IpAddressSubnet
from aos_sw_api.mac_authentication import MacAuthentication
from aos_sw_api.mac_table import MacTable
from aos_sw_api.poe import Poe
from aos_sw_api.port import Port
from aos_sw_api.radius_server import RadiusServer
from aos_sw_api.snmp_server import SnmpServer
from aos_sw_api.snmpv3 import SnmpV3
from aos_sw_api.sntp import Sntp
from aos_sw_api.sntp_server_details import SntpServerDetails
from aos_sw_api.stp import SpanningTree
from aos_sw_api.syslog import Syslog
from aos_sw_api.system import System
from aos_sw_api.tacacs_profile import TacacsProfile
from aos_sw_api.transceivers import Transceiver
from aos_sw_api.vlan import Vlan
from aos_sw_api.vlan_port import VlanPort


class BaseClient:

    def __init__(self,
                 switch_ip: str,
                 api_version: int,
                 sync: bool,
                 username: str,
                 password: str,
                 https: bool,
                 auto_logout: bool,
                 cookie: Union[str, None],
                 cert_path: Union[str, bool]):

        self._auto_logout = auto_logout
        self.cookie = cookie

        if https:
            base_url = f"https://{switch_ip}/rest/v{api_version}/"
        else:
            base_url = f"http://{switch_ip}/rest/v{api_version}/"
        client_settings = dict(base_url=base_url, verify=cert_path)

        if sync:
            self._session = httpx.Client(**client_settings)
        else:
            self._session = httpx.AsyncClient(**client_settings)

        # ArubaOS-Switch REST api does not support keep-alive
        # Disable http keep-alive
        self._session.headers["Connection"] = "close"

        self.auth = Auth(session=self._session, username=username, password=password)
        self.authentication = Authentication(session=self._session)
        self.dot1x = Dot1x(session=self._session)
        self.ip_address_subnet = IpAddressSubnet(session=self._session)
        self.mac_authentication = MacAuthentication(session=self._session)
        self.poe = Poe(session=self._session)
        self.port = Port(session=self._session)
        self.radius_server = RadiusServer(session=self._session)
        self.snmp_server = SnmpServer(session=self._session)
        self.snmpv3 = SnmpV3(session=self._session)
        self.sntp = Sntp(session=self._session)
        self.sntp_server_details = SntpServerDetails(session=self._session)
        self.stp = SpanningTree(session=self._session)
        self.syslog = Syslog(session=self._session)
        self.system = System(session=self._session)
        self.tacacs_profile = TacacsProfile(session=self._session)
        self.vlan = Vlan(session=self._session)
        self.vlan_port = VlanPort(session=self._session)
        self.transceivers = Transceiver(session=self._session)
        self.mac_table = MacTable(session=self._session)
        self.cmd = CliCommand(session=self._session)


class Client(BaseClient):

    def __init__(self,
                 switch_ip: str,
                 api_version: int,
                 username: str,
                 password: str,
                 https: bool = True,
                 auto_logout: bool = True,
                 cookie: str = None,
                 cert_path: Union[str, bool] = False):
        super().__init__(switch_ip=switch_ip,
                         api_version=api_version,
                         sync=True,
                         username=username,
                         password=password,
                         https=https,
                         auto_logout=auto_logout,
                         cookie=cookie,
                         cert_path=cert_path)

    def __enter__(self):
        self.auth.login(cookie=self.cookie)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session: httpx.Client
        if self._auto_logout:
            self.auth.logout()
        self._session.close()

    def close_session(self):
        self._session: httpx.Client
        self._session.close()


class AsyncClient(BaseClient):

    def __init__(self,
                 switch_ip: str,
                 api_version: int,
                 username: str,
                 password: str,
                 https: bool = True,
                 auto_logout: bool = True,
                 cookie: str = None,
                 cert_path: Union[str, bool] = False):
        super().__init__(switch_ip=switch_ip,
                         api_version=api_version,
                         sync=False,
                         username=username,
                         password=password,
                         https=https,
                         auto_logout=auto_logout,
                         cookie=cookie,
                         cert_path=cert_path)

    async def __aenter__(self):
        await self.auth.login(cookie=self.cookie)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._auto_logout:
            await self.auth.logout()
        await self._session.aclose()

    async def close_session(self):
        await self._session.aclose()
