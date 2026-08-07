import asyncio
import shutil
import socket
import subprocess
import time
from contextlib import closing

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

EXPECTED_TOOLS = {
    "init",
    "save-code",
    "check-syntax",
    "build-stl",
    "measure-stl",
    "render-images",
    "browse-library-catalog",
    "fetch-library",
    "read-library-source",
    "read-library-file",
    "list-reviewed-libraries",
    "submit-feedback",
    "list-feedback",
    "finalize",
}


def free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_port(port: int, timeout: float = 20.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise TimeoutError(f"gateway did not listen on port {port}")


async def list_tools(url: str) -> set[str]:
    async with streamable_http_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()
            return {tool.name for tool in result.tools}


def test_mature_upstream_is_exposed_unchanged_over_streamable_http(tmp_path):
    proxy = shutil.which("mcp-proxy")
    upstream = shutil.which("openscad-mcp-server")
    assert proxy, "mcp-proxy executable is required"
    assert upstream, "openscad-mcp-server executable is required"

    port = free_port()
    process = subprocess.Popen(
        [
            proxy,
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--",
            upstream,
        ],
        cwd=tmp_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        wait_for_port(port)
        tools = asyncio.run(list_tools(f"http://127.0.0.1:{port}/mcp"))
        assert tools == EXPECTED_TOOLS
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

        if process.returncode not in (0, -15):
            stdout, stderr = process.communicate()
            raise AssertionError(
                f"gateway exited unexpectedly ({process.returncode})\n"
                f"stdout:\n{stdout}\n"
                f"stderr:\n{stderr}"
            )
