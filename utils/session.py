import functools
import ujson
import asyncio
import aiohttp
from pydantic import BaseModel
from aiohttp import client_exceptions
from tenacity import retry, stop_after_attempt, wait_fixed, RetryCallState, _utils
from enum import Enum
from types import TracebackType
from typing import Any, Optional, Type, TypeVar
from .helper import Error_Message
from .logger import Logger

T = TypeVar("T")

log = Logger("NET").logger


def retry_log(retry_state: "RetryCallState"):
    if retry_state.attempt_number > 1:
        fn_name = _utils.get_callback_name(retry_state.fn)
        log.debug(fn_name + " 重试次数: %s" % retry_state.attempt_number)


class HTTPMethod(Enum):
    OPTIONS = "OPTIONS"
    GET = "GET"
    POST = "POST"


class HTTPSession:
    def __init__(self, headers=None):
        self.headers = headers
        self._session = None

    async def _create(self) -> aiohttp.ClientSession:
        """创建aiohttp客户端会话"""
        return aiohttp.ClientSession(
            headers=self.headers,
            connector=aiohttp.TCPConnector(ssl=False),
            json_serialize=ujson.dumps,
            timeout=aiohttp.ClientTimeout(total=5 * 60 * 60),
        )

    async def __aenter__(self) -> aiohttp.ClientSession:
        self._session = await self._create()
        return await self._session.__aenter__()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self._session.close()

    @staticmethod
    def Session(f):
        @functools.wraps(f)
        async def wrapper(
            self,
            *args: Any,
            session: Optional[aiohttp.ClientSession] = None,
            **kwargs: Any,
        ) -> T:
            if session is None:
                async with self._session as session:
                    return await f(self, *args, session=session, **kwargs)
            return await f(self, *args, session=session, **kwargs)

        return wrapper


class RespondBase(BaseModel):
    data: dict | list | bytes = None
    status: int = 0
    headers: dict = None

    class Config:
        arbitrary_types_allowed = "allow"


class RespondJson(RespondBase): ...


class RespondRawData(RespondBase): ...


class HTTPSessionApi:
    request_headers: dict = None

    def __init__(self, host: str, proxy: str = ""):
        self.host = host
        self.proxy = proxy
        self._session = HTTPSession()

    async def close_session(self):
        """关闭客户端会话"""
        await self._session._session.close()

    @retry(
        stop=stop_after_attempt(5), wait=wait_fixed(1), before=retry_log, reraise=True
    )
    async def request_json(
        self, path: str, method: HTTPMethod = None, **kwargs
    ) -> RespondJson:
        if method is None:
            method = HTTPMethod.GET
        return await self.__request__(method, path, **kwargs)
    
    @retry(
        stop=stop_after_attempt(5), wait=wait_fixed(1), before=retry_log, reraise=True
    )
    async def request_raw_data(
        self,
        path: str,
        method: HTTPMethod = None,
        chunk_handler: Optional[callable] = None,
        chunk_size: int = 1024,
        **kwargs,
    ) -> RespondRawData:
        if method is None:
            method = HTTPMethod.GET

        return await self.__request__(
            method,
            path,
            res_json=False,
            res_raw_data=True,
            chunk_handler=chunk_handler,
            chunk_size=chunk_size,
            **kwargs,
        )

    @HTTPSession.Session
    async def __request__(
        self,
        method: HTTPMethod,
        path: str,
        res_json: bool = True,
        res_raw_data: bool = False,
        *,
        host: Optional[str] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        raise_error: bool = True,
        chunk_handler: Optional[callable] = None,
        chunk_size: int = 1024,
        session: aiohttp.ClientSession,
    ) -> RespondBase:
        """发起HTTP请求并获取数据"""
        host = host or self.host
        
        if not path.startswith("http"):
            request_url = host + path
        else:
            request_url = path
        
        try:
            headers = headers or {}
            headers.update(self.request_headers or {})
            if json is not None:
                headers["Content-Type"] = "application/json"

            if not res_json and not res_raw_data:
                raise ValueError("请指定返回数据类型")

            async with session.request(
                method.value if method != HTTPMethod.OPTIONS else "GET",
                request_url,
                headers=headers,
                json=json,
                proxy=self.proxy,
            ) as resp:
                if method == HTTPMethod.OPTIONS:
                    return RespondRawData(
                        data={}, status=resp.status, headers=resp.headers
                    )
                if resp.status == 401:
                    raise Error_Message("access token 验证失败")

                if resp.status != 200:
                    return RespondBase(status=resp.status)

                if res_json:
                    data = await resp.json()
                    return RespondJson(
                        data=data, status=resp.status, headers=resp.headers
                    )
                elif res_raw_data:
                    data = None
                    if chunk_handler is not None:
                        data = b""
                        async for chunk in resp.content.iter_chunked(chunk_size):
                            chunk_handler(chunk)
                            data += chunk
                    else:
                        data = await resp.read()
                    return RespondRawData(
                        data=data, status=resp.status, headers=resp.headers
                    )

        except client_exceptions.InvalidURL:
            err_msg = f"错误的服务器地址 ({self.host})"
            self._handle_error(err_msg, raise_error)
        except client_exceptions.ClientConnectorError:
            err_msg = f"无法连接服务器地址 ({self.host})"
            self._handle_error(err_msg, raise_error)
        except asyncio.TimeoutError:
            err_msg = f"连接服务器超时 ({self.host})"
            self._handle_error(err_msg, raise_error)

    def _handle_error(self, message: str, raise_error: bool):
        """处理错误日志记录"""
        if raise_error:
            raise Error_Message(message)
        log.warning(message)
