import base64
from io import BytesIO
from pathlib import Path
from typing import Any, Literal

from PIL import Image as PILImg
from PIL import ImageOps as PILOps
from typing_extensions import Self

from .typing import PILImage, T_Anchor, T_Color, T_Format, T_Mode, T_Resample
from .utils import awaitable


class Imager:
    """图像处理器"""

    __slots__ = "_image"

    def __init__(self, image: Self | PILImage) -> None:
        self._image = image.image.copy() if isinstance(image, Imager) else image

    def __getattr__(self, name: str) -> Any:
        return getattr(self.image, name)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.image.__exit__(exc_type, exc_value, traceback)

    def __repr__(self) -> str:
        return f"Imager(id={id(self)} mode={self.mode} size={self.width}*{self.height})"

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def image(self) -> PILImage:
        """PIL 图像对象"""
        return self._image

    @image.setter
    def image(self, image: PILImage) -> None:
        self._image = image

    @property
    def width(self) -> int:
        """图像宽度, 单位: 像素"""
        return self.size[0]

    @property
    def height(self) -> int:
        """图像高度, 单位: 像素"""
        return self.size[1]

    @property
    def size(self) -> tuple[int, int]:
        """图像尺寸"""
        return self.image.size

    @property
    def mode(self) -> T_Mode:
        """图像模式"""
        return self.image.mode  # type: ignore

    def _calculate_position(
        self, size: tuple[int, int], pos: tuple[int, int], anchor: T_Anchor
    ) -> tuple[int, int]:
        x, y = pos
        size_x, size_y = size
        if "b" in anchor:
            y = y - size_y
        if "r" in anchor:
            x = x - size_x
        if anchor[0] == "m":
            x = x - int(0.5 * size_x)
        if anchor[-1] == "m":
            y = y - int(0.5 * size_y)
        return x, y

    def convert(self, mode: T_Mode) -> Self:
        """转换图像模式

        ### 参数
            mode: 图像模式。
        """
        self.image = self.image.convert(mode)
        return self

    @awaitable
    def paste(
        self,
        img: Self,
        pos: tuple[int, int] = (0, 0),
        anchor: T_Anchor = "lt",
        reverse: bool = False,
    ) -> Self:
        """粘贴图像

        ### 说明
            支持透明图像。

        ### 参数
            img: 粘贴图像。
            pos: 锚点坐标。
            anchor: 锚点位置, 默认左上角-lt, x 轴: (l: 左, m: 中, r: 右), y 轴: (t: 上, m: 中, b: 下)。
            reverse: 是否反转图层顺序。
        """
        pos = self._calculate_position(img.size, pos, anchor)

        if not (self.has_transparency(img) or self.has_transparency(self)):
            if reverse:
                return self
            self.image.paste(img.image, pos)
            return self

        if self.image.mode != "RGBA":
            self.image = self.image.convert("RGBA")

        layer = PILImg.new("RGBA", self.image.size)
        layer.paste(img.image, pos)

        if reverse:
            self.image, layer = layer, self.image

        self.image = PILImg.alpha_composite(self.image, layer)

        return self

    @awaitable
    def apply_mask(self, mask: Self) -> Self:
        """将蒙版应用于图像

        ### 说明
            蒙版图像应与原始图像的大小相匹配。

        ### 参数
            mask: 蒙版图像。
        """
        self.image.putalpha(mask.image.convert("L"))
        return self

    @awaitable
    def invert(self) -> Self:
        """反色图像"""
        if self.mode == "RGBA":
            self.convert("RGB")
        self.image = PILOps.invert(self.image)
        return self

    @awaitable
    def grayscale(self) -> Self:
        """灰度图像"""
        self.image = PILOps.grayscale(self.image)
        return self

    @awaitable
    def rotate(
        self,
        angle: float,
        resample: T_Resample = PILImg.BICUBIC,
        expand: bool = False,
        center: tuple[float, float] | None = None,
        translate: tuple[float, float] | None = None,
        fillcolor: T_Color | None = None,
    ) -> Self:
        """
        旋转图像

        ### 参数
            angle: 旋转角度，以度为单位，逆时针方向。
            resample: 重采样过滤器。
            expand: 是否扩展图像边界, 使其足够大以容纳整个旋转的图像。
            center: 旋转中心点。原点是左上角。默认是图像的中心。
            translate: 旋转后偏移量。
            fillcolor: 旋转图像外部区域的背景色。
        """
        self.image = self.image.rotate(
            angle,
            resample,
            expand,
            center=center,
            translate=translate,
            fillcolor=fillcolor,
        )
        return self

    @awaitable
    def flip(self, axis: Literal["x", "y", "xy"]) -> Self:
        """
        翻转图像

        ### 参数
            axis: 翻转轴，沿指定轴镜像翻转180°。
        """

        if axis == "x":
            self.image = self.image.transpose(PILImg.FLIP_TOP_BOTTOM)
        elif axis == "y":
            self.image = self.image.transpose(PILImg.FLIP_LEFT_RIGHT)
        elif axis == "xy":
            self.image = self.image.rotate(180)

        return self

    @awaitable
    def opacity(self, alpha: int | float) -> Self:
        """调整图像不透明度"""
        if isinstance(alpha, float):
            if alpha < 0 or alpha > 1:
                raise ValueError("不透明度百分比必须在0到1之间")
            alpha = int(alpha * 255)
        elif isinstance(alpha, int):
            if alpha < 0 or alpha > 255:
                raise ValueError("不透明度值必须在0到255之间")
        else:
            raise TypeError("不透明度必须是整数或小数")

        self.image.putalpha(alpha)
        return self

    @awaitable
    def copy(self) -> Self:
        """复制图像"""
        return self.__class__(self)

    @awaitable
    def show(self, title: str | None = None) -> None:
        """显示图像"""
        self.image.show(title)

    @awaitable
    def save(self, fp: str | bytes | Path, **kwargs) -> None:
        """保存图像"""
        self.image.save(fp, **kwargs)

    def to_bytes(self) -> bytes:
        """转换图像为 bytes"""
        return self.image.tobytes()

    def to_base64(self, format: T_Format = "jpeg", **kwargs) -> str:
        """转换图像为 base64 字符串"""
        self.image.save(buf := BytesIO(), format, **kwargs)
        return base64.b64encode(buf.getvalue()).decode()

    def to_data_url(self, format: T_Format = "jpeg", **kwargs) -> str:
        """转换图像为 data url"""
        return f"data:image/{format};base64,{self.to_base64(format, **kwargs)}"

    @classmethod
    def open(
        cls,
        file: str | Path | bytes | BytesIO,
        formats: list[T_Format] | tuple[T_Format, ...] | None = None,
    ) -> Self:
        """打开指定的图像"""
        return cls(PILImg.open(file, "r", formats))  # type: ignore

    @classmethod
    def new(
        cls, mode: T_Mode, size: int | tuple[int, int], color: T_Color | None = None
    ) -> Self:
        """创建一个具有给定模式和大小的新图像"""
        if isinstance(size, int):
            size = (size, size)
        return cls(PILImg.new(mode, size, color or 0))

    @classmethod
    def has_transparency(cls, image: Self) -> bool:
        """检查图像是否具有透明度"""
        if image.mode == "P":
            transparent = image.info.get("transparency", -1)
            if colors := image.getcolors():
                for _, index in colors:
                    if index == transparent:
                        return True
        elif image.mode == "RGBA":
            extrema = image.getextrema()
            if extrema[3][0] < 255:
                return True

        return False
