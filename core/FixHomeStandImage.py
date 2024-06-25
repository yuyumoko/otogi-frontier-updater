from pathlib import Path

from PIL import Image

from lib.flowery.flowery import Imager

from core.DataServer.GitHubServer import GitHubServer


class FixHomeStandImage:
    root_path: Path
    char_id: str
    request: GitHubServer
    homestand_fix = None
    homestand_name = None
    homestand_no_fix = [21971, 22161]

    def __init__(self, root_path: Path, char_id):
        self.root_path = root_path
        self.char_id = str(char_id)
        self.request = GitHubServer()

    async def init(self):
        if self.homestand_fix is not None:
            return

        self.homestand_fix = await self.request.getHomestandFix()
        self.homestand_name = await self.request.getHomestandFixName()

    async def fix(self):
        await self.init()
        
        pos = self.homestand_fix.get(self.char_id)
        
        if pos is None:
            return

        chara_path = self.root_path / self.char_id
        if not chara_path.exists():
            return

        base_im = Image.open(chara_path / "idle.png")

        for name in self.homestand_name:
            im_path = chara_path / f"{name}.png"
            if not im_path.exists():
                continue

            body_im = Image.open(chara_path / "body.png")
            overlay = Image.open(im_path)

            if body_im.size == overlay.size:
                continue

            if self.char_id in ["21491"]:
                base_x = base_im.size[0] - overlay.size[0]
                base_y = base_im.size[1] - overlay.size[1]
                x = pos["x"] + base_x
                y = pos["y"] + base_y
            else:
                x = pos["x"]
                y = pos["y"]

            ima = Imager(Image.new("RGBA", body_im.size, (0, 0, 0, 0)))
            overlay_ima = Imager(overlay)
            await ima.paste(overlay_ima, (x, y))
            await ima.save(im_path)
