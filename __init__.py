# SPDX-License-Identifier: MIT
# Copyright (c) 2026 solarL
"""ComfyUI audio/video tools by solarL."""

import importlib.util
import sys
from pathlib import Path

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

for folder in sorted(Path(__file__).parent.iterdir()):
    entry = folder / "__init__.py"
    if not folder.is_dir() or not folder.name.endswith("-solarL"):
        continue
    if not entry.is_file():
        continue
    module_name = f"{__name__}.{folder.name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(
        module_name, entry, submodule_search_locations=[str(folder)]
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
