from typing import Literal, TypeAlias

from PIL.Image import Image

PILImage: TypeAlias = Image
T_Anchor: TypeAlias = Literal["lt", "lm", "lb", "mt", "mm", "mb", "rt", "rm", "rb"]
T_Mode: TypeAlias = Literal[
    "1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "LAB", "HSV", "I", "F"
]
T_Pos: TypeAlias = tuple[int, int]
T_Format: TypeAlias = Literal["png", "jpg", "jpeg", "bmp", "tiff", "webp"]
T_Color: TypeAlias = (
    int
    | tuple[int]
    | tuple[int, int]
    | tuple[int, int, int]
    | tuple[int, int, int, int]
    | str
    | float
    | tuple[float]
)
T_Resample: TypeAlias = Literal[0, 1, 2, 3, 4, 5]
