"""Reproducible synthetic boundary probes for the relocation-aware crosswalk."""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
from test_ps2_irx_crosswalk import relocatable_module
from test_ps2_irx_relocations import build_irx
import ps2_irx
import ps2_irx_crosswalk as crosswalk


def outcome(label, inputs, base=0x1000):
    try:
        value = crosswalk.crosswalk(inputs, synthetic_load_base=base)
        edge_candidates = [candidate for edge in value["edges"] for candidate in edge["candidates"]]
        return {"case": label, "status": "accepted", "export_entries": value["export_entries"],
                "candidate_targets": [item["relative_target"] for item in edge_candidates]}
    except Exception as exc:
        return {"case": label, "status": "rejected",
                "error": f"{type(exc).__name__}: {exc}"}


valid_provider = relocatable_module(pointer_relocations=(20, 24), tail_target=0x80)
valid_consumer = relocatable_module(importing=True)
true_terminator = relocatable_module(pointer_relocations=(), tail_target=0x80)
partial_relocation = relocatable_module(pointer_relocations=(20,), tail_target=0x80)
wrapped_pointer = relocatable_module(pointer_relocations=(20, 24), tail_target=0xFFFFF000)

words = [0] * 64
words[0] = 0xDEAD0000
words[1] = ps2_irx.EXPORT_MAGIC
words[2] = 0
words[3] = 0x101
words[4] = int.from_bytes(b"demo\0\0\0\0"[:4], "little")
words[5] = 0
words[6] = 0
words[7] = 0x80
words[8] = 0
non_r32 = build_irx(words=tuple(words), text_relocations=((0, 5), (24, 6), (28, 2)),
                     bss_relocations=(), module_text=0x100, module_bss=0,
                     load_memory_size=0x100, module_id=8, module_gp=0x20)

import_template = relocatable_module(importing=True)
text_meta = ps2_irx.parse_irx(import_template)["text"]
text_bytes = import_template[text_meta["offset"]:text_meta["offset"] + text_meta["size"]]
import_words = struct.unpack("<64I", text_bytes)
relocated_import_stub = build_irx(words=import_words, text_relocations=((20, 2),),
                                   bss_relocations=(), module_text=0x100,
                                   module_bss=0, load_memory_size=0x100,
                                   module_id=8, module_gp=0x20)

cases = [
    outcome("R32_zero_pointer_is_candidate", [("consumer", valid_consumer), ("provider", valid_provider)]),
    outcome("genuine_zero_terminator_ends_table", [("provider", true_terminator)]),
    outcome("unrelocated_pointer_after_relocated_zero_is_rejected",
            [("provider", partial_relocation)]),
    outcome("non_R32_LO16_export_pointer_is_rejected", [("provider", non_r32)]),
    outcome("wrapped_pointer_cannot_become_false_terminator", [("provider", wrapped_pointer)]),
    outcome("relocated_import_stub_is_rejected", [("consumer", relocated_import_stub)]),
]
print(json.dumps(cases, indent=2))
