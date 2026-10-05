# Headless, focus-free execution is permitted as a behavioral oracle

The project's hard rule was static and offline only — never run the game, guest code, an emulator or a debugger. The owner has now authorized running the game provided it is **completely headless and never takes input focus** from the machine.

Decided: execution is permitted as a **behavioral oracle** under two constraints — headless (no window, no display, no audio) and no focus theft — and it is **never a source of static evidence**. The matching target stays checkable without it; the oracle only validates behavior (e.g. a rebuilt function run headless against a known input). The earlier static-only rule is superseded for this purpose; it still governs all evidence that feeds the coverage ledger and byte accounting.
