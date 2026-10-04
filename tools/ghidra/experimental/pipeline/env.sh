# Sourced by the drivers. Resolves the repository root from this file's location, never from a fixed path.
# Required environment: JAVA_HOME (JDK for Ghidra) and GHIDRA_HEADLESS (path to support/analyzeHeadless).
# Optional: PYTHON (default python3), FR2_WORK (ignored scratch output dir; default below).
PIPE=${${(%):-%x}:A:h}
ROOT=$(git -C "$PIPE" rev-parse --show-toplevel) || { echo "cannot resolve repository root" >&2; exit 2; }
cd "$ROOT"
: "${JAVA_HOME:?set JAVA_HOME to a JDK for Ghidra}"
: "${GHIDRA_HEADLESS:?set GHIDRA_HEADLESS to Ghidra's support/analyzeHeadless}"
PYTHON=${PYTHON:-python3}
export JAVA_HOME FR2_WORK=${FR2_WORK:-.scratch/mesh/codex-audit/frontier-3845-01}
case $FR2_WORK in /*) echo "FR2_WORK must be relative to the repository root, got $FR2_WORK" >&2; exit 2;; esac
D=$FR2_WORK
# Sorted "sha256  relative/path" records for every file under a project directory; paths are part of the record.
tree_sha() { (cd "$1" && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256); }
