import time
import asyncio
import ujson as json

from aiohttp import ClientSession, ClientTimeout


class GitHubFileFetcher:
    def __init__(self, repo, branch, auth_token, proxy=True):
        self.repo = repo
        self.branch = branch
        self.auth_token = auth_token
        self.proxy = proxy
        self.default_github_proxy = None

    async def get_github_file_url(self):
        base_url = f"https://raw.githubusercontent.com/"
        repo_path_format = f"{self.repo}/{self.branch}/"

        if not self.proxy:
            return base_url + repo_path_format

        if self.default_github_proxy is not None:
            proxy_url = self.default_github_proxy["proxy_url"].format(repo=self.repo, branch=self.branch)
            real_url = self.default_github_proxy["url"] + proxy_url
            return real_url

        github_prox_list = [
            # fmt: off
            {"name": "ghproxy", "url": "https://ghproxy.net/", "proxy_url": base_url + repo_path_format},
            {"name": "ghproxy_mirror", "url": "https://mirror.ghproxy.com/", "proxy_url": base_url + repo_path_format},
            {"name": "ixnic", "url": "https://fastraw.ixnic.net/", "proxy_url": repo_path_format},
            # fmt: on
        ]

        async def fetch_proxy_url(prox_info):
            start_time = time.time()
            async with ClientSession(timeout=ClientTimeout(total=5)) as session:
                try:
                    async with session.options(prox_info["url"]) as response:
                        return time.time() - start_time, prox_info
                except Exception as e:
                    return None

        tasks = [fetch_proxy_url(prox_info) for prox_info in github_prox_list]
        results = await asyncio.gather(*tasks)
        results = [result for result in results if result is not None]
        if len(results) == 0:
            raise Exception("No proxy server available")
        results.sort(key=lambda x: x[0])
        first_result = results[0][1]
        proxy_url = first_result["proxy_url"].format(repo=self.repo, branch=self.branch)
        real_url = first_result["url"] + proxy_url

        self.default_github_proxy = first_result

        return real_url

    async def fetch_json(self, file_name):
        return json.loads(await self.fetch_text(file_name))

    async def fetch_text(self, file_name):
        baseUrl = await self.get_github_file_url()

        url = baseUrl + file_name
        headers = {
            "Authorization": f"token {self.auth_token}",
        }

        async with ClientSession(timeout=ClientTimeout(total=2 * 60)) as session:
            async with session.request("GET", url, headers=headers) as response:
                if response.status != 200:
                    return None
                return await response.text()

    async def fetch_binary(self, file_name):
        baseUrl = await self.get_github_file_url()

        url = baseUrl + file_name
        headers = {
            "Authorization": f"token {self.auth_token}",
        }

        async with ClientSession(timeout=ClientTimeout(total=2 * 60)) as session:
            async with session.request("GET", url, headers=headers) as response:
                if response.status != 200:
                    return None
                return await response.read()


async def main():
    repo_path = ""
    repo_branch = ""
    auth_token = ""

    file_fetcher = GitHubFileFetcher(repo_path, repo_branch, auth_token)
    file_name = "VieableEpisodeList/19931"
    data = await file_fetcher.fetch_json(file_name)
    print(data)


if __name__ == "__main__":
    asyncio.run(main())
