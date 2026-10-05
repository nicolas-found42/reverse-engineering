# Repository licence and IP rails

"Completely open source" applies to the repository as well as the toolchain. Decided: the tooling and reconstruction source are **MIT licensed**, and the same rails `nathanialf/ico` uses are adopted — a `docs/LEGAL.md` stating what may and may not be tracked, a `.gitignore` shaped for the corpus, and a pre-commit hook that refuses to commit a PS2 boot ELF or any Sony-derived artifact. The game binary, raw dumps, generated C/assembly, and Sony SDK objects are **never committed**.

Considered and rejected: **GPL** (the toolchain `ee-gcc` is GPL, but the project's own source need not be copyleft, and matching-decomp peers are MIT); **no licence** (blocks reuse and contradicts "open source").
