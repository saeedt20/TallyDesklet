"""Register bundled OFL fonts in this process only."""
import ctypes
import ctypes.util
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"
if not DATA.is_dir():
    DATA = Path(__file__).resolve().parent.parent / "data"
_loaded = False


def load():
    global _loaded
    if _loaded:
        return
    _loaded = True
    try:
        library = ctypes.util.find_library("fontconfig")
        if not library:
            return
        fc = ctypes.CDLL(library)
        fc.FcConfigGetCurrent.restype = ctypes.c_void_p
        fc.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        fc.FcConfigAppFontAddFile.restype = ctypes.c_int
        config = fc.FcConfigGetCurrent()
        for path in (DATA / "fonts/vazirmatn").glob("*.ttf"):
            fc.FcConfigAppFontAddFile(config, str(path).encode())
        from gi.repository import PangoCairo
        PangoCairo.FontMap.get_default().changed()
    except (OSError, AttributeError, TypeError):
        pass
