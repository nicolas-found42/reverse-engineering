# compiler-profile-independent: pass



```json
{
  "profile_status": "pass",
  "selected_id": "ee-gcc2.96",
  "surviving_candidates": [
    "ee-gcc2.96"
  ],
  "unit_outcomes": [
    {
      "unit": "accessor",
      "matches": [
        "ee-gcc2.96"
      ]
    },
    {
      "unit": "misc3d_reset",
      "matches": [
        "ee-gcc2.9-991111-01",
        "ee-gcc2.96",
        "ee-gcc2.95.2-273a",
        "ee-gcc2.95.3-114",
        "ee-gcc2.95.3-136"
      ]
    },
    {
      "unit": "entity_set_first",
      "matches": [
        "ee-gcc2.96"
      ]
    },
    {
      "unit": "parser_lookup",
      "matches": [
        "ee-gcc2.96"
      ]
    }
  ],
  "operational_gaps": [],
  "matched_bytes": 0,
  "ac05_status": "incomplete",
  "ac05_reason": "The EE panel bounds a matching profile only. Source forms are inferred/explored, exact historical source/package binding remains #21, and relevant game-owned IOP probes are outside this panel.",
  "claim_limits": [
    "No original-source identity or full-image compiler claim.",
    "Pre-link diagnostics exclude relocation fields; exact linked comparisons retain them.",
    "GNU ld 2.40 placement is a substitution, whose full contract remains #9.",
    "No ownership change or additional matched-byte credit.",
    "A byte match establishes no package permission."
  ],
  "probes": [
    {
      "status": "pass",
      "selected_id": "ee-gcc2.96",
      "matches": [
        "ee-gcc2.96"
      ],
      "failures": [
        "ee-gcc2.9-991111-01",
        "ee-gcc3.2-030926",
        "ee-gcc3.2-040921",
        "ee-gcc2.95.2-273a",
        "ee-gcc2.95.3-114",
        "ee-gcc2.95.3-136"
      ],
      "errors": [],
      "incomplete": [],
      "manifest": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/manifest.json",
        "bytes": 27280,
        "sha256": "4b468883ddbbaf66f510f7cddc4958ab07c23fb2b63633440ad6e7af0774018e"
      },
      "evidence": {
        "corpus": {
          "profile": "fr2-pal-sles-517.05",
          "sources": {
            "ford-racing-2.bin": {
              "bytes": 678667248,
              "sha256": "ae8d5a32c9d832f34a08fad6f0e97ce6e89e6b040597011f6362d886145b9d3d"
            },
            "ford-racing-2.cue": {
              "bytes": 79,
              "sha256": "c2e0aaf75a43150567f4ffe02ac863c8d1bda8f2fdf744012361436ec582edb6"
            },
            "extracted/SLES_517.05": {
              "bytes": 1662804,
              "sha256": "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95"
            },
            "extracted/FILES.HDR": {
              "bytes": 29428,
              "sha256": "f4e4a4f91cd89bcaa8c2772e6cba2a839d92fbe222290c8c751777a81963731d"
            },
            "extracted/FILES.DAT": {
              "bytes": 334641152,
              "sha256": "357fc371f47e366bf507b721e26eed9f1205516c19b793e0316ccecc2175a722"
            }
          },
          "corpus_id": "e69a2afbd6db606d166e40bae32c436691e134722ad153200859961a5f517dab"
        },
        "reference_range": {
          "section": ".text",
          "vaddr": "001d1800",
          "file_offset": "000d2800",
          "bytes": 60,
          "sha256": "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e",
          "scope": "game_owned",
          "decision": "ADR-0005 local split, cross-checked against source map, callers, and helper provenance"
        },
        "candidate_source": "Hand-written exploratory reconstruction; inferred names, ABI and ownership; not original source.",
        "tool_source": "decompme/compilers release tag compilers; per-candidate archive URLs and SHA-256 values follow.",
        "tool_distributions": [
          {
            "candidate": "ee-gcc2.9-991111-01",
            "archive": "ee-gcc2.9-991111-01.tar.xz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.9-991111-01.tar.xz",
            "expected_sha256": "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8",
            "available_locally": true,
            "observed_sha256": "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8"
          },
          {
            "candidate": "ee-gcc2.95.2-273a",
            "archive": "ee-gcc2.95.2-273a.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.2-273a.tar.gz",
            "expected_sha256": "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e",
            "available_locally": true,
            "observed_sha256": "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e"
          },
          {
            "candidate": "ee-gcc2.95.3-114",
            "archive": "ee-gcc2.95.3-114.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.3-114.tar.gz",
            "expected_sha256": "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb",
            "available_locally": true,
            "observed_sha256": "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb"
          },
          {
            "candidate": "ee-gcc2.95.3-136",
            "archive": "ee-gcc2.95.3-136.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.3-136.tar.gz",
            "expected_sha256": "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f",
            "available_locally": true,
            "observed_sha256": "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f"
          },
          {
            "candidate": "ee-gcc2.96",
            "archive": "ee-gcc2.96.tar.xz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.96.tar.xz",
            "expected_sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a",
            "available_locally": true,
            "observed_sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a"
          },
          {
            "candidate": "ee-gcc3.2-030926",
            "archive": "ee-gcc3.2-030926.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-030926.tar.gz",
            "expected_sha256": "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9",
            "available_locally": true,
            "observed_sha256": "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9"
          },
          {
            "candidate": "ee-gcc3.2-040921",
            "archive": "ee-gcc3.2-040921.tar.xz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-040921.tar.xz",
            "expected_sha256": "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f",
            "available_locally": true,
            "observed_sha256": "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f"
          }
        ],
        "license_status": "The release archives inspected do not include COPYING or LICENSE entries. Per-package redistribution terms are unresolved; no compiler binaries are redistributed here.",
        "runtime_profile": "Immutable image IDs are verified before invocation: Debian Bookworm linux/amd64 with Wine 8 for Windows compiler drivers, and GNU binutils 2.40 in the Debian image for object preparation, linking, and objcopy.",
        "linker_profile": "GNU binutils 2.40 substitution; not the original proprietary linker."
      },
      "source": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.c",
        "bytes": 627,
        "sha256": "44b17bacf38c4a9befdb77dca2b137ac1e0826cb595ad7dd87c4775dfa5375bc"
      },
      "reference": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/reference.bin",
        "bytes": 60,
        "sha256": "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e"
      },
      "symbol": "fr2_misc3d_get_database_id",
      "candidates": [
        {
          "id": "ee-gcc2.9-991111-01",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/bin/ee-gcc",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-ud3sc5ht/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/lib/gcc-lib/ee/2.9-ee-991111-01/cc1",
              "bytes": 4794381,
              "sha256": "b9aef69f93efb949f15ea58189e8eef4a002b9fe4de5d3fcf89c34e1244ec026"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/lib/gcc-lib/ee/2.9-ee-991111-01/cpp",
              "bytes": 241396,
              "sha256": "f85a54d241e019993fa7a06285d3677856b3b431e10318a587ab029373c603d7"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/ee/bin/as",
              "bytes": 2210289,
              "sha256": "296af123052ee39d175e5b3254102aafca105d4f6e975b351a13867f59b04019"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "64d0a50fef499da0b98177eb5e79e41dfb066ad44246b137c78a266ef97ee265",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-ud3sc5ht/candidate.o",
              "bytes": 2000,
              "sha256": "e41e5dcf870ce3a5272e15bcc6d28575415f479345da3085fc1ab811d1c23af0"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-ud3sc5ht/prepared.o",
              "bytes": 1904,
              "sha256": "2d2574e362f777a4a8aef1956793e4351d58ec3ed69c041e0e269be6627c04ce"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-ud3sc5ht/linked.o",
              "bytes": 14696,
              "sha256": "6c698345eda219d0304b2a07eba970083c70cfed018a66e22afc0c18547a86f2"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-ud3sc5ht/function.bin",
              "bytes": 64,
              "sha256": "e54a7daa25ca8db663b12aa3bf17327ea0fe6b4b23838e71b867cb54383dfa60"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Using builtin specs.\ngcc version 2.9-ee-991111-01\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/cc1 /tools/compiler-profile-if5l6kuy/accessor/candidate.c -G8 -lang-c -iprefix /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/ -quiet -dumpbase candidate.c -undef -D__GNUC__=2 -D__GNUC_MINOR__=9 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float -version -ffunction-sections -O2 -o /tmp/cc4AI7sL.s\nGNU C version 2.9-ee-991111-01 (ee) compiled by GNU C version 2.7.2.3.\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/../../../../ee/bin/as -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-ud3sc5ht/candidate.o /tmp/cc4AI7sL.s\nGNU assembler version 2.9-ee-991111 (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "e41e5dcf870ce3a5272e15bcc6d28575415f479345da3085fc1ab811d1c23af0",
            "text_sha256": "e1ae6d9aa9ca50672ceb6ba4574ecd0a09b54a756599c9ebfabffcd94fb313a1",
            "text_bytes": 64,
            "relocations": [
              {
                "offset": 4,
                "type": 7,
                "symbol_index": 14,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 4,
                "mask": "0000ffff"
              },
              {
                "offset": 36,
                "type": 6,
                "symbol_index": 4,
                "mask": "0000ffff"
              },
              {
                "offset": 32,
                "type": 5,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 40,
                "type": 6,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 44,
                "type": 4,
                "symbol_index": 15,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 60,
              "reason": "function length differs",
              "expected_bytes": 60,
              "actual_bytes": 64
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-ud3sc5ht/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-ud3sc5ht/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-ud3sc5ht/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-ud3sc5ht/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-ud3sc5ht/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-ud3sc5ht/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "e54a7daa25ca8db663b12aa3bf17327ea0fe6b4b23838e71b867cb54383dfa60",
          "actual_bytes": 64,
          "reference_sha256": "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 60,
            "first_difference": {
              "offset": 0,
              "address": "001d1800",
              "file_offset": "000d2800",
              "word": 0,
              "expected": "54ad838f",
              "actual": "f0ffbd27"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.96",
          "status": "pass",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-bcqf_pwa/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/cc1",
              "bytes": 5526661,
              "sha256": "59ec92b3f9f3513e0633331af304733e3094de30884e662a8cb584a51c1c42b5"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/cpp0",
              "bytes": 421478,
              "sha256": "f6f6b598f39649edfe171d6da8c7f91d07f2b87c2aeeffffbc5f566bfb1a39a9"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/ee/bin/as",
              "bytes": 2169068,
              "sha256": "b8cfdb6ecb6931642914020f92a62e653378f57230eed4895f69afa050d47b5e"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "b8c284d16c9c0a0e8788e9522c46881e224ad01fa1c732aed43f821cc32f168b",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-bcqf_pwa/candidate.o",
              "bytes": 2144,
              "sha256": "227b580076f9c73ae53ea1d5d161f2913c02bec9b4c710bf99ab9a3a9e451bd9"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-bcqf_pwa/prepared.o",
              "bytes": 1968,
              "sha256": "6117a77019c88c34eb75aa18e12bf9a51ca40d034509996a2aca76ab22af7c8c"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-bcqf_pwa/linked.o",
              "bytes": 14696,
              "sha256": "d5b9edb85db09fee11a514551767d33874a23de997558bed8963e3e694b86d6d"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-bcqf_pwa/function.bin",
              "bytes": 60,
              "sha256": "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Using builtin specs.\ngcc version 2.96-ee-001003-1\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/ -D__GNUC__=2 -D__GNUC_MINOR__=96 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/accessor/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccoOEa0w.s\nGNU CPP version 2.96-ee-001003-1 (cpplib)\n [AL 1.1, MM 40] BSD Mips\nGNU C version 2.96-ee-001003-1 (ee) compiled by GNU C version 2.9-gnupro-99r1.\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/sys-include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/sys-include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/../../../../ee/bin/as -G8 -EL -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-bcqf_pwa/candidate.o /tmp/ccoOEa0w.s\nGNU assembler version 2.10-ee-001003-1 (ee) using BFD version 2.10-ee-001003\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "227b580076f9c73ae53ea1d5d161f2913c02bec9b4c710bf99ab9a3a9e451bd9",
            "text_sha256": "1ec038d0f5965ff1281e89a337f246aef193b21c62285fa51623746bf58934b2",
            "text_bytes": 60,
            "relocations": [
              {
                "offset": 0,
                "type": 7,
                "symbol_index": 15,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 5,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 32,
                "type": 6,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 6,
                "mask": "0000ffff"
              },
              {
                "offset": 36,
                "type": 6,
                "symbol_index": 6,
                "mask": "0000ffff"
              },
              {
                "offset": 40,
                "type": 4,
                "symbol_index": 16,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof."
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-bcqf_pwa/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-bcqf_pwa/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-bcqf_pwa/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-bcqf_pwa/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-bcqf_pwa/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-bcqf_pwa/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e",
          "actual_bytes": 60,
          "reference_sha256": "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "pass",
            "reason": null,
            "matched_bytes": 60,
            "section_bytes": 60
          }
        },
        {
          "id": "ee-gcc3.2-030926",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-pdcgf22b/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/cc1",
              "bytes": 9764536,
              "sha256": "da4fec4d48d91e62fd968f76acb16981dd8131d02f27c1b7559f0e903b590eb6"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/cpp0",
              "bytes": 703785,
              "sha256": "2d1a4b260e143a8b467bb7609cb3fd60ae541174ffff78d922feb2d7fbb0e218"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/ee/bin/as",
              "bytes": 5887159,
              "sha256": "d04424acb1359b31b3ad138f8d17876623ffe9182497ff4516055b71f22bf2fa"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "8ba17b0f2cbcc87b31bb164766bc3e7e340f714adfb518bc4634a6f1ffda8951",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-pdcgf22b/candidate.o",
              "bytes": 1860,
              "sha256": "7f1968d435d96069f07d8c6ba17b8fff5c01f3a398f7850829029b05d36697a3"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-pdcgf22b/prepared.o",
              "bytes": 1860,
              "sha256": "0e9c24584cef8752dfabece3105b83a97ffad1c6f7161c7e0ef171b6fd56eade"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-pdcgf22b/linked.o",
              "bytes": 14640,
              "sha256": "e7c8dd24beac65e44eb68fa19cb6fb70da797e3d6af15578b002ea9313ec888c"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-pdcgf22b/function.bin",
              "bytes": 64,
              "sha256": "2902d95cb4904c7bdb0884208592c92b09c842f250bb925d8f81fc0391499229"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Reading specs from /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/specs\nConfigured with: /proj/ee-toolchain/ee-gcc-3.2-final-rc2/release-src/ee-gcc/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-030926\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/accessor/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccvSP5WV.s\nGNU CPP version 3.2-ee-030926 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-030926 (ee)\n\tcompiled by GNU C version 3.2.\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-pdcgf22b/candidate.o /tmp/ccvSP5WV.s\nGNU assembler version 2.12-ee-030926 (ee) using BFD version 2.12-ee-030926 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "7f1968d435d96069f07d8c6ba17b8fff5c01f3a398f7850829029b05d36697a3",
            "text_sha256": "05b57dce92fdc9b17d504917281a523539cabf74979f1139e79210238e4b4559",
            "text_bytes": 64,
            "relocations": [
              {
                "offset": 4,
                "type": 5,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 12,
                "type": 6,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 36,
                "type": 6,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 32,
                "type": 5,
                "symbol_index": 6,
                "mask": "0000ffff"
              },
              {
                "offset": 40,
                "type": 6,
                "symbol_index": 6,
                "mask": "0000ffff"
              },
              {
                "offset": 44,
                "type": 4,
                "symbol_index": 14,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 60,
              "reason": "function length differs",
              "expected_bytes": 60,
              "actual_bytes": 64
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-pdcgf22b/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-pdcgf22b/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-pdcgf22b/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-pdcgf22b/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-pdcgf22b/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-pdcgf22b/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "2902d95cb4904c7bdb0884208592c92b09c842f250bb925d8f81fc0391499229",
          "actual_bytes": 64,
          "reference_sha256": "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 60,
            "first_difference": {
              "offset": 0,
              "address": "001d1800",
              "file_offset": "000d2800",
              "word": 0,
              "expected": "54ad838f",
              "actual": "f0ffbd27"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc3.2-040921",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-q1zwpzd2/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1",
              "bytes": 7201720,
              "sha256": "0bcc90bd23e10698e75047db9a84ea47e753791115fdd23d6f637a544f6d257d"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-cpp",
              "bytes": 266763,
              "sha256": "ed76fe8e08c13c749d59a458d21c912567b10e5e01bff028a4147debd56d15e6"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/ee/bin/as",
              "bytes": 3706255,
              "sha256": "cf85edec3ea30b0918e8a78ac49affca111a45e5b0ca9a776b6ded5c0118379b"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "a5095b5d7b55f91535b12e48e9d808170fa9fb8c0620c43c2fb61379b1a3663a",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-q1zwpzd2/candidate.o",
              "bytes": 1860,
              "sha256": "7f1968d435d96069f07d8c6ba17b8fff5c01f3a398f7850829029b05d36697a3"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-q1zwpzd2/prepared.o",
              "bytes": 1860,
              "sha256": "0e9c24584cef8752dfabece3105b83a97ffad1c6f7161c7e0ef171b6fd56eade"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-q1zwpzd2/linked.o",
              "bytes": 14640,
              "sha256": "e7c8dd24beac65e44eb68fa19cb6fb70da797e3d6af15578b002ea9313ec888c"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-q1zwpzd2/function.bin",
              "bytes": 64,
              "sha256": "2902d95cb4904c7bdb0884208592c92b09c842f250bb925d8f81fc0391499229"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Using built-in specs.\nConfigured with: ../src/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-040921\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/accessor/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccG4i9za.s\nGNU CPP version 3.2-ee-040921 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-040921 (ee)\n\tcompiled by GNU C version 3.2.2 20030222 (Red Hat Linux 3.2.2-5).\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-q1zwpzd2/candidate.o /tmp/ccG4i9za.s\nGNU assembler version 2.12-ee-040921 (ee) using BFD version 2.12-ee-040921 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "7f1968d435d96069f07d8c6ba17b8fff5c01f3a398f7850829029b05d36697a3",
            "text_sha256": "05b57dce92fdc9b17d504917281a523539cabf74979f1139e79210238e4b4559",
            "text_bytes": 64,
            "relocations": [
              {
                "offset": 4,
                "type": 5,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 12,
                "type": 6,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 36,
                "type": 6,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 32,
                "type": 5,
                "symbol_index": 6,
                "mask": "0000ffff"
              },
              {
                "offset": 40,
                "type": 6,
                "symbol_index": 6,
                "mask": "0000ffff"
              },
              {
                "offset": 44,
                "type": 4,
                "symbol_index": 14,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 60,
              "reason": "function length differs",
              "expected_bytes": 60,
              "actual_bytes": 64
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-q1zwpzd2/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-q1zwpzd2/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-q1zwpzd2/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-q1zwpzd2/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-q1zwpzd2/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-q1zwpzd2/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "2902d95cb4904c7bdb0884208592c92b09c842f250bb925d8f81fc0391499229",
          "actual_bytes": 64,
          "reference_sha256": "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 60,
            "first_difference": {
              "offset": 0,
              "address": "001d1800",
              "file_offset": "000d2800",
              "word": 0,
              "expected": "54ad838f",
              "actual": "f0ffbd27"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.95.2-273a",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/bin/ee-gcc.exe",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "platform": "linux/amd64",
            "runner": "Wine 8 Debian Bookworm on Linux amd64 via Docker Desktop"
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-617paopu/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/cc1.exe",
              "bytes": 1773568,
              "sha256": "2aaf3d22ce5c3508ecba15f16b06737713263e6aee289ca1e43d3ff9c17d964f"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/cpp.exe",
              "bytes": 110592,
              "sha256": "f7db993de8745339ec71cf10d5fe9e7772d75e79a037e97809ed5e34ea3150c3"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/specs",
              "bytes": 4260,
              "sha256": "372d6255779b9214f7f980a8289461209c9be4cb12a91c6b4e01e14c0f91070c"
            }
          },
          "compiler_sha256": "ab787f9bda2531e116f420eec639e7d34bcc92caf4eb8d3dc71fefddffd3fcfc",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-617paopu/candidate.o",
              "bytes": 2004,
              "sha256": "7ed73452f627dbe04b68bbae6eb9657519e169e84e1c9d92ed4159aae476a7b7"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-617paopu/prepared.o",
              "bytes": 1908,
              "sha256": "e75629fe17701696a1c01ce4a72e761859abe7c21051af70cb8e82ed3d4a0e26"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-617paopu/linked.o",
              "bytes": 14696,
              "sha256": "16b411a84348c5ecfab1b5229503876cdb36bfa713fb8f8f19f9b357e4455a32"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-617paopu/function.bin",
              "bytes": 68,
              "sha256": "31f5767905e165342ac41afabee74e3e2bcf55cdaad6c74aca29af11a20addd8"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.2-EE\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/accessor/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.2 v2 [AL 1.1, MM 40] BSD Mips\n#include \"...\" search starts here:\nEnd of search list.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.2 SN BUILD v2.73a for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-617paopu/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "7ed73452f627dbe04b68bbae6eb9657519e169e84e1c9d92ed4159aae476a7b7",
            "text_sha256": "1a162e8a8782b95797658915b85024083e4c30fc2b3954a8c945a5578821df7d",
            "text_bytes": 68,
            "relocations": [
              {
                "offset": 4,
                "type": 7,
                "symbol_index": 14,
                "mask": "0000ffff"
              },
              {
                "offset": 20,
                "type": 5,
                "symbol_index": 4,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 6,
                "symbol_index": 4,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 5,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 32,
                "type": 6,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 36,
                "type": 4,
                "symbol_index": 15,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 60,
              "reason": "function length differs",
              "expected_bytes": 60,
              "actual_bytes": 68
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-617paopu/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-617paopu/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-617paopu/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-617paopu/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-617paopu/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-617paopu/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "31f5767905e165342ac41afabee74e3e2bcf55cdaad6c74aca29af11a20addd8",
          "actual_bytes": 68,
          "reference_sha256": "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 60,
            "first_difference": {
              "offset": 0,
              "address": "001d1800",
              "file_offset": "000d2800",
              "word": 0,
              "expected": "54ad838f",
              "actual": "f0ffbd27"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.95.3-114",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/bin/ee-gcc.exe",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "platform": "linux/amd64",
            "runner": "Wine 8 Debian Bookworm on Linux amd64 via Docker Desktop"
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-9ihieel9/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1654784,
              "sha256": "7bccdee8d6cc6bc56a84824cadb9c5ce546a1aa7f9b836447d2482408c5c5832"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "271e9a55b782153acf303566c93c18ea30253e9c14d4df4daa55c521ead92eef"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "compiler_sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-9ihieel9/candidate.o",
              "bytes": 2004,
              "sha256": "7ed73452f627dbe04b68bbae6eb9657519e169e84e1c9d92ed4159aae476a7b7"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-9ihieel9/prepared.o",
              "bytes": 1908,
              "sha256": "e75629fe17701696a1c01ce4a72e761859abe7c21051af70cb8e82ed3d4a0e26"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-9ihieel9/linked.o",
              "bytes": 14696,
              "sha256": "16b411a84348c5ecfab1b5229503876cdb36bfa713fb8f8f19f9b357e4455a32"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-9ihieel9/function.bin",
              "bytes": 68,
              "sha256": "31f5767905e165342ac41afabee74e3e2bcf55cdaad6c74aca29af11a20addd8"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/accessor/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.05 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-114/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.14 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-9ihieel9/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "7ed73452f627dbe04b68bbae6eb9657519e169e84e1c9d92ed4159aae476a7b7",
            "text_sha256": "1a162e8a8782b95797658915b85024083e4c30fc2b3954a8c945a5578821df7d",
            "text_bytes": 68,
            "relocations": [
              {
                "offset": 4,
                "type": 7,
                "symbol_index": 14,
                "mask": "0000ffff"
              },
              {
                "offset": 20,
                "type": 5,
                "symbol_index": 4,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 6,
                "symbol_index": 4,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 5,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 32,
                "type": 6,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 36,
                "type": 4,
                "symbol_index": 15,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 60,
              "reason": "function length differs",
              "expected_bytes": 60,
              "actual_bytes": 68
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-9ihieel9/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-9ihieel9/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-9ihieel9/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-9ihieel9/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-9ihieel9/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-9ihieel9/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "31f5767905e165342ac41afabee74e3e2bcf55cdaad6c74aca29af11a20addd8",
          "actual_bytes": 68,
          "reference_sha256": "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 60,
            "first_difference": {
              "offset": 0,
              "address": "001d1800",
              "file_offset": "000d2800",
              "word": 0,
              "expected": "54ad838f",
              "actual": "f0ffbd27"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.95.3-136",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/bin/ee-gcc.exe",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "platform": "linux/amd64",
            "runner": "Wine 8 Debian Bookworm on Linux amd64 via Docker Desktop"
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-lr1t7kzo/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1708032,
              "sha256": "0393bcd31f91a6b9f0255db97f1cc99eba78ee8fc003e9a04dfabed1ae1d522e"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "b9c50aa66f9cf5dbd80b2affe9874ec7674b7328965c629476f6ad7c77943154"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "compiler_sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-lr1t7kzo/candidate.o",
              "bytes": 2004,
              "sha256": "a21e30ba8ece43f6b9d12d9734aab6b0b58e0d25dc38c2cc226e15010485c7ed"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-lr1t7kzo/prepared.o",
              "bytes": 1908,
              "sha256": "043a9615cb3a99750a30e7c00aae10f684883aabeeb3fda8fae9ab51d74095bf"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-lr1t7kzo/linked.o",
              "bytes": 14696,
              "sha256": "6ca6d6343eff20422152bafce4bbb1f9e8fb2574e596f9690dcaad7eb660078e"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-lr1t7kzo/function.bin",
              "bytes": 68,
              "sha256": "6611e74411e449673728a17e0a54312d978727f1196df62c093458e91253c618"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/accessor/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.12 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-136/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.36 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-lr1t7kzo/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "a21e30ba8ece43f6b9d12d9734aab6b0b58e0d25dc38c2cc226e15010485c7ed",
            "text_sha256": "fd99e7efe0c3aca0a59ad74ab6fab58019da19d2879bec3e594469f7ff601b21",
            "text_bytes": 68,
            "relocations": [
              {
                "offset": 4,
                "type": 7,
                "symbol_index": 14,
                "mask": "0000ffff"
              },
              {
                "offset": 20,
                "type": 5,
                "symbol_index": 4,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 6,
                "symbol_index": 4,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 5,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 32,
                "type": 6,
                "symbol_index": 5,
                "mask": "0000ffff"
              },
              {
                "offset": 36,
                "type": 4,
                "symbol_index": 15,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 60,
              "reason": "function length differs",
              "expected_bytes": 60,
              "actual_bytes": 68
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-lr1t7kzo/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-lr1t7kzo/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-lr1t7kzo/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-lr1t7kzo/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-lr1t7kzo/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/accessor/objects/fr2-compiler-probe-lr1t7kzo/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "6611e74411e449673728a17e0a54312d978727f1196df62c093458e91253c618",
          "actual_bytes": 68,
          "reference_sha256": "1dc86d826f214003c72279c975fcb246a45a5383f407ee0d96f81e987333522e",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 60,
            "first_difference": {
              "offset": 0,
              "address": "001d1800",
              "file_offset": "000d2800",
              "word": 0,
              "expected": "54ad838f",
              "actual": "f0ffbd27"
            }
          },
          "reason": "function bytes differ"
        }
      ],
      "claim_limits": [
        "A unique match identifies this source/compiler/flags/reference probe only.",
        "It does not establish the original compiler ID without an independently evidenced retail function/reference pair.",
        "This runner executes compiler and objcopy argv from the local manifest."
      ],
      "unit": "accessor",
      "package_members": [
        {
          "candidate": "ee-gcc2.9-991111-01",
          "archive": "ee-gcc2.9-991111-01.tar.xz",
          "sha256": "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 154155,
              "sha256": "64d0a50fef499da0b98177eb5e79e41dfb066ad44246b137c78a266ef97ee265"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.9-ee-991111-01/cc1",
              "bytes": 4794381,
              "sha256": "b9aef69f93efb949f15ea58189e8eef4a002b9fe4de5d3fcf89c34e1244ec026"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.9-ee-991111-01/cpp",
              "bytes": 241396,
              "sha256": "f85a54d241e019993fa7a06285d3677856b3b431e10318a587ab029373c603d7"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 2210289,
              "sha256": "296af123052ee39d175e5b3254102aafca105d4f6e975b351a13867f59b04019"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.96",
          "archive": "ee-gcc2.96.tar.xz",
          "sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 333402,
              "sha256": "b8c284d16c9c0a0e8788e9522c46881e224ad01fa1c732aed43f821cc32f168b"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.96-ee-001003-1/cc1",
              "bytes": 5526661,
              "sha256": "59ec92b3f9f3513e0633331af304733e3094de30884e662a8cb584a51c1c42b5"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.96-ee-001003-1/cpp0",
              "bytes": 421478,
              "sha256": "f6f6b598f39649edfe171d6da8c7f91d07f2b87c2aeeffffbc5f566bfb1a39a9"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 2169068,
              "sha256": "b8cfdb6ecb6931642914020f92a62e653378f57230eed4895f69afa050d47b5e"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc3.2-030926",
          "archive": "ee-gcc3.2-030926.tar.gz",
          "sha256": "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 335156,
              "sha256": "8ba17b0f2cbcc87b31bb164766bc3e7e340f714adfb518bc4634a6f1ffda8951"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/3.2-ee-030926/cc1",
              "bytes": 9764536,
              "sha256": "da4fec4d48d91e62fd968f76acb16981dd8131d02f27c1b7559f0e903b590eb6"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/3.2-ee-030926/cpp0",
              "bytes": 703785,
              "sha256": "2d1a4b260e143a8b467bb7609cb3fd60ae541174ffff78d922feb2d7fbb0e218"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 5887159,
              "sha256": "d04424acb1359b31b3ad138f8d17876623ffe9182497ff4516055b71f22bf2fa"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc3.2-040921",
          "archive": "ee-gcc3.2-040921.tar.xz",
          "sha256": "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 265116,
              "sha256": "a5095b5d7b55f91535b12e48e9d808170fa9fb8c0620c43c2fb61379b1a3663a"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/3.2-ee-040921/cc1",
              "bytes": 7201720,
              "sha256": "0bcc90bd23e10698e75047db9a84ea47e753791115fdd23d6f637a544f6d257d"
            },
            "cpp": {
              "member": "bin/ee-cpp",
              "bytes": 266763,
              "sha256": "ed76fe8e08c13c749d59a458d21c912567b10e5e01bff028a4147debd56d15e6"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 3706255,
              "sha256": "cf85edec3ea30b0918e8a78ac49affca111a45e5b0ca9a776b6ded5c0118379b"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.95.2-273a",
          "archive": "ee-gcc2.95.2-273a.tar.gz",
          "sha256": "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e",
          "members": {
            "driver": {
              "member": "bin/ee-gcc.exe",
              "bytes": 122880,
              "sha256": "ab787f9bda2531e116f420eec639e7d34bcc92caf4eb8d3dc71fefddffd3fcfc"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.95.2/cc1.exe",
              "bytes": 1773568,
              "sha256": "2aaf3d22ce5c3508ecba15f16b06737713263e6aee289ca1e43d3ff9c17d964f"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.95.2/cpp.exe",
              "bytes": 110592,
              "sha256": "f7db993de8745339ec71cf10d5fe9e7772d75e79a037e97809ed5e34ea3150c3"
            },
            "gnu_assembler": {
              "member": "lib/gcc-lib/ee/2.95.2/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "member": "lib/gcc-lib/ee/2.95.2/specs",
              "bytes": 4260,
              "sha256": "372d6255779b9214f7f980a8289461209c9be4cb12a91c6b4e01e14c0f91070c"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.95.3-114",
          "archive": "ee-gcc2.95.3-114.tar.gz",
          "sha256": "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb",
          "members": {
            "driver": {
              "member": "bin/ee-gcc.exe",
              "bytes": 122880,
              "sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1654784,
              "sha256": "7bccdee8d6cc6bc56a84824cadb9c5ce546a1aa7f9b836447d2482408c5c5832"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "271e9a55b782153acf303566c93c18ea30253e9c14d4df4daa55c521ead92eef"
            },
            "gnu_assembler": {
              "member": "lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "member": "lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.95.3-136",
          "archive": "ee-gcc2.95.3-136.tar.gz",
          "sha256": "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f",
          "members": {
            "driver": {
              "member": "bin/ee-gcc.exe",
              "bytes": 122880,
              "sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1708032,
              "sha256": "0393bcd31f91a6b9f0255db97f1cc99eba78ee8fc003e9a04dfabed1ae1d522e"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "b9c50aa66f9cf5dbd80b2affe9874ec7674b7328965c629476f6ad7c77943154"
            },
            "gnu_assembler": {
              "member": "lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "member": "lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        }
      ],
      "package_identity_status": "pass"
    },
    {
      "status": "incomplete",
      "selected_id": null,
      "matches": [
        "ee-gcc2.9-991111-01",
        "ee-gcc2.96",
        "ee-gcc2.95.2-273a",
        "ee-gcc2.95.3-114",
        "ee-gcc2.95.3-136"
      ],
      "failures": [
        "ee-gcc3.2-030926",
        "ee-gcc3.2-040921"
      ],
      "errors": [],
      "incomplete": [],
      "manifest": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/manifest.json",
        "bytes": 29641,
        "sha256": "5bfaf94f74d0dfda12b2cf8300dd456d8df43d79f699a17dc8024834cbf13693"
      },
      "evidence": {
        "corpus": {
          "profile": "fr2-pal-sles-517.05",
          "sources": {
            "ford-racing-2.bin": {
              "bytes": 678667248,
              "sha256": "ae8d5a32c9d832f34a08fad6f0e97ce6e89e6b040597011f6362d886145b9d3d"
            },
            "ford-racing-2.cue": {
              "bytes": 79,
              "sha256": "c2e0aaf75a43150567f4ffe02ac863c8d1bda8f2fdf744012361436ec582edb6"
            },
            "extracted/SLES_517.05": {
              "bytes": 1662804,
              "sha256": "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95"
            },
            "extracted/FILES.HDR": {
              "bytes": 29428,
              "sha256": "f4e4a4f91cd89bcaa8c2772e6cba2a839d92fbe222290c8c751777a81963731d"
            },
            "extracted/FILES.DAT": {
              "bytes": 334641152,
              "sha256": "357fc371f47e366bf507b721e26eed9f1205516c19b793e0316ccecc2175a722"
            }
          },
          "corpus_id": "e69a2afbd6db606d166e40bae32c436691e134722ad153200859961a5f517dab"
        },
        "reference_range": {
          "section": ".text",
          "vaddr": "001d17a8",
          "bytes": 28,
          "file_offset": "000d27a8",
          "sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "scope": "mixed"
        },
        "candidate_source": "Hand-written exploratory reconstruction; inferred names, ABI and ownership; not original source.",
        "tool_source": "decompme/compilers release tag compilers; per-candidate archive URLs and SHA-256 values follow.",
        "tool_distributions": [
          {
            "candidate": "ee-gcc2.9-991111-01",
            "archive": "ee-gcc2.9-991111-01.tar.xz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.9-991111-01.tar.xz",
            "expected_sha256": "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8",
            "available_locally": true,
            "observed_sha256": "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8"
          },
          {
            "candidate": "ee-gcc2.95.2-273a",
            "archive": "ee-gcc2.95.2-273a.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.2-273a.tar.gz",
            "expected_sha256": "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e",
            "available_locally": true,
            "observed_sha256": "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e"
          },
          {
            "candidate": "ee-gcc2.95.3-114",
            "archive": "ee-gcc2.95.3-114.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.3-114.tar.gz",
            "expected_sha256": "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb",
            "available_locally": true,
            "observed_sha256": "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb"
          },
          {
            "candidate": "ee-gcc2.95.3-136",
            "archive": "ee-gcc2.95.3-136.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.3-136.tar.gz",
            "expected_sha256": "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f",
            "available_locally": true,
            "observed_sha256": "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f"
          },
          {
            "candidate": "ee-gcc2.96",
            "archive": "ee-gcc2.96.tar.xz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.96.tar.xz",
            "expected_sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a",
            "available_locally": true,
            "observed_sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a"
          },
          {
            "candidate": "ee-gcc3.2-030926",
            "archive": "ee-gcc3.2-030926.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-030926.tar.gz",
            "expected_sha256": "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9",
            "available_locally": true,
            "observed_sha256": "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9"
          },
          {
            "candidate": "ee-gcc3.2-040921",
            "archive": "ee-gcc3.2-040921.tar.xz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-040921.tar.xz",
            "expected_sha256": "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f",
            "available_locally": true,
            "observed_sha256": "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f"
          }
        ],
        "license_status": "The release archives inspected do not include COPYING or LICENSE entries. Per-package redistribution terms are unresolved; no compiler binaries are redistributed here.",
        "runtime_profile": "Immutable image IDs are verified before invocation: Debian Bookworm linux/amd64 with Wine 8 for Windows compiler drivers, and GNU binutils 2.40 in the Debian image for object preparation, linking, and objcopy.",
        "linker_profile": "GNU binutils 2.40 substitution; not the original proprietary linker.",
        "independent_unit": {
          "id": "misc3d_reset",
          "symbol": "fr2_misc3d_reset",
          "source": "tools/compiler_probe_recipe/misc3d_reset.c",
          "source_sha256": "a447ce7bffe4ab51cf7151f0d504d1e7a83e5cd6e715cb981a582c89f101e19f",
          "vaddr": "001d17a8",
          "bytes": 28,
          "sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "definitions": {
            "fr2_db_id": "00290ac4",
            "fr2_material_a": "00290ac8",
            "fr2_material_b": "00290acc",
            "fr2_material_c": "00290ad0",
            "fr2_material_d": "00290ad4"
          },
          "source_path": "../fr2/source/app3d/misc3d.c",
          "independent_basis": "Source-map enclosure between direct anchors 001d1408 and 001d1800; direct static caller 001ccbd8. Five gp stores of the sentinel end in a return delay-slot store.",
          "distinguishes": "Small-data relocation choice, store scheduling and delay-slot scheduling; no call or frame.",
          "static_callers": [
            "001ccbd8"
          ],
          "body_ranges": [
            {
              "start": "001d17a8",
              "end": "001d17c3"
            }
          ],
          "claim_limit": "Hand-written inference from independent static evidence; names/types are provisional; no original-source, execution or owned-byte credit. Store source order was explored; this unit cannot by itself identify an original compiler."
        }
      },
      "source": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.c",
        "bytes": 384,
        "sha256": "a447ce7bffe4ab51cf7151f0d504d1e7a83e5cd6e715cb981a582c89f101e19f"
      },
      "reference": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/reference.bin",
        "bytes": 28,
        "sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce"
      },
      "symbol": "fr2_misc3d_reset",
      "candidates": [
        {
          "id": "ee-gcc2.9-991111-01",
          "status": "pass",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/bin/ee-gcc",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-wcxixybi/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/lib/gcc-lib/ee/2.9-ee-991111-01/cc1",
              "bytes": 4794381,
              "sha256": "b9aef69f93efb949f15ea58189e8eef4a002b9fe4de5d3fcf89c34e1244ec026"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/lib/gcc-lib/ee/2.9-ee-991111-01/cpp",
              "bytes": 241396,
              "sha256": "f85a54d241e019993fa7a06285d3677856b3b431e10318a587ab029373c603d7"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/ee/bin/as",
              "bytes": 2210289,
              "sha256": "296af123052ee39d175e5b3254102aafca105d4f6e975b351a13867f59b04019"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "64d0a50fef499da0b98177eb5e79e41dfb066ad44246b137c78a266ef97ee265",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-wcxixybi/candidate.o",
              "bytes": 1716,
              "sha256": "c7c746990629b777f7000dfa993db4fb93bb27c5898b5d82dfc0a730e5a5a4de"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-wcxixybi/prepared.o",
              "bytes": 1628,
              "sha256": "06da623635a8e4a5bb21fcc92aa27a9d86163d5c74425c925d65c353aa93379c"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-wcxixybi/linked.o",
              "bytes": 7524,
              "sha256": "9f5a8b88b0af00e9bb7562e7f10d69aa5dba29701bdba3fd0fe436c7cb36820d"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-wcxixybi/function.bin",
              "bytes": 28,
              "sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Using builtin specs.\ngcc version 2.9-ee-991111-01\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/cc1 /tools/compiler-profile-if5l6kuy/misc3d_reset/candidate.c -G8 -lang-c -iprefix /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/ -quiet -dumpbase candidate.c -undef -D__GNUC__=2 -D__GNUC_MINOR__=9 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float -version -ffunction-sections -O2 -o /tmp/cciGDXkg.s\nGNU C version 2.9-ee-991111-01 (ee) compiled by GNU C version 2.7.2.3.\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/../../../../ee/bin/as -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-wcxixybi/candidate.o /tmp/cciGDXkg.s\nGNU assembler version 2.9-ee-991111 (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "c7c746990629b777f7000dfa993db4fb93bb27c5898b5d82dfc0a730e5a5a4de",
            "text_sha256": "43e2be8a034f051b91fbede07cb6ff7b033815afa76effaa8c521e4e82135fae",
            "text_bytes": 28,
            "relocations": [
              {
                "offset": 4,
                "type": 7,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 8,
                "type": 7,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 12,
                "type": 7,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 7,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 7,
                "symbol_index": 14,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof."
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-wcxixybi/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-wcxixybi/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-wcxixybi/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-wcxixybi/prepared.o",
            "--defsym=fr2_db_id=0x00290ac4",
            "--defsym=fr2_material_a=0x00290ac8",
            "--defsym=fr2_material_b=0x00290acc",
            "--defsym=fr2_material_c=0x00290ad0",
            "--defsym=fr2_material_d=0x00290ad4",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-wcxixybi/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-wcxixybi/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "actual_bytes": 28,
          "reference_sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "reference_bytes": 28,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "pass",
            "reason": null,
            "matched_bytes": 28,
            "section_bytes": 28
          }
        },
        {
          "id": "ee-gcc2.96",
          "status": "pass",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-jec992kh/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/cc1",
              "bytes": 5526661,
              "sha256": "59ec92b3f9f3513e0633331af304733e3094de30884e662a8cb584a51c1c42b5"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/cpp0",
              "bytes": 421478,
              "sha256": "f6f6b598f39649edfe171d6da8c7f91d07f2b87c2aeeffffbc5f566bfb1a39a9"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/ee/bin/as",
              "bytes": 2169068,
              "sha256": "b8cfdb6ecb6931642914020f92a62e653378f57230eed4895f69afa050d47b5e"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "b8c284d16c9c0a0e8788e9522c46881e224ad01fa1c732aed43f821cc32f168b",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-jec992kh/candidate.o",
              "bytes": 1856,
              "sha256": "006cf1879982c427b41b8a67de741103e8f780e0efbfc8f3a0cb4e0d34bbc9c4"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-jec992kh/prepared.o",
              "bytes": 1700,
              "sha256": "10f72cb91c8eb1ea2a736dbb77ad2260d7b075a9d9b11d297cbf09d159f790b9"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-jec992kh/linked.o",
              "bytes": 7524,
              "sha256": "9f5a8b88b0af00e9bb7562e7f10d69aa5dba29701bdba3fd0fe436c7cb36820d"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-jec992kh/function.bin",
              "bytes": 28,
              "sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Using builtin specs.\ngcc version 2.96-ee-001003-1\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/ -D__GNUC__=2 -D__GNUC_MINOR__=96 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/misc3d_reset/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccgKmDPg.s\nGNU CPP version 2.96-ee-001003-1 (cpplib)\n [AL 1.1, MM 40] BSD Mips\nGNU C version 2.96-ee-001003-1 (ee) compiled by GNU C version 2.9-gnupro-99r1.\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/sys-include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/sys-include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/../../../../ee/bin/as -G8 -EL -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-jec992kh/candidate.o /tmp/ccgKmDPg.s\nGNU assembler version 2.10-ee-001003-1 (ee) using BFD version 2.10-ee-001003\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "006cf1879982c427b41b8a67de741103e8f780e0efbfc8f3a0cb4e0d34bbc9c4",
            "text_sha256": "43e2be8a034f051b91fbede07cb6ff7b033815afa76effaa8c521e4e82135fae",
            "text_bytes": 28,
            "relocations": [
              {
                "offset": 4,
                "type": 7,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 8,
                "type": 7,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 12,
                "type": 7,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 7,
                "symbol_index": 14,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 7,
                "symbol_index": 15,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof."
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-jec992kh/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-jec992kh/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-jec992kh/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-jec992kh/prepared.o",
            "--defsym=fr2_db_id=0x00290ac4",
            "--defsym=fr2_material_a=0x00290ac8",
            "--defsym=fr2_material_b=0x00290acc",
            "--defsym=fr2_material_c=0x00290ad0",
            "--defsym=fr2_material_d=0x00290ad4",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-jec992kh/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-jec992kh/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "actual_bytes": 28,
          "reference_sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "reference_bytes": 28,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "pass",
            "reason": null,
            "matched_bytes": 28,
            "section_bytes": 28
          }
        },
        {
          "id": "ee-gcc3.2-030926",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-i6wk4hh6/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/cc1",
              "bytes": 9764536,
              "sha256": "da4fec4d48d91e62fd968f76acb16981dd8131d02f27c1b7559f0e903b590eb6"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/cpp0",
              "bytes": 703785,
              "sha256": "2d1a4b260e143a8b467bb7609cb3fd60ae541174ffff78d922feb2d7fbb0e218"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/ee/bin/as",
              "bytes": 5887159,
              "sha256": "d04424acb1359b31b3ad138f8d17876623ffe9182497ff4516055b71f22bf2fa"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "8ba17b0f2cbcc87b31bb164766bc3e7e340f714adfb518bc4634a6f1ffda8951",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-i6wk4hh6/candidate.o",
              "bytes": 1640,
              "sha256": "76217ec192e4a841acd84a4e84a676d93cbf6f5eabdfd7ab49b44e19ffb4cf33"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-i6wk4hh6/prepared.o",
              "bytes": 1640,
              "sha256": "151e0651476062719bcd0245a818a66bd532de90d22d0c2c699faa122d78a4ba"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-i6wk4hh6/linked.o",
              "bytes": 7488,
              "sha256": "d1c9e5f3d4a258007519666af4f064994e7e6c40d9cd7ffbf9a415bdb0765191"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-i6wk4hh6/function.bin",
              "bytes": 48,
              "sha256": "2076c3accf31374474ef88460166f318e65ca3efa2bcc773724f1cbe390d3c61"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Reading specs from /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/specs\nConfigured with: /proj/ee-toolchain/ee-gcc-3.2-final-rc2/release-src/ee-gcc/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-030926\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/misc3d_reset/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccVJ6x4u.s\nGNU CPP version 3.2-ee-030926 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-030926 (ee)\n\tcompiled by GNU C version 3.2.\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-i6wk4hh6/candidate.o /tmp/ccVJ6x4u.s\nGNU assembler version 2.12-ee-030926 (ee) using BFD version 2.12-ee-030926 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "76217ec192e4a841acd84a4e84a676d93cbf6f5eabdfd7ab49b44e19ffb4cf33",
            "text_sha256": "2ce906e1330795f166e7b7bea26a5d46685437c9a49619d8ba477d1b83f3daf3",
            "text_bytes": 48,
            "relocations": [
              {
                "offset": 4,
                "type": 5,
                "symbol_index": 9,
                "mask": "0000ffff"
              },
              {
                "offset": 8,
                "type": 6,
                "symbol_index": 9,
                "mask": "0000ffff"
              },
              {
                "offset": 12,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 20,
                "type": 5,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 6,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 32,
                "type": 6,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 36,
                "type": 5,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 44,
                "type": 6,
                "symbol_index": 13,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 28,
              "reason": "function length differs",
              "expected_bytes": 28,
              "actual_bytes": 48
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-i6wk4hh6/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-i6wk4hh6/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-i6wk4hh6/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-i6wk4hh6/prepared.o",
            "--defsym=fr2_db_id=0x00290ac4",
            "--defsym=fr2_material_a=0x00290ac8",
            "--defsym=fr2_material_b=0x00290acc",
            "--defsym=fr2_material_c=0x00290ad0",
            "--defsym=fr2_material_d=0x00290ad4",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-i6wk4hh6/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-i6wk4hh6/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "2076c3accf31374474ef88460166f318e65ca3efa2bcc773724f1cbe390d3c61",
          "actual_bytes": 48,
          "reference_sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "reference_bytes": 28,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 28,
            "first_difference": {
              "offset": 0,
              "address": "001d17a8",
              "file_offset": "000d27a8",
              "word": 0,
              "expected": "ffff0224",
              "actual": "ffff0d24"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc3.2-040921",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-9s_c7t2n/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1",
              "bytes": 7201720,
              "sha256": "0bcc90bd23e10698e75047db9a84ea47e753791115fdd23d6f637a544f6d257d"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-cpp",
              "bytes": 266763,
              "sha256": "ed76fe8e08c13c749d59a458d21c912567b10e5e01bff028a4147debd56d15e6"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/ee/bin/as",
              "bytes": 3706255,
              "sha256": "cf85edec3ea30b0918e8a78ac49affca111a45e5b0ca9a776b6ded5c0118379b"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "a5095b5d7b55f91535b12e48e9d808170fa9fb8c0620c43c2fb61379b1a3663a",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-9s_c7t2n/candidate.o",
              "bytes": 1640,
              "sha256": "76217ec192e4a841acd84a4e84a676d93cbf6f5eabdfd7ab49b44e19ffb4cf33"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-9s_c7t2n/prepared.o",
              "bytes": 1640,
              "sha256": "151e0651476062719bcd0245a818a66bd532de90d22d0c2c699faa122d78a4ba"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-9s_c7t2n/linked.o",
              "bytes": 7488,
              "sha256": "d1c9e5f3d4a258007519666af4f064994e7e6c40d9cd7ffbf9a415bdb0765191"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-9s_c7t2n/function.bin",
              "bytes": 48,
              "sha256": "2076c3accf31374474ef88460166f318e65ca3efa2bcc773724f1cbe390d3c61"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Using built-in specs.\nConfigured with: ../src/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-040921\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/misc3d_reset/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccualvwH.s\nGNU CPP version 3.2-ee-040921 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-040921 (ee)\n\tcompiled by GNU C version 3.2.2 20030222 (Red Hat Linux 3.2.2-5).\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-9s_c7t2n/candidate.o /tmp/ccualvwH.s\nGNU assembler version 2.12-ee-040921 (ee) using BFD version 2.12-ee-040921 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "76217ec192e4a841acd84a4e84a676d93cbf6f5eabdfd7ab49b44e19ffb4cf33",
            "text_sha256": "2ce906e1330795f166e7b7bea26a5d46685437c9a49619d8ba477d1b83f3daf3",
            "text_bytes": 48,
            "relocations": [
              {
                "offset": 4,
                "type": 5,
                "symbol_index": 9,
                "mask": "0000ffff"
              },
              {
                "offset": 8,
                "type": 6,
                "symbol_index": 9,
                "mask": "0000ffff"
              },
              {
                "offset": 12,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 20,
                "type": 5,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 6,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 32,
                "type": 6,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 36,
                "type": 5,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 44,
                "type": 6,
                "symbol_index": 13,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 28,
              "reason": "function length differs",
              "expected_bytes": 28,
              "actual_bytes": 48
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-9s_c7t2n/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-9s_c7t2n/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-9s_c7t2n/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-9s_c7t2n/prepared.o",
            "--defsym=fr2_db_id=0x00290ac4",
            "--defsym=fr2_material_a=0x00290ac8",
            "--defsym=fr2_material_b=0x00290acc",
            "--defsym=fr2_material_c=0x00290ad0",
            "--defsym=fr2_material_d=0x00290ad4",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-9s_c7t2n/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-9s_c7t2n/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "2076c3accf31374474ef88460166f318e65ca3efa2bcc773724f1cbe390d3c61",
          "actual_bytes": 48,
          "reference_sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "reference_bytes": 28,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 28,
            "first_difference": {
              "offset": 0,
              "address": "001d17a8",
              "file_offset": "000d27a8",
              "word": 0,
              "expected": "ffff0224",
              "actual": "ffff0d24"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.95.2-273a",
          "status": "pass",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/bin/ee-gcc.exe",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "platform": "linux/amd64",
            "runner": "Wine 8 Debian Bookworm on Linux amd64 via Docker Desktop"
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-b0z5z0o6/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/cc1.exe",
              "bytes": 1773568,
              "sha256": "2aaf3d22ce5c3508ecba15f16b06737713263e6aee289ca1e43d3ff9c17d964f"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/cpp.exe",
              "bytes": 110592,
              "sha256": "f7db993de8745339ec71cf10d5fe9e7772d75e79a037e97809ed5e34ea3150c3"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/specs",
              "bytes": 4260,
              "sha256": "372d6255779b9214f7f980a8289461209c9be4cb12a91c6b4e01e14c0f91070c"
            }
          },
          "compiler_sha256": "ab787f9bda2531e116f420eec639e7d34bcc92caf4eb8d3dc71fefddffd3fcfc",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-b0z5z0o6/candidate.o",
              "bytes": 1716,
              "sha256": "c7c746990629b777f7000dfa993db4fb93bb27c5898b5d82dfc0a730e5a5a4de"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-b0z5z0o6/prepared.o",
              "bytes": 1628,
              "sha256": "06da623635a8e4a5bb21fcc92aa27a9d86163d5c74425c925d65c353aa93379c"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-b0z5z0o6/linked.o",
              "bytes": 7524,
              "sha256": "9f5a8b88b0af00e9bb7562e7f10d69aa5dba29701bdba3fd0fe436c7cb36820d"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-b0z5z0o6/function.bin",
              "bytes": 28,
              "sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.2-EE\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/misc3d_reset/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.2 v2 [AL 1.1, MM 40] BSD Mips\n#include \"...\" search starts here:\nEnd of search list.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.2 SN BUILD v2.73a for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-b0z5z0o6/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "c7c746990629b777f7000dfa993db4fb93bb27c5898b5d82dfc0a730e5a5a4de",
            "text_sha256": "43e2be8a034f051b91fbede07cb6ff7b033815afa76effaa8c521e4e82135fae",
            "text_bytes": 28,
            "relocations": [
              {
                "offset": 4,
                "type": 7,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 8,
                "type": 7,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 12,
                "type": 7,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 7,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 7,
                "symbol_index": 14,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof."
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-b0z5z0o6/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-b0z5z0o6/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-b0z5z0o6/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-b0z5z0o6/prepared.o",
            "--defsym=fr2_db_id=0x00290ac4",
            "--defsym=fr2_material_a=0x00290ac8",
            "--defsym=fr2_material_b=0x00290acc",
            "--defsym=fr2_material_c=0x00290ad0",
            "--defsym=fr2_material_d=0x00290ad4",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-b0z5z0o6/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-b0z5z0o6/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "actual_bytes": 28,
          "reference_sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "reference_bytes": 28,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "pass",
            "reason": null,
            "matched_bytes": 28,
            "section_bytes": 28
          }
        },
        {
          "id": "ee-gcc2.95.3-114",
          "status": "pass",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/bin/ee-gcc.exe",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "platform": "linux/amd64",
            "runner": "Wine 8 Debian Bookworm on Linux amd64 via Docker Desktop"
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-bv_533gm/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1654784,
              "sha256": "7bccdee8d6cc6bc56a84824cadb9c5ce546a1aa7f9b836447d2482408c5c5832"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "271e9a55b782153acf303566c93c18ea30253e9c14d4df4daa55c521ead92eef"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "compiler_sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-bv_533gm/candidate.o",
              "bytes": 1716,
              "sha256": "c7c746990629b777f7000dfa993db4fb93bb27c5898b5d82dfc0a730e5a5a4de"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-bv_533gm/prepared.o",
              "bytes": 1628,
              "sha256": "06da623635a8e4a5bb21fcc92aa27a9d86163d5c74425c925d65c353aa93379c"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-bv_533gm/linked.o",
              "bytes": 7524,
              "sha256": "9f5a8b88b0af00e9bb7562e7f10d69aa5dba29701bdba3fd0fe436c7cb36820d"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-bv_533gm/function.bin",
              "bytes": 28,
              "sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/misc3d_reset/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.05 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-114/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.14 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-bv_533gm/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "c7c746990629b777f7000dfa993db4fb93bb27c5898b5d82dfc0a730e5a5a4de",
            "text_sha256": "43e2be8a034f051b91fbede07cb6ff7b033815afa76effaa8c521e4e82135fae",
            "text_bytes": 28,
            "relocations": [
              {
                "offset": 4,
                "type": 7,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 8,
                "type": 7,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 12,
                "type": 7,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 7,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 7,
                "symbol_index": 14,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof."
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-bv_533gm/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-bv_533gm/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-bv_533gm/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-bv_533gm/prepared.o",
            "--defsym=fr2_db_id=0x00290ac4",
            "--defsym=fr2_material_a=0x00290ac8",
            "--defsym=fr2_material_b=0x00290acc",
            "--defsym=fr2_material_c=0x00290ad0",
            "--defsym=fr2_material_d=0x00290ad4",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-bv_533gm/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-bv_533gm/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "actual_bytes": 28,
          "reference_sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "reference_bytes": 28,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "pass",
            "reason": null,
            "matched_bytes": 28,
            "section_bytes": 28
          }
        },
        {
          "id": "ee-gcc2.95.3-136",
          "status": "pass",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/bin/ee-gcc.exe",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "platform": "linux/amd64",
            "runner": "Wine 8 Debian Bookworm on Linux amd64 via Docker Desktop"
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-3l24raku/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1708032,
              "sha256": "0393bcd31f91a6b9f0255db97f1cc99eba78ee8fc003e9a04dfabed1ae1d522e"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "b9c50aa66f9cf5dbd80b2affe9874ec7674b7328965c629476f6ad7c77943154"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "compiler_sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-3l24raku/candidate.o",
              "bytes": 1716,
              "sha256": "c7c746990629b777f7000dfa993db4fb93bb27c5898b5d82dfc0a730e5a5a4de"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-3l24raku/prepared.o",
              "bytes": 1628,
              "sha256": "06da623635a8e4a5bb21fcc92aa27a9d86163d5c74425c925d65c353aa93379c"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-3l24raku/linked.o",
              "bytes": 7524,
              "sha256": "9f5a8b88b0af00e9bb7562e7f10d69aa5dba29701bdba3fd0fe436c7cb36820d"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-3l24raku/function.bin",
              "bytes": 28,
              "sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/misc3d_reset/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.12 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-136/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.36 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-3l24raku/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "c7c746990629b777f7000dfa993db4fb93bb27c5898b5d82dfc0a730e5a5a4de",
            "text_sha256": "43e2be8a034f051b91fbede07cb6ff7b033815afa76effaa8c521e4e82135fae",
            "text_bytes": 28,
            "relocations": [
              {
                "offset": 4,
                "type": 7,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 8,
                "type": 7,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 12,
                "type": 7,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 7,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 7,
                "symbol_index": 14,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof."
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-3l24raku/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-3l24raku/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-3l24raku/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-3l24raku/prepared.o",
            "--defsym=fr2_db_id=0x00290ac4",
            "--defsym=fr2_material_a=0x00290ac8",
            "--defsym=fr2_material_b=0x00290acc",
            "--defsym=fr2_material_c=0x00290ad0",
            "--defsym=fr2_material_d=0x00290ad4",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-3l24raku/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/misc3d_reset/objects/fr2-compiler-probe-3l24raku/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "actual_bytes": 28,
          "reference_sha256": "d31428f0506f37cf1ba8c2e6d374474809fa0c1fa1644124bf83010aef4fc2ce",
          "reference_bytes": 28,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "pass",
            "reason": null,
            "matched_bytes": 28,
            "section_bytes": 28
          }
        }
      ],
      "claim_limits": [
        "A unique match identifies this source/compiler/flags/reference probe only.",
        "It does not establish the original compiler ID without an independently evidenced retail function/reference pair.",
        "This runner executes compiler and objcopy argv from the local manifest."
      ],
      "unit": "misc3d_reset",
      "package_members": [
        {
          "candidate": "ee-gcc2.9-991111-01",
          "archive": "ee-gcc2.9-991111-01.tar.xz",
          "sha256": "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 154155,
              "sha256": "64d0a50fef499da0b98177eb5e79e41dfb066ad44246b137c78a266ef97ee265"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.9-ee-991111-01/cc1",
              "bytes": 4794381,
              "sha256": "b9aef69f93efb949f15ea58189e8eef4a002b9fe4de5d3fcf89c34e1244ec026"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.9-ee-991111-01/cpp",
              "bytes": 241396,
              "sha256": "f85a54d241e019993fa7a06285d3677856b3b431e10318a587ab029373c603d7"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 2210289,
              "sha256": "296af123052ee39d175e5b3254102aafca105d4f6e975b351a13867f59b04019"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.96",
          "archive": "ee-gcc2.96.tar.xz",
          "sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 333402,
              "sha256": "b8c284d16c9c0a0e8788e9522c46881e224ad01fa1c732aed43f821cc32f168b"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.96-ee-001003-1/cc1",
              "bytes": 5526661,
              "sha256": "59ec92b3f9f3513e0633331af304733e3094de30884e662a8cb584a51c1c42b5"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.96-ee-001003-1/cpp0",
              "bytes": 421478,
              "sha256": "f6f6b598f39649edfe171d6da8c7f91d07f2b87c2aeeffffbc5f566bfb1a39a9"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 2169068,
              "sha256": "b8cfdb6ecb6931642914020f92a62e653378f57230eed4895f69afa050d47b5e"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc3.2-030926",
          "archive": "ee-gcc3.2-030926.tar.gz",
          "sha256": "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 335156,
              "sha256": "8ba17b0f2cbcc87b31bb164766bc3e7e340f714adfb518bc4634a6f1ffda8951"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/3.2-ee-030926/cc1",
              "bytes": 9764536,
              "sha256": "da4fec4d48d91e62fd968f76acb16981dd8131d02f27c1b7559f0e903b590eb6"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/3.2-ee-030926/cpp0",
              "bytes": 703785,
              "sha256": "2d1a4b260e143a8b467bb7609cb3fd60ae541174ffff78d922feb2d7fbb0e218"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 5887159,
              "sha256": "d04424acb1359b31b3ad138f8d17876623ffe9182497ff4516055b71f22bf2fa"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc3.2-040921",
          "archive": "ee-gcc3.2-040921.tar.xz",
          "sha256": "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 265116,
              "sha256": "a5095b5d7b55f91535b12e48e9d808170fa9fb8c0620c43c2fb61379b1a3663a"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/3.2-ee-040921/cc1",
              "bytes": 7201720,
              "sha256": "0bcc90bd23e10698e75047db9a84ea47e753791115fdd23d6f637a544f6d257d"
            },
            "cpp": {
              "member": "bin/ee-cpp",
              "bytes": 266763,
              "sha256": "ed76fe8e08c13c749d59a458d21c912567b10e5e01bff028a4147debd56d15e6"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 3706255,
              "sha256": "cf85edec3ea30b0918e8a78ac49affca111a45e5b0ca9a776b6ded5c0118379b"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.95.2-273a",
          "archive": "ee-gcc2.95.2-273a.tar.gz",
          "sha256": "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e",
          "members": {
            "driver": {
              "member": "bin/ee-gcc.exe",
              "bytes": 122880,
              "sha256": "ab787f9bda2531e116f420eec639e7d34bcc92caf4eb8d3dc71fefddffd3fcfc"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.95.2/cc1.exe",
              "bytes": 1773568,
              "sha256": "2aaf3d22ce5c3508ecba15f16b06737713263e6aee289ca1e43d3ff9c17d964f"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.95.2/cpp.exe",
              "bytes": 110592,
              "sha256": "f7db993de8745339ec71cf10d5fe9e7772d75e79a037e97809ed5e34ea3150c3"
            },
            "gnu_assembler": {
              "member": "lib/gcc-lib/ee/2.95.2/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "member": "lib/gcc-lib/ee/2.95.2/specs",
              "bytes": 4260,
              "sha256": "372d6255779b9214f7f980a8289461209c9be4cb12a91c6b4e01e14c0f91070c"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.95.3-114",
          "archive": "ee-gcc2.95.3-114.tar.gz",
          "sha256": "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb",
          "members": {
            "driver": {
              "member": "bin/ee-gcc.exe",
              "bytes": 122880,
              "sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1654784,
              "sha256": "7bccdee8d6cc6bc56a84824cadb9c5ce546a1aa7f9b836447d2482408c5c5832"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "271e9a55b782153acf303566c93c18ea30253e9c14d4df4daa55c521ead92eef"
            },
            "gnu_assembler": {
              "member": "lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "member": "lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.95.3-136",
          "archive": "ee-gcc2.95.3-136.tar.gz",
          "sha256": "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f",
          "members": {
            "driver": {
              "member": "bin/ee-gcc.exe",
              "bytes": 122880,
              "sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1708032,
              "sha256": "0393bcd31f91a6b9f0255db97f1cc99eba78ee8fc003e9a04dfabed1ae1d522e"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "b9c50aa66f9cf5dbd80b2affe9874ec7674b7328965c629476f6ad7c77943154"
            },
            "gnu_assembler": {
              "member": "lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "member": "lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        }
      ],
      "package_identity_status": "pass"
    },
    {
      "status": "pass",
      "selected_id": "ee-gcc2.96",
      "matches": [
        "ee-gcc2.96"
      ],
      "failures": [
        "ee-gcc2.9-991111-01",
        "ee-gcc3.2-030926",
        "ee-gcc3.2-040921",
        "ee-gcc2.95.2-273a",
        "ee-gcc2.95.3-114",
        "ee-gcc2.95.3-136"
      ],
      "errors": [],
      "incomplete": [],
      "manifest": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/manifest.json",
        "bytes": 29167,
        "sha256": "562ee45813f069b96248af7f29cd7f3499f041fb52e436f19e002716b412b01b"
      },
      "evidence": {
        "corpus": {
          "profile": "fr2-pal-sles-517.05",
          "sources": {
            "ford-racing-2.bin": {
              "bytes": 678667248,
              "sha256": "ae8d5a32c9d832f34a08fad6f0e97ce6e89e6b040597011f6362d886145b9d3d"
            },
            "ford-racing-2.cue": {
              "bytes": 79,
              "sha256": "c2e0aaf75a43150567f4ffe02ac863c8d1bda8f2fdf744012361436ec582edb6"
            },
            "extracted/SLES_517.05": {
              "bytes": 1662804,
              "sha256": "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95"
            },
            "extracted/FILES.HDR": {
              "bytes": 29428,
              "sha256": "f4e4a4f91cd89bcaa8c2772e6cba2a839d92fbe222290c8c751777a81963731d"
            },
            "extracted/FILES.DAT": {
              "bytes": 334641152,
              "sha256": "357fc371f47e366bf507b721e26eed9f1205516c19b793e0316ccecc2175a722"
            }
          },
          "corpus_id": "e69a2afbd6db606d166e40bae32c436691e134722ad153200859961a5f517dab"
        },
        "reference_range": {
          "section": ".text",
          "vaddr": "0018bba8",
          "bytes": 60,
          "file_offset": "0008cba8",
          "sha256": "dde62359047f7cee35cce6202e4b709aacb19c26f86a3797e451b398fe18579d",
          "scope": "mixed"
        },
        "candidate_source": "Hand-written exploratory reconstruction; inferred names, ABI and ownership; not original source.",
        "tool_source": "decompme/compilers release tag compilers; per-candidate archive URLs and SHA-256 values follow.",
        "tool_distributions": [
          {
            "candidate": "ee-gcc2.9-991111-01",
            "archive": "ee-gcc2.9-991111-01.tar.xz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.9-991111-01.tar.xz",
            "expected_sha256": "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8",
            "available_locally": true,
            "observed_sha256": "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8"
          },
          {
            "candidate": "ee-gcc2.95.2-273a",
            "archive": "ee-gcc2.95.2-273a.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.2-273a.tar.gz",
            "expected_sha256": "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e",
            "available_locally": true,
            "observed_sha256": "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e"
          },
          {
            "candidate": "ee-gcc2.95.3-114",
            "archive": "ee-gcc2.95.3-114.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.3-114.tar.gz",
            "expected_sha256": "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb",
            "available_locally": true,
            "observed_sha256": "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb"
          },
          {
            "candidate": "ee-gcc2.95.3-136",
            "archive": "ee-gcc2.95.3-136.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.3-136.tar.gz",
            "expected_sha256": "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f",
            "available_locally": true,
            "observed_sha256": "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f"
          },
          {
            "candidate": "ee-gcc2.96",
            "archive": "ee-gcc2.96.tar.xz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.96.tar.xz",
            "expected_sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a",
            "available_locally": true,
            "observed_sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a"
          },
          {
            "candidate": "ee-gcc3.2-030926",
            "archive": "ee-gcc3.2-030926.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-030926.tar.gz",
            "expected_sha256": "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9",
            "available_locally": true,
            "observed_sha256": "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9"
          },
          {
            "candidate": "ee-gcc3.2-040921",
            "archive": "ee-gcc3.2-040921.tar.xz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-040921.tar.xz",
            "expected_sha256": "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f",
            "available_locally": true,
            "observed_sha256": "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f"
          }
        ],
        "license_status": "The release archives inspected do not include COPYING or LICENSE entries. Per-package redistribution terms are unresolved; no compiler binaries are redistributed here.",
        "runtime_profile": "Immutable image IDs are verified before invocation: Debian Bookworm linux/amd64 with Wine 8 for Windows compiler drivers, and GNU binutils 2.40 in the Debian image for object preparation, linking, and objcopy.",
        "linker_profile": "GNU binutils 2.40 substitution; not the original proprietary linker.",
        "independent_unit": {
          "id": "entity_set_first",
          "symbol": "fr2_entity_set_first",
          "source": "tools/compiler_probe_recipe/entity_set_first.c",
          "source_sha256": "92f4fe16d604fce7638e7a056d0db1bd60ff8f0cceb034f8fbfaec68f6cdf99e",
          "vaddr": "0018bba8",
          "bytes": 60,
          "sha256": "dde62359047f7cee35cce6202e4b709aacb19c26f86a3797e451b398fe18579d",
          "definitions": {
            "fr2_entity_error": "001b0770",
            "fr2_set_first_file": "0025eba8"
          },
          "source_path": "../fr2/source/entity/system/en_funcs/en_list/set_frst.h",
          "independent_basis": "Direct source-path reference at 0018bbd4 and line 290. Kind 22 selects a payload pointer at +4 and a store at +0; other kinds call a separately located diagnostic. No saved direct caller in the retained inventory. The contiguous probe includes the return delay slot through 0018bbe3. The inventory sum (56) excludes a four-byte alignment hole and is not a contiguous extent.",
          "distinguishes": "Argument ABI, conditional store, error-call scheduling and stack/return convention.",
          "static_callers": [],
          "body_ranges": [
            {
              "start": "0018bba8",
              "end": "0018bbbb"
            },
            {
              "start": "0018bbbc",
              "end": "0018bbc3"
            },
            {
              "start": "0018bbc8",
              "end": "0018bbd7"
            },
            {
              "start": "0018bbd8",
              "end": "0018bbe3"
            }
          ],
          "claim_limit": "Hand-written inference from independent static evidence; names/types are provisional; no original-source, execution or owned-byte credit."
        }
      },
      "source": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.c",
        "bytes": 551,
        "sha256": "92f4fe16d604fce7638e7a056d0db1bd60ff8f0cceb034f8fbfaec68f6cdf99e"
      },
      "reference": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/reference.bin",
        "bytes": 60,
        "sha256": "dde62359047f7cee35cce6202e4b709aacb19c26f86a3797e451b398fe18579d"
      },
      "symbol": "fr2_entity_set_first",
      "candidates": [
        {
          "id": "ee-gcc2.9-991111-01",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/bin/ee-gcc",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-b2v5lfjf/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/lib/gcc-lib/ee/2.9-ee-991111-01/cc1",
              "bytes": 4794381,
              "sha256": "b9aef69f93efb949f15ea58189e8eef4a002b9fe4de5d3fcf89c34e1244ec026"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/lib/gcc-lib/ee/2.9-ee-991111-01/cpp",
              "bytes": 241396,
              "sha256": "f85a54d241e019993fa7a06285d3677856b3b431e10318a587ab029373c603d7"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/ee/bin/as",
              "bytes": 2210289,
              "sha256": "296af123052ee39d175e5b3254102aafca105d4f6e975b351a13867f59b04019"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "64d0a50fef499da0b98177eb5e79e41dfb066ad44246b137c78a266ef97ee265",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-b2v5lfjf/candidate.o",
              "bytes": 1576,
              "sha256": "f4709e430073100d7246f138a4a9be8333c0c8ac0f924d6932cc71203e48f984"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-b2v5lfjf/prepared.o",
              "bytes": 1484,
              "sha256": "77ae83da8a02c5a7a46276b25a5b317dc19899036ef07e352a9be8c30a26f5f9"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-b2v5lfjf/linked.o",
              "bytes": 49372,
              "sha256": "7c842f6bdf66863ef7bed98ce3e50a83fd21b7871cf7b6789fd0f76948b367ab"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-b2v5lfjf/function.bin",
              "bytes": 36,
              "sha256": "17bb261925cb927c8af4d6235e3f200337794af64fbaec3b8b7ce2a7f0408b4c"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Using builtin specs.\ngcc version 2.9-ee-991111-01\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/cc1 /tools/compiler-profile-if5l6kuy/entity_set_first/candidate.c -G8 -lang-c -iprefix /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/ -quiet -dumpbase candidate.c -undef -D__GNUC__=2 -D__GNUC_MINOR__=9 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float -version -ffunction-sections -O2 -o /tmp/ccvqBjse.s\nGNU C version 2.9-ee-991111-01 (ee) compiled by GNU C version 2.7.2.3.\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/../../../../ee/bin/as -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-b2v5lfjf/candidate.o /tmp/ccvqBjse.s\nGNU assembler version 2.9-ee-991111 (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "f4709e430073100d7246f138a4a9be8333c0c8ac0f924d6932cc71203e48f984",
            "text_sha256": "51777bdc57d2c470fe936001dfd3a33aaddee7d3e59fa0651a7e288ac98f45c4",
            "text_bytes": 36,
            "relocations": [
              {
                "offset": 20,
                "type": 4,
                "symbol_index": 11,
                "mask": "03ffffff"
              },
              {
                "offset": 12,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 36,
              "reason": "function length differs",
              "expected_bytes": 60,
              "actual_bytes": 36
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-b2v5lfjf/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-b2v5lfjf/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-b2v5lfjf/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-b2v5lfjf/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-b2v5lfjf/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-b2v5lfjf/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "17bb261925cb927c8af4d6235e3f200337794af64fbaec3b8b7ce2a7f0408b4c",
          "actual_bytes": 36,
          "reference_sha256": "dde62359047f7cee35cce6202e4b709aacb19c26f86a3797e451b398fe18579d",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 60,
            "first_difference": {
              "offset": 0,
              "address": "0018bba8",
              "file_offset": "0008cba8",
              "word": 0,
              "expected": "f0ffbd27",
              "actual": "16000224"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.96",
          "status": "pass",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-ajrfdg0i/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/cc1",
              "bytes": 5526661,
              "sha256": "59ec92b3f9f3513e0633331af304733e3094de30884e662a8cb584a51c1c42b5"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/cpp0",
              "bytes": 421478,
              "sha256": "f6f6b598f39649edfe171d6da8c7f91d07f2b87c2aeeffffbc5f566bfb1a39a9"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/ee/bin/as",
              "bytes": 2169068,
              "sha256": "b8cfdb6ecb6931642914020f92a62e653378f57230eed4895f69afa050d47b5e"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "b8c284d16c9c0a0e8788e9522c46881e224ad01fa1c732aed43f821cc32f168b",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-ajrfdg0i/candidate.o",
              "bytes": 1744,
              "sha256": "7630fb5473f52cb6c574986b80a7bf0fabd1cd60a90dc2ab44cd81fb217267da"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-ajrfdg0i/prepared.o",
              "bytes": 1580,
              "sha256": "2e4802ce489e1fddf85d4ea057edea4043028956affcea4941a479db41143b00"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-ajrfdg0i/linked.o",
              "bytes": 49396,
              "sha256": "68e03cf42be37fc4f50438269fa80b948fa1fc31b32823c7b5d2e0a7bbbfb081"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-ajrfdg0i/function.bin",
              "bytes": 60,
              "sha256": "dde62359047f7cee35cce6202e4b709aacb19c26f86a3797e451b398fe18579d"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Using builtin specs.\ngcc version 2.96-ee-001003-1\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/ -D__GNUC__=2 -D__GNUC_MINOR__=96 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/entity_set_first/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccgar4ZE.s\nGNU CPP version 2.96-ee-001003-1 (cpplib)\n [AL 1.1, MM 40] BSD Mips\nGNU C version 2.96-ee-001003-1 (ee) compiled by GNU C version 2.9-gnupro-99r1.\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/sys-include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/sys-include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/../../../../ee/bin/as -G8 -EL -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-ajrfdg0i/candidate.o /tmp/ccgar4ZE.s\nGNU assembler version 2.10-ee-001003-1 (ee) using BFD version 2.10-ee-001003\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "7630fb5473f52cb6c574986b80a7bf0fabd1cd60a90dc2ab44cd81fb217267da",
            "text_sha256": "d9aa828c8869512910d84a697abc0d5879202da0c46e3e40b53f1e15f1b3376a",
            "text_bytes": 60,
            "relocations": [
              {
                "offset": 40,
                "type": 4,
                "symbol_index": 12,
                "mask": "03ffffff"
              },
              {
                "offset": 32,
                "type": 5,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 44,
                "type": 6,
                "symbol_index": 11,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof."
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-ajrfdg0i/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-ajrfdg0i/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-ajrfdg0i/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-ajrfdg0i/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-ajrfdg0i/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-ajrfdg0i/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "dde62359047f7cee35cce6202e4b709aacb19c26f86a3797e451b398fe18579d",
          "actual_bytes": 60,
          "reference_sha256": "dde62359047f7cee35cce6202e4b709aacb19c26f86a3797e451b398fe18579d",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "pass",
            "reason": null,
            "matched_bytes": 60,
            "section_bytes": 60
          }
        },
        {
          "id": "ee-gcc3.2-030926",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-eo_vfw7l/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/cc1",
              "bytes": 9764536,
              "sha256": "da4fec4d48d91e62fd968f76acb16981dd8131d02f27c1b7559f0e903b590eb6"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/cpp0",
              "bytes": 703785,
              "sha256": "2d1a4b260e143a8b467bb7609cb3fd60ae541174ffff78d922feb2d7fbb0e218"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/ee/bin/as",
              "bytes": 5887159,
              "sha256": "d04424acb1359b31b3ad138f8d17876623ffe9182497ff4516055b71f22bf2fa"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "8ba17b0f2cbcc87b31bb164766bc3e7e340f714adfb518bc4634a6f1ffda8951",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-eo_vfw7l/candidate.o",
              "bytes": 1464,
              "sha256": "b40ec80f3c3501f148e89354bb3ed5aca9893d0aad6b52d6cb616850dab2ecb6"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-eo_vfw7l/prepared.o",
              "bytes": 1464,
              "sha256": "20dccab438b5e4ab3023a5f2ae904349f30950d40ade6b29db040a37bb22aeb9"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-eo_vfw7l/linked.o",
              "bytes": 49344,
              "sha256": "0fa5f408dd73ec91321b2e89efe25fbdec71376bc351b222c460dd16999d1424"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-eo_vfw7l/function.bin",
              "bytes": 64,
              "sha256": "2619143e440401fbfca4e274446f6226742203bac5df5cc4abd014f70bd10fd8"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Reading specs from /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/specs\nConfigured with: /proj/ee-toolchain/ee-gcc-3.2-final-rc2/release-src/ee-gcc/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-030926\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/entity_set_first/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccD7CJSg.s\nGNU CPP version 3.2-ee-030926 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-030926 (ee)\n\tcompiled by GNU C version 3.2.\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-eo_vfw7l/candidate.o /tmp/ccD7CJSg.s\nGNU assembler version 2.12-ee-030926 (ee) using BFD version 2.12-ee-030926 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "b40ec80f3c3501f148e89354bb3ed5aca9893d0aad6b52d6cb616850dab2ecb6",
            "text_sha256": "dbd6699756cceb22122382531b83da7831aa547fdc62e61a135733ef1c6af8fb",
            "text_bytes": 64,
            "relocations": [
              {
                "offset": 44,
                "type": 4,
                "symbol_index": 10,
                "mask": "03ffffff"
              },
              {
                "offset": 36,
                "type": 5,
                "symbol_index": 9,
                "mask": "0000ffff"
              },
              {
                "offset": 48,
                "type": 6,
                "symbol_index": 9,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 60,
              "reason": "function length differs",
              "expected_bytes": 60,
              "actual_bytes": 64
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-eo_vfw7l/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-eo_vfw7l/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-eo_vfw7l/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-eo_vfw7l/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-eo_vfw7l/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-eo_vfw7l/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "2619143e440401fbfca4e274446f6226742203bac5df5cc4abd014f70bd10fd8",
          "actual_bytes": 64,
          "reference_sha256": "dde62359047f7cee35cce6202e4b709aacb19c26f86a3797e451b398fe18579d",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 4,
            "section_bytes": 60,
            "first_difference": {
              "offset": 4,
              "address": "0018bbac",
              "file_offset": "0008cbac",
              "word": 1,
              "expected": "16000224",
              "actual": "16000f24"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc3.2-040921",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-a41c2c7p/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1",
              "bytes": 7201720,
              "sha256": "0bcc90bd23e10698e75047db9a84ea47e753791115fdd23d6f637a544f6d257d"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-cpp",
              "bytes": 266763,
              "sha256": "ed76fe8e08c13c749d59a458d21c912567b10e5e01bff028a4147debd56d15e6"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/ee/bin/as",
              "bytes": 3706255,
              "sha256": "cf85edec3ea30b0918e8a78ac49affca111a45e5b0ca9a776b6ded5c0118379b"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "a5095b5d7b55f91535b12e48e9d808170fa9fb8c0620c43c2fb61379b1a3663a",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-a41c2c7p/candidate.o",
              "bytes": 1464,
              "sha256": "b40ec80f3c3501f148e89354bb3ed5aca9893d0aad6b52d6cb616850dab2ecb6"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-a41c2c7p/prepared.o",
              "bytes": 1464,
              "sha256": "20dccab438b5e4ab3023a5f2ae904349f30950d40ade6b29db040a37bb22aeb9"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-a41c2c7p/linked.o",
              "bytes": 49344,
              "sha256": "0fa5f408dd73ec91321b2e89efe25fbdec71376bc351b222c460dd16999d1424"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-a41c2c7p/function.bin",
              "bytes": 64,
              "sha256": "2619143e440401fbfca4e274446f6226742203bac5df5cc4abd014f70bd10fd8"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Using built-in specs.\nConfigured with: ../src/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-040921\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/entity_set_first/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccUFwLEM.s\nGNU CPP version 3.2-ee-040921 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-040921 (ee)\n\tcompiled by GNU C version 3.2.2 20030222 (Red Hat Linux 3.2.2-5).\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-a41c2c7p/candidate.o /tmp/ccUFwLEM.s\nGNU assembler version 2.12-ee-040921 (ee) using BFD version 2.12-ee-040921 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "b40ec80f3c3501f148e89354bb3ed5aca9893d0aad6b52d6cb616850dab2ecb6",
            "text_sha256": "dbd6699756cceb22122382531b83da7831aa547fdc62e61a135733ef1c6af8fb",
            "text_bytes": 64,
            "relocations": [
              {
                "offset": 44,
                "type": 4,
                "symbol_index": 10,
                "mask": "03ffffff"
              },
              {
                "offset": 36,
                "type": 5,
                "symbol_index": 9,
                "mask": "0000ffff"
              },
              {
                "offset": 48,
                "type": 6,
                "symbol_index": 9,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 60,
              "reason": "function length differs",
              "expected_bytes": 60,
              "actual_bytes": 64
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-a41c2c7p/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-a41c2c7p/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-a41c2c7p/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-a41c2c7p/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-a41c2c7p/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-a41c2c7p/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "2619143e440401fbfca4e274446f6226742203bac5df5cc4abd014f70bd10fd8",
          "actual_bytes": 64,
          "reference_sha256": "dde62359047f7cee35cce6202e4b709aacb19c26f86a3797e451b398fe18579d",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 4,
            "section_bytes": 60,
            "first_difference": {
              "offset": 4,
              "address": "0018bbac",
              "file_offset": "0008cbac",
              "word": 1,
              "expected": "16000224",
              "actual": "16000f24"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.95.2-273a",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/bin/ee-gcc.exe",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "platform": "linux/amd64",
            "runner": "Wine 8 Debian Bookworm on Linux amd64 via Docker Desktop"
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-x1dww2ns/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/cc1.exe",
              "bytes": 1773568,
              "sha256": "2aaf3d22ce5c3508ecba15f16b06737713263e6aee289ca1e43d3ff9c17d964f"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/cpp.exe",
              "bytes": 110592,
              "sha256": "f7db993de8745339ec71cf10d5fe9e7772d75e79a037e97809ed5e34ea3150c3"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/specs",
              "bytes": 4260,
              "sha256": "372d6255779b9214f7f980a8289461209c9be4cb12a91c6b4e01e14c0f91070c"
            }
          },
          "compiler_sha256": "ab787f9bda2531e116f420eec639e7d34bcc92caf4eb8d3dc71fefddffd3fcfc",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-x1dww2ns/candidate.o",
              "bytes": 1596,
              "sha256": "9dbdea63852f188375bfc5db28be4b71d8952518486437041afbb698eee2cb51"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-x1dww2ns/prepared.o",
              "bytes": 1504,
              "sha256": "df4fadcdf4c1d11c9440b6adae38979d391530b45aeaa2e3691ef6cf6ee115f8"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-x1dww2ns/linked.o",
              "bytes": 49392,
              "sha256": "294f82d91b13e22b3b950f6cf8f144ee5d0e3d13f52f53425fa7e3cbc63ba2f3"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-x1dww2ns/function.bin",
              "bytes": 56,
              "sha256": "df1a7f25e9a66c1fb292ce07ceef9a28c9032323788b4f7efffefdf2b66c083a"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.2-EE\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/entity_set_first/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.2 v2 [AL 1.1, MM 40] BSD Mips\n#include \"...\" search starts here:\nEnd of search list.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.2 SN BUILD v2.73a for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-x1dww2ns/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "9dbdea63852f188375bfc5db28be4b71d8952518486437041afbb698eee2cb51",
            "text_sha256": "e6130e6b15fb311391e874235908ef3336265c469a30b7ec33249e5c96471d53",
            "text_bytes": 56,
            "relocations": [
              {
                "offset": 36,
                "type": 4,
                "symbol_index": 11,
                "mask": "03ffffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 40,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 56,
              "reason": "function length differs",
              "expected_bytes": 60,
              "actual_bytes": 56
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-x1dww2ns/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-x1dww2ns/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-x1dww2ns/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-x1dww2ns/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-x1dww2ns/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-x1dww2ns/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "df1a7f25e9a66c1fb292ce07ceef9a28c9032323788b4f7efffefdf2b66c083a",
          "actual_bytes": 56,
          "reference_sha256": "dde62359047f7cee35cce6202e4b709aacb19c26f86a3797e451b398fe18579d",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 8,
            "section_bytes": 60,
            "first_difference": {
              "offset": 8,
              "address": "0018bbb0",
              "file_offset": "0008cbb0",
              "word": 2,
              "expected": "0000bfff",
              "actual": "0000bf7f"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.95.3-114",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/bin/ee-gcc.exe",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "platform": "linux/amd64",
            "runner": "Wine 8 Debian Bookworm on Linux amd64 via Docker Desktop"
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-3eu2e892/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1654784,
              "sha256": "7bccdee8d6cc6bc56a84824cadb9c5ce546a1aa7f9b836447d2482408c5c5832"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "271e9a55b782153acf303566c93c18ea30253e9c14d4df4daa55c521ead92eef"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "compiler_sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-3eu2e892/candidate.o",
              "bytes": 1596,
              "sha256": "9dbdea63852f188375bfc5db28be4b71d8952518486437041afbb698eee2cb51"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-3eu2e892/prepared.o",
              "bytes": 1504,
              "sha256": "df4fadcdf4c1d11c9440b6adae38979d391530b45aeaa2e3691ef6cf6ee115f8"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-3eu2e892/linked.o",
              "bytes": 49392,
              "sha256": "294f82d91b13e22b3b950f6cf8f144ee5d0e3d13f52f53425fa7e3cbc63ba2f3"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-3eu2e892/function.bin",
              "bytes": 56,
              "sha256": "df1a7f25e9a66c1fb292ce07ceef9a28c9032323788b4f7efffefdf2b66c083a"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/entity_set_first/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.05 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-114/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.14 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-3eu2e892/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "9dbdea63852f188375bfc5db28be4b71d8952518486437041afbb698eee2cb51",
            "text_sha256": "e6130e6b15fb311391e874235908ef3336265c469a30b7ec33249e5c96471d53",
            "text_bytes": 56,
            "relocations": [
              {
                "offset": 36,
                "type": 4,
                "symbol_index": 11,
                "mask": "03ffffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 40,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 56,
              "reason": "function length differs",
              "expected_bytes": 60,
              "actual_bytes": 56
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-3eu2e892/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-3eu2e892/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-3eu2e892/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-3eu2e892/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-3eu2e892/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-3eu2e892/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "df1a7f25e9a66c1fb292ce07ceef9a28c9032323788b4f7efffefdf2b66c083a",
          "actual_bytes": 56,
          "reference_sha256": "dde62359047f7cee35cce6202e4b709aacb19c26f86a3797e451b398fe18579d",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 8,
            "section_bytes": 60,
            "first_difference": {
              "offset": 8,
              "address": "0018bbb0",
              "file_offset": "0008cbb0",
              "word": 2,
              "expected": "0000bfff",
              "actual": "0000bf7f"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.95.3-136",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/bin/ee-gcc.exe",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "platform": "linux/amd64",
            "runner": "Wine 8 Debian Bookworm on Linux amd64 via Docker Desktop"
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-z9h07i03/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1708032,
              "sha256": "0393bcd31f91a6b9f0255db97f1cc99eba78ee8fc003e9a04dfabed1ae1d522e"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "b9c50aa66f9cf5dbd80b2affe9874ec7674b7328965c629476f6ad7c77943154"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "compiler_sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-z9h07i03/candidate.o",
              "bytes": 1596,
              "sha256": "5af3190d5218839b9c9603e3d909e2835c7cf58f1903791f13e299bb40e4d6ab"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-z9h07i03/prepared.o",
              "bytes": 1504,
              "sha256": "42d1979f99a94d052fdceae5b1997800cc827b7c1bdb7384c41fa243b7649494"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-z9h07i03/linked.o",
              "bytes": 49392,
              "sha256": "d28c49a66340b95d547fc9966b162ad2da22f1c7e186ecc9aab2a458f65994ae"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-z9h07i03/function.bin",
              "bytes": 56,
              "sha256": "be97e51cbe9d94980c249d3c91cfa76fcc05de5724999e3debfe379ea67662cc"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/entity_set_first/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.12 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-136/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.36 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-z9h07i03/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "5af3190d5218839b9c9603e3d909e2835c7cf58f1903791f13e299bb40e4d6ab",
            "text_sha256": "72b09dcf09c73131e2ad13b5b95add18745041b14ae8c933a6b90651ad983f45",
            "text_bytes": 56,
            "relocations": [
              {
                "offset": 36,
                "type": 4,
                "symbol_index": 11,
                "mask": "03ffffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 40,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 56,
              "reason": "function length differs",
              "expected_bytes": 60,
              "actual_bytes": 56
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-z9h07i03/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-z9h07i03/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-z9h07i03/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-z9h07i03/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-z9h07i03/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/entity_set_first/objects/fr2-compiler-probe-z9h07i03/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "be97e51cbe9d94980c249d3c91cfa76fcc05de5724999e3debfe379ea67662cc",
          "actual_bytes": 56,
          "reference_sha256": "dde62359047f7cee35cce6202e4b709aacb19c26f86a3797e451b398fe18579d",
          "reference_bytes": 60,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 12,
            "section_bytes": 60,
            "first_difference": {
              "offset": 12,
              "address": "0018bbb4",
              "file_offset": "0008cbb4",
              "word": 3,
              "expected": "0400a214",
              "actual": "0300a214"
            }
          },
          "reason": "function bytes differ"
        }
      ],
      "claim_limits": [
        "A unique match identifies this source/compiler/flags/reference probe only.",
        "It does not establish the original compiler ID without an independently evidenced retail function/reference pair.",
        "This runner executes compiler and objcopy argv from the local manifest."
      ],
      "unit": "entity_set_first",
      "package_members": [
        {
          "candidate": "ee-gcc2.9-991111-01",
          "archive": "ee-gcc2.9-991111-01.tar.xz",
          "sha256": "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 154155,
              "sha256": "64d0a50fef499da0b98177eb5e79e41dfb066ad44246b137c78a266ef97ee265"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.9-ee-991111-01/cc1",
              "bytes": 4794381,
              "sha256": "b9aef69f93efb949f15ea58189e8eef4a002b9fe4de5d3fcf89c34e1244ec026"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.9-ee-991111-01/cpp",
              "bytes": 241396,
              "sha256": "f85a54d241e019993fa7a06285d3677856b3b431e10318a587ab029373c603d7"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 2210289,
              "sha256": "296af123052ee39d175e5b3254102aafca105d4f6e975b351a13867f59b04019"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.96",
          "archive": "ee-gcc2.96.tar.xz",
          "sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 333402,
              "sha256": "b8c284d16c9c0a0e8788e9522c46881e224ad01fa1c732aed43f821cc32f168b"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.96-ee-001003-1/cc1",
              "bytes": 5526661,
              "sha256": "59ec92b3f9f3513e0633331af304733e3094de30884e662a8cb584a51c1c42b5"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.96-ee-001003-1/cpp0",
              "bytes": 421478,
              "sha256": "f6f6b598f39649edfe171d6da8c7f91d07f2b87c2aeeffffbc5f566bfb1a39a9"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 2169068,
              "sha256": "b8cfdb6ecb6931642914020f92a62e653378f57230eed4895f69afa050d47b5e"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc3.2-030926",
          "archive": "ee-gcc3.2-030926.tar.gz",
          "sha256": "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 335156,
              "sha256": "8ba17b0f2cbcc87b31bb164766bc3e7e340f714adfb518bc4634a6f1ffda8951"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/3.2-ee-030926/cc1",
              "bytes": 9764536,
              "sha256": "da4fec4d48d91e62fd968f76acb16981dd8131d02f27c1b7559f0e903b590eb6"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/3.2-ee-030926/cpp0",
              "bytes": 703785,
              "sha256": "2d1a4b260e143a8b467bb7609cb3fd60ae541174ffff78d922feb2d7fbb0e218"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 5887159,
              "sha256": "d04424acb1359b31b3ad138f8d17876623ffe9182497ff4516055b71f22bf2fa"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc3.2-040921",
          "archive": "ee-gcc3.2-040921.tar.xz",
          "sha256": "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 265116,
              "sha256": "a5095b5d7b55f91535b12e48e9d808170fa9fb8c0620c43c2fb61379b1a3663a"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/3.2-ee-040921/cc1",
              "bytes": 7201720,
              "sha256": "0bcc90bd23e10698e75047db9a84ea47e753791115fdd23d6f637a544f6d257d"
            },
            "cpp": {
              "member": "bin/ee-cpp",
              "bytes": 266763,
              "sha256": "ed76fe8e08c13c749d59a458d21c912567b10e5e01bff028a4147debd56d15e6"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 3706255,
              "sha256": "cf85edec3ea30b0918e8a78ac49affca111a45e5b0ca9a776b6ded5c0118379b"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.95.2-273a",
          "archive": "ee-gcc2.95.2-273a.tar.gz",
          "sha256": "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e",
          "members": {
            "driver": {
              "member": "bin/ee-gcc.exe",
              "bytes": 122880,
              "sha256": "ab787f9bda2531e116f420eec639e7d34bcc92caf4eb8d3dc71fefddffd3fcfc"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.95.2/cc1.exe",
              "bytes": 1773568,
              "sha256": "2aaf3d22ce5c3508ecba15f16b06737713263e6aee289ca1e43d3ff9c17d964f"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.95.2/cpp.exe",
              "bytes": 110592,
              "sha256": "f7db993de8745339ec71cf10d5fe9e7772d75e79a037e97809ed5e34ea3150c3"
            },
            "gnu_assembler": {
              "member": "lib/gcc-lib/ee/2.95.2/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "member": "lib/gcc-lib/ee/2.95.2/specs",
              "bytes": 4260,
              "sha256": "372d6255779b9214f7f980a8289461209c9be4cb12a91c6b4e01e14c0f91070c"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.95.3-114",
          "archive": "ee-gcc2.95.3-114.tar.gz",
          "sha256": "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb",
          "members": {
            "driver": {
              "member": "bin/ee-gcc.exe",
              "bytes": 122880,
              "sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1654784,
              "sha256": "7bccdee8d6cc6bc56a84824cadb9c5ce546a1aa7f9b836447d2482408c5c5832"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "271e9a55b782153acf303566c93c18ea30253e9c14d4df4daa55c521ead92eef"
            },
            "gnu_assembler": {
              "member": "lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "member": "lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.95.3-136",
          "archive": "ee-gcc2.95.3-136.tar.gz",
          "sha256": "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f",
          "members": {
            "driver": {
              "member": "bin/ee-gcc.exe",
              "bytes": 122880,
              "sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1708032,
              "sha256": "0393bcd31f91a6b9f0255db97f1cc99eba78ee8fc003e9a04dfabed1ae1d522e"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "b9c50aa66f9cf5dbd80b2affe9874ec7674b7328965c629476f6ad7c77943154"
            },
            "gnu_assembler": {
              "member": "lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "member": "lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        }
      ],
      "package_identity_status": "pass"
    },
    {
      "status": "pass",
      "selected_id": "ee-gcc2.96",
      "matches": [
        "ee-gcc2.96"
      ],
      "failures": [
        "ee-gcc2.9-991111-01",
        "ee-gcc3.2-030926",
        "ee-gcc3.2-040921",
        "ee-gcc2.95.2-273a",
        "ee-gcc2.95.3-114",
        "ee-gcc2.95.3-136"
      ],
      "errors": [],
      "incomplete": [],
      "manifest": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/manifest.json",
        "bytes": 29644,
        "sha256": "454f44f5fab567050778f52c6b2c8e568a7722d031e15329ff1738377a043684"
      },
      "evidence": {
        "corpus": {
          "profile": "fr2-pal-sles-517.05",
          "sources": {
            "ford-racing-2.bin": {
              "bytes": 678667248,
              "sha256": "ae8d5a32c9d832f34a08fad6f0e97ce6e89e6b040597011f6362d886145b9d3d"
            },
            "ford-racing-2.cue": {
              "bytes": 79,
              "sha256": "c2e0aaf75a43150567f4ffe02ac863c8d1bda8f2fdf744012361436ec582edb6"
            },
            "extracted/SLES_517.05": {
              "bytes": 1662804,
              "sha256": "216711210898aee296eed73d0776e7f733bac04c334002683bce769c86beea95"
            },
            "extracted/FILES.HDR": {
              "bytes": 29428,
              "sha256": "f4e4a4f91cd89bcaa8c2772e6cba2a839d92fbe222290c8c751777a81963731d"
            },
            "extracted/FILES.DAT": {
              "bytes": 334641152,
              "sha256": "357fc371f47e366bf507b721e26eed9f1205516c19b793e0316ccecc2175a722"
            }
          },
          "corpus_id": "e69a2afbd6db606d166e40bae32c436691e134722ad153200859961a5f517dab"
        },
        "reference_range": {
          "section": ".text",
          "vaddr": "0018b840",
          "bytes": 80,
          "file_offset": "0008c840",
          "sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "scope": "mixed"
        },
        "candidate_source": "Hand-written exploratory reconstruction; inferred names, ABI and ownership; not original source.",
        "tool_source": "decompme/compilers release tag compilers; per-candidate archive URLs and SHA-256 values follow.",
        "tool_distributions": [
          {
            "candidate": "ee-gcc2.9-991111-01",
            "archive": "ee-gcc2.9-991111-01.tar.xz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.9-991111-01.tar.xz",
            "expected_sha256": "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8",
            "available_locally": true,
            "observed_sha256": "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8"
          },
          {
            "candidate": "ee-gcc2.95.2-273a",
            "archive": "ee-gcc2.95.2-273a.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.2-273a.tar.gz",
            "expected_sha256": "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e",
            "available_locally": true,
            "observed_sha256": "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e"
          },
          {
            "candidate": "ee-gcc2.95.3-114",
            "archive": "ee-gcc2.95.3-114.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.3-114.tar.gz",
            "expected_sha256": "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb",
            "available_locally": true,
            "observed_sha256": "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb"
          },
          {
            "candidate": "ee-gcc2.95.3-136",
            "archive": "ee-gcc2.95.3-136.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.95.3-136.tar.gz",
            "expected_sha256": "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f",
            "available_locally": true,
            "observed_sha256": "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f"
          },
          {
            "candidate": "ee-gcc2.96",
            "archive": "ee-gcc2.96.tar.xz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc2.96.tar.xz",
            "expected_sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a",
            "available_locally": true,
            "observed_sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a"
          },
          {
            "candidate": "ee-gcc3.2-030926",
            "archive": "ee-gcc3.2-030926.tar.gz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-030926.tar.gz",
            "expected_sha256": "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9",
            "available_locally": true,
            "observed_sha256": "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9"
          },
          {
            "candidate": "ee-gcc3.2-040921",
            "archive": "ee-gcc3.2-040921.tar.xz",
            "source": "https://github.com/decompme/compilers/releases/download/compilers/ee-gcc3.2-040921.tar.xz",
            "expected_sha256": "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f",
            "available_locally": true,
            "observed_sha256": "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f"
          }
        ],
        "license_status": "The release archives inspected do not include COPYING or LICENSE entries. Per-package redistribution terms are unresolved; no compiler binaries are redistributed here.",
        "runtime_profile": "Immutable image IDs are verified before invocation: Debian Bookworm linux/amd64 with Wine 8 for Windows compiler drivers, and GNU binutils 2.40 in the Debian image for object preparation, linking, and objcopy.",
        "linker_profile": "GNU binutils 2.40 substitution; not the original proprietary linker.",
        "independent_unit": {
          "id": "parser_lookup",
          "symbol": "fr2_parser_lookup",
          "source": "tools/compiler_probe_recipe/parser_lookup.c",
          "source_sha256": "23059c7e7fc5c1b475d81bded4331b2a7a38ec1b3a9c1b32baccb1dafc2a93dd",
          "vaddr": "0018b840",
          "bytes": 80,
          "sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "definitions": {
            "fr2_parser_table": "0023b600",
            "fr2_parser_file": "0025eae8",
            "fr2_parser_message": "0025eb78",
            "report_error": "00105888"
          },
          "source_path": "../fr2/source/parser/parser.c",
          "independent_basis": "Direct source-path reference at 0018b880 and line 736, game parser diagnostic, and caller 0018ac40. Eight-byte table entries terminate on key 5 after the requested-key test.",
          "distinguishes": "Loop and branch-likely scheduling, table addressing, saved argument and diagnostic-call ABI.",
          "static_callers": [
            "0018ac40"
          ],
          "body_ranges": [
            {
              "start": "0018b840",
              "end": "0018b85f"
            },
            {
              "start": "0018b860",
              "end": "0018b86b"
            },
            {
              "start": "0018b86c",
              "end": "0018b877"
            },
            {
              "start": "0018b878",
              "end": "0018b87f"
            },
            {
              "start": "0018b880",
              "end": "0018b88f"
            }
          ],
          "claim_limit": "Hand-written inference from independent static evidence; names/types are provisional; no original-source, execution or owned-byte credit."
        }
      },
      "source": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.c",
        "bytes": 689,
        "sha256": "23059c7e7fc5c1b475d81bded4331b2a7a38ec1b3a9c1b32baccb1dafc2a93dd"
      },
      "reference": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/reference.bin",
        "bytes": 80,
        "sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d"
      },
      "symbol": "fr2_parser_lookup",
      "candidates": [
        {
          "id": "ee-gcc2.9-991111-01",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/bin/ee-gcc",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3o7vdn85/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/lib/gcc-lib/ee/2.9-ee-991111-01/cc1",
              "bytes": 4794381,
              "sha256": "b9aef69f93efb949f15ea58189e8eef4a002b9fe4de5d3fcf89c34e1244ec026"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/lib/gcc-lib/ee/2.9-ee-991111-01/cpp",
              "bytes": 241396,
              "sha256": "f85a54d241e019993fa7a06285d3677856b3b431e10318a587ab029373c603d7"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/ee/bin/as",
              "bytes": 2210289,
              "sha256": "296af123052ee39d175e5b3254102aafca105d4f6e975b351a13867f59b04019"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "64d0a50fef499da0b98177eb5e79e41dfb066ad44246b137c78a266ef97ee265",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3o7vdn85/candidate.o",
              "bytes": 1752,
              "sha256": "ec4d08c1ffb3307fecd921607598767ce35980c7f7c70a18cac79609d0ac3242"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3o7vdn85/prepared.o",
              "bytes": 1664,
              "sha256": "45667c4cf5a086f50109ed5ea0dc20f039f081ababf0a9237257441ec8cb5ac0"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3o7vdn85/linked.o",
              "bytes": 48652,
              "sha256": "42b307c91bb189031f8f9a7f4b9458dbc54e69253176fe8ffed6f3c5712c7789"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3o7vdn85/function.bin",
              "bytes": 80,
              "sha256": "6e954c8c21e6338cb8e2fa5560853d3b0cc98eabcf4eb466f37d5f4e39f4be84"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Using builtin specs.\ngcc version 2.9-ee-991111-01\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/cc1 /tools/compiler-profile-if5l6kuy/parser_lookup/candidate.c -G8 -lang-c -iprefix /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/ -quiet -dumpbase candidate.c -undef -D__GNUC__=2 -D__GNUC_MINOR__=9 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float -version -ffunction-sections -O2 -o /tmp/ccZlQhIA.s\nGNU C version 2.9-ee-991111-01 (ee) compiled by GNU C version 2.7.2.3.\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/../../../../ee/bin/as -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3o7vdn85/candidate.o /tmp/ccZlQhIA.s\nGNU assembler version 2.9-ee-991111 (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "ec4d08c1ffb3307fecd921607598767ce35980c7f7c70a18cac79609d0ac3242",
            "text_sha256": "f0a2a08e2fee6d28602f9374b7c51e0ca3aa027b39691646a33d22a8c650fdee",
            "text_bytes": 80,
            "relocations": [
              {
                "offset": 4,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 5,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 52,
                "type": 6,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 56,
                "type": 6,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 60,
                "type": 4,
                "symbol_index": 13,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 8,
              "word_index": 2,
              "expected": "ffbf0000",
              "actual": "0080382d",
              "relocation_mask": "00000000"
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3o7vdn85/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3o7vdn85/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3o7vdn85/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3o7vdn85/prepared.o",
            "--defsym=fr2_parser_table=0x0023b600",
            "--defsym=fr2_parser_file=0x0025eae8",
            "--defsym=fr2_parser_message=0x0025eb78",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3o7vdn85/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3o7vdn85/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "6e954c8c21e6338cb8e2fa5560853d3b0cc98eabcf4eb466f37d5f4e39f4be84",
          "actual_bytes": 80,
          "reference_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "reference_bytes": 80,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 8,
            "section_bytes": 80,
            "first_difference": {
              "offset": 8,
              "address": "0018b848",
              "file_offset": "0008c848",
              "word": 2,
              "expected": "0000bfff",
              "actual": "2d388000"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.96",
          "status": "pass",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3oxdttxk/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/cc1",
              "bytes": 5526661,
              "sha256": "59ec92b3f9f3513e0633331af304733e3094de30884e662a8cb584a51c1c42b5"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/cpp0",
              "bytes": 421478,
              "sha256": "f6f6b598f39649edfe171d6da8c7f91d07f2b87c2aeeffffbc5f566bfb1a39a9"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/ee/bin/as",
              "bytes": 2169068,
              "sha256": "b8cfdb6ecb6931642914020f92a62e653378f57230eed4895f69afa050d47b5e"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "b8c284d16c9c0a0e8788e9522c46881e224ad01fa1c732aed43f821cc32f168b",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3oxdttxk/candidate.o",
              "bytes": 1892,
              "sha256": "39848f64b683740e16ca1e7c1f63873cd58fc8d7fdb6d0742fffb4f561ea4c5f"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3oxdttxk/prepared.o",
              "bytes": 1732,
              "sha256": "9d5c5573bf3958289477f2c3c7ecd2bef27947005867014c2d2d9f9691d6fcd4"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3oxdttxk/linked.o",
              "bytes": 48652,
              "sha256": "e127cb32c9a9a680867f85859877680bb9c97e01fbf662eb67db32c269d0798d"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3oxdttxk/function.bin",
              "bytes": 80,
              "sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Using builtin specs.\ngcc version 2.96-ee-001003-1\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/ -D__GNUC__=2 -D__GNUC_MINOR__=96 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/parser_lookup/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccG2IMkc.s\nGNU CPP version 2.96-ee-001003-1 (cpplib)\n [AL 1.1, MM 40] BSD Mips\nGNU C version 2.96-ee-001003-1 (ee) compiled by GNU C version 2.9-gnupro-99r1.\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/sys-include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/sys-include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/../../../../ee/bin/as -G8 -EL -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3oxdttxk/candidate.o /tmp/ccG2IMkc.s\nGNU assembler version 2.10-ee-001003-1 (ee) using BFD version 2.10-ee-001003\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "39848f64b683740e16ca1e7c1f63873cd58fc8d7fdb6d0742fffb4f561ea4c5f",
            "text_sha256": "a914946fe3c5823d22a9cf1a12fa92b8b8d8b84fec4baec4627c50d809d5cc07",
            "text_bytes": 80,
            "relocations": [
              {
                "offset": 4,
                "type": 5,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 6,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 5,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 64,
                "type": 6,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 68,
                "type": 6,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 72,
                "type": 4,
                "symbol_index": 14,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof."
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3oxdttxk/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3oxdttxk/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3oxdttxk/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3oxdttxk/prepared.o",
            "--defsym=fr2_parser_table=0x0023b600",
            "--defsym=fr2_parser_file=0x0025eae8",
            "--defsym=fr2_parser_message=0x0025eb78",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3oxdttxk/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-3oxdttxk/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "actual_bytes": 80,
          "reference_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "reference_bytes": 80,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "pass",
            "reason": null,
            "matched_bytes": 80,
            "section_bytes": 80
          }
        },
        {
          "id": "ee-gcc3.2-030926",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-hs2xd31q/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/cc1",
              "bytes": 9764536,
              "sha256": "da4fec4d48d91e62fd968f76acb16981dd8131d02f27c1b7559f0e903b590eb6"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/cpp0",
              "bytes": 703785,
              "sha256": "2d1a4b260e143a8b467bb7609cb3fd60ae541174ffff78d922feb2d7fbb0e218"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/ee/bin/as",
              "bytes": 5887159,
              "sha256": "d04424acb1359b31b3ad138f8d17876623ffe9182497ff4516055b71f22bf2fa"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "8ba17b0f2cbcc87b31bb164766bc3e7e340f714adfb518bc4634a6f1ffda8951",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-hs2xd31q/candidate.o",
              "bytes": 1612,
              "sha256": "cb4441635d8260b08f9822cbb6fc31806132d75c349f15c419286046fd1eb6d3"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-hs2xd31q/prepared.o",
              "bytes": 1612,
              "sha256": "202a1785130d87826da795b51d836466f3cdafa584bf204a29544fc7d39b54ed"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-hs2xd31q/linked.o",
              "bytes": 48596,
              "sha256": "5d2338d0001a3ad556a8142a8b7df5258303119ecba72034e98b301469219075"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-hs2xd31q/function.bin",
              "bytes": 80,
              "sha256": "3ba6189c91f82752ba18ad56702d15fd9199c1e0c57f8335b1179670d6c90392"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Reading specs from /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/specs\nConfigured with: /proj/ee-toolchain/ee-gcc-3.2-final-rc2/release-src/ee-gcc/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-030926\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/parser_lookup/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/cc45U0RL.s\nGNU CPP version 3.2-ee-030926 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-030926 (ee)\n\tcompiled by GNU C version 3.2.\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-hs2xd31q/candidate.o /tmp/cc45U0RL.s\nGNU assembler version 2.12-ee-030926 (ee) using BFD version 2.12-ee-030926 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "cb4441635d8260b08f9822cbb6fc31806132d75c349f15c419286046fd1eb6d3",
            "text_sha256": "b90f7d245a9261ab2bdb246651af5fd5c99db5ba2b80a13312a5795d2409fb94",
            "text_bytes": 80,
            "relocations": [
              {
                "offset": 4,
                "type": 5,
                "symbol_index": 9,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 6,
                "symbol_index": 9,
                "mask": "0000ffff"
              },
              {
                "offset": 44,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 52,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 48,
                "type": 5,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 56,
                "type": 6,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 60,
                "type": 4,
                "symbol_index": 12,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 4,
              "word_index": 1,
              "expected": "3c020024",
              "actual": "3c0f0000",
              "relocation_mask": "0000ffff"
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-hs2xd31q/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-hs2xd31q/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-hs2xd31q/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-hs2xd31q/prepared.o",
            "--defsym=fr2_parser_table=0x0023b600",
            "--defsym=fr2_parser_file=0x0025eae8",
            "--defsym=fr2_parser_message=0x0025eb78",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-hs2xd31q/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-hs2xd31q/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "3ba6189c91f82752ba18ad56702d15fd9199c1e0c57f8335b1179670d6c90392",
          "actual_bytes": 80,
          "reference_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "reference_bytes": 80,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 4,
            "section_bytes": 80,
            "first_difference": {
              "offset": 4,
              "address": "0018b844",
              "file_offset": "0008c844",
              "word": 1,
              "expected": "2400023c",
              "actual": "24000f3c"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc3.2-040921",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-gcc",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
            "platform": "linux/amd64",
            "base": "Debian bookworm-slim sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587",
            "packages": {
              "libc6:i386": "2.36-9+deb12u14",
              "libgcc-s1:i386": "12.2.0-14+deb12u1",
              "binutils-mips-linux-gnu": "2.40-2cross2"
            }
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-06ti90fe/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/cc1",
              "bytes": 7201720,
              "sha256": "0bcc90bd23e10698e75047db9a84ea47e753791115fdd23d6f637a544f6d257d"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-cpp",
              "bytes": 266763,
              "sha256": "ed76fe8e08c13c749d59a458d21c912567b10e5e01bff028a4147debd56d15e6"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/ee/bin/as",
              "bytes": 3706255,
              "sha256": "cf85edec3ea30b0918e8a78ac49affca111a45e5b0ca9a776b6ded5c0118379b"
            },
            "mips_linker": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compiler_sha256": "a5095b5d7b55f91535b12e48e9d808170fa9fb8c0620c43c2fb61379b1a3663a",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-06ti90fe/candidate.o",
              "bytes": 1612,
              "sha256": "cb4441635d8260b08f9822cbb6fc31806132d75c349f15c419286046fd1eb6d3"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-06ti90fe/prepared.o",
              "bytes": 1612,
              "sha256": "202a1785130d87826da795b51d836466f3cdafa584bf204a29544fc7d39b54ed"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-06ti90fe/linked.o",
              "bytes": 48596,
              "sha256": "5d2338d0001a3ad556a8142a8b7df5258303119ecba72034e98b301469219075"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-06ti90fe/function.bin",
              "bytes": 80,
              "sha256": "3ba6189c91f82752ba18ad56702d15fd9199c1e0c57f8335b1179670d6c90392"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "Using built-in specs.\nConfigured with: ../src/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-040921\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/parser_lookup/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccIbgB5i.s\nGNU CPP version 3.2-ee-040921 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-040921 (ee)\n\tcompiled by GNU C version 3.2.2 20030222 (Red Hat Linux 3.2.2-5).\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-06ti90fe/candidate.o /tmp/ccIbgB5i.s\nGNU assembler version 2.12-ee-040921 (ee) using BFD version 2.12-ee-040921 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "cb4441635d8260b08f9822cbb6fc31806132d75c349f15c419286046fd1eb6d3",
            "text_sha256": "b90f7d245a9261ab2bdb246651af5fd5c99db5ba2b80a13312a5795d2409fb94",
            "text_bytes": 80,
            "relocations": [
              {
                "offset": 4,
                "type": 5,
                "symbol_index": 9,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 6,
                "symbol_index": 9,
                "mask": "0000ffff"
              },
              {
                "offset": 44,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 52,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 48,
                "type": 5,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 56,
                "type": 6,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 60,
                "type": 4,
                "symbol_index": 12,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 4,
              "word_index": 1,
              "expected": "3c020024",
              "actual": "3c0f0000",
              "relocation_mask": "0000ffff"
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-06ti90fe/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-06ti90fe/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-06ti90fe/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-06ti90fe/prepared.o",
            "--defsym=fr2_parser_table=0x0023b600",
            "--defsym=fr2_parser_file=0x0025eae8",
            "--defsym=fr2_parser_message=0x0025eb78",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-06ti90fe/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-06ti90fe/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "3ba6189c91f82752ba18ad56702d15fd9199c1e0c57f8335b1179670d6c90392",
          "actual_bytes": 80,
          "reference_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "reference_bytes": 80,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 4,
            "section_bytes": 80,
            "first_difference": {
              "offset": 4,
              "address": "0018b844",
              "file_offset": "0008c844",
              "word": 1,
              "expected": "2400023c",
              "actual": "24000f3c"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.95.2-273a",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/bin/ee-gcc.exe",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "platform": "linux/amd64",
            "runner": "Wine 8 Debian Bookworm on Linux amd64 via Docker Desktop"
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jk1t2wfm/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/cc1.exe",
              "bytes": 1773568,
              "sha256": "2aaf3d22ce5c3508ecba15f16b06737713263e6aee289ca1e43d3ff9c17d964f"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/cpp.exe",
              "bytes": 110592,
              "sha256": "f7db993de8745339ec71cf10d5fe9e7772d75e79a037e97809ed5e34ea3150c3"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/lib/gcc-lib/ee/2.95.2/specs",
              "bytes": 4260,
              "sha256": "372d6255779b9214f7f980a8289461209c9be4cb12a91c6b4e01e14c0f91070c"
            }
          },
          "compiler_sha256": "ab787f9bda2531e116f420eec639e7d34bcc92caf4eb8d3dc71fefddffd3fcfc",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jk1t2wfm/candidate.o",
              "bytes": 1760,
              "sha256": "c8a8076dc5f17ba5a753500a743116008e0427f32ef58549b350f98db5829c22"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jk1t2wfm/prepared.o",
              "bytes": 1672,
              "sha256": "1ae7e12902c44f6596327a201096675d964f949d6492fd5ee670005065304e26"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jk1t2wfm/linked.o",
              "bytes": 48660,
              "sha256": "9a8c378030e23d7dfdecc3ccdd3d69e20ce9a661545f0a75de5341fd70ddda9a"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jk1t2wfm/function.bin",
              "bytes": 88,
              "sha256": "d35756764cb228b0705a83eabb1db416a0cb1bade1f4a48685416bf9f02ebca4"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.2-EE\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/parser_lookup/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.2 v2 [AL 1.1, MM 40] BSD Mips\n#include \"...\" search starts here:\nEnd of search list.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.2 SN BUILD v2.73a for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jk1t2wfm/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "c8a8076dc5f17ba5a753500a743116008e0427f32ef58549b350f98db5829c22",
            "text_sha256": "01e285e404b8ae4fe780b9d631b795567c09dc93aa7e782438c87b6e48e28f62",
            "text_bytes": 88,
            "relocations": [
              {
                "offset": 4,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 5,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 60,
                "type": 6,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 64,
                "type": 6,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 68,
                "type": 4,
                "symbol_index": 13,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 80,
              "reason": "function length differs",
              "expected_bytes": 80,
              "actual_bytes": 88
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jk1t2wfm/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jk1t2wfm/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jk1t2wfm/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jk1t2wfm/prepared.o",
            "--defsym=fr2_parser_table=0x0023b600",
            "--defsym=fr2_parser_file=0x0025eae8",
            "--defsym=fr2_parser_message=0x0025eb78",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jk1t2wfm/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jk1t2wfm/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "d35756764cb228b0705a83eabb1db416a0cb1bade1f4a48685416bf9f02ebca4",
          "actual_bytes": 88,
          "reference_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "reference_bytes": 80,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 8,
            "section_bytes": 80,
            "first_difference": {
              "offset": 8,
              "address": "0018b848",
              "file_offset": "0008c848",
              "word": 2,
              "expected": "0000bfff",
              "actual": "2d388000"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.95.3-114",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/bin/ee-gcc.exe",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "platform": "linux/amd64",
            "runner": "Wine 8 Debian Bookworm on Linux amd64 via Docker Desktop"
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jfpl6aun/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1654784,
              "sha256": "7bccdee8d6cc6bc56a84824cadb9c5ce546a1aa7f9b836447d2482408c5c5832"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "271e9a55b782153acf303566c93c18ea30253e9c14d4df4daa55c521ead92eef"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "compiler_sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jfpl6aun/candidate.o",
              "bytes": 1760,
              "sha256": "c8a8076dc5f17ba5a753500a743116008e0427f32ef58549b350f98db5829c22"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jfpl6aun/prepared.o",
              "bytes": 1672,
              "sha256": "1ae7e12902c44f6596327a201096675d964f949d6492fd5ee670005065304e26"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jfpl6aun/linked.o",
              "bytes": 48660,
              "sha256": "9a8c378030e23d7dfdecc3ccdd3d69e20ce9a661545f0a75de5341fd70ddda9a"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jfpl6aun/function.bin",
              "bytes": 88,
              "sha256": "d35756764cb228b0705a83eabb1db416a0cb1bade1f4a48685416bf9f02ebca4"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/parser_lookup/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.05 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-114/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.14 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jfpl6aun/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "c8a8076dc5f17ba5a753500a743116008e0427f32ef58549b350f98db5829c22",
            "text_sha256": "01e285e404b8ae4fe780b9d631b795567c09dc93aa7e782438c87b6e48e28f62",
            "text_bytes": 88,
            "relocations": [
              {
                "offset": 4,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 5,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 60,
                "type": 6,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 64,
                "type": 6,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 68,
                "type": 4,
                "symbol_index": 13,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 80,
              "reason": "function length differs",
              "expected_bytes": 80,
              "actual_bytes": 88
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jfpl6aun/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jfpl6aun/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jfpl6aun/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jfpl6aun/prepared.o",
            "--defsym=fr2_parser_table=0x0023b600",
            "--defsym=fr2_parser_file=0x0025eae8",
            "--defsym=fr2_parser_message=0x0025eb78",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jfpl6aun/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-jfpl6aun/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "d35756764cb228b0705a83eabb1db416a0cb1bade1f4a48685416bf9f02ebca4",
          "actual_bytes": 88,
          "reference_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "reference_bytes": 80,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 8,
            "section_bytes": 80,
            "first_difference": {
              "offset": 8,
              "address": "0018b848",
              "file_offset": "0008c848",
              "word": 2,
              "expected": "0000bfff",
              "actual": "2d388000"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.95.3-136",
          "status": "fail",
          "compiler_launcher": "/bin/bash",
          "compiler": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/bin/ee-gcc.exe",
          "objcopy_launcher": "/bin/bash",
          "objcopy": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
          "runtime": {
            "image": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
            "platform": "linux/amd64",
            "runner": "Wine 8 Debian Bookworm on Linux amd64 via Docker Desktop"
          },
          "compile_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-8qd74zfs/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy"
          ],
          "flags": [
            "-G8",
            "-O2",
            "-v"
          ],
          "compiler_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "objcopy_launcher_sha256": "35536aea9733aa345b61134a98d00232380898e55b2ea2a07c497011f7dfc7a3",
          "tool_files": {
            "cc1": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1708032,
              "sha256": "0393bcd31f91a6b9f0255db97f1cc99eba78ee8fc003e9a04dfabed1ae1d522e"
            },
            "cpp": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "b9c50aa66f9cf5dbd80b2affe9874ec7674b7328965c629476f6ad7c77943154"
            },
            "gnu_assembler": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "compiler_sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e",
          "objcopy_sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed",
          "artifacts": {
            "object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-8qd74zfs/candidate.o",
              "bytes": 1760,
              "sha256": "3737b1a8c8693094928e0e3b99f6f3b085c1eaabf013b8bf37b5ed24a512406c"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-8qd74zfs/prepared.o",
              "bytes": 1672,
              "sha256": "7d573c37d4e8926ad1b2f0acb05d92d69c4e920372eb0726646cf548194561aa"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-8qd74zfs/linked.o",
              "bytes": 48660,
              "sha256": "071d2ae5e2f1aba91c9a09a2d22e5f6ff9bedfb403bd9c7e4714f33065d7cab8"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-8qd74zfs/function.bin",
              "bytes": 88,
              "sha256": "32f6928b9c51c4efbf11334240c55e84767dace53cda274d2897e4baf3206321"
            }
          },
          "phase_tools": {
            "prepare_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-objcopy",
              "bytes": 192168,
              "sha256": "29e2ef3c83acffe8287b3666934e8a76624a53e539089bd4715e98ace874a2ed"
            },
            "link": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/mips-linux-gnu-ld",
              "bytes": 1817176,
              "sha256": "c4f8ab0708eef3a96b5cc0680d9455f557dcd2e08576f1c2a7abb631931cd271"
            }
          },
          "compile_returncode": 0,
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-if5l6kuy/parser_lookup/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.12 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-136/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.36 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-8qd74zfs/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "3737b1a8c8693094928e0e3b99f6f3b085c1eaabf013b8bf37b5ed24a512406c",
            "text_sha256": "bc8f86f0d294945a7f04f3cad3ac5ff2eccfa29c48e39b1d27686d35abced513",
            "text_bytes": 88,
            "relocations": [
              {
                "offset": 4,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 16,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 5,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 60,
                "type": 6,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 28,
                "type": 5,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 64,
                "type": 6,
                "symbol_index": 12,
                "mask": "0000ffff"
              },
              {
                "offset": 68,
                "type": 4,
                "symbol_index": 13,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 80,
              "reason": "function length differs",
              "expected_bytes": 80,
              "actual_bytes": 88
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-8qd74zfs/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-8qd74zfs/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-8qd74zfs/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-8qd74zfs/prepared.o",
            "--defsym=fr2_parser_table=0x0023b600",
            "--defsym=fr2_parser_file=0x0025eae8",
            "--defsym=fr2_parser_message=0x0025eb78",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-8qd74zfs/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy/parser_lookup/objects/fr2-compiler-probe-8qd74zfs/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "32f6928b9c51c4efbf11334240c55e84767dace53cda274d2897e4baf3206321",
          "actual_bytes": 88,
          "reference_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "reference_bytes": 80,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 8,
            "section_bytes": 80,
            "first_difference": {
              "offset": 8,
              "address": "0018b848",
              "file_offset": "0008c848",
              "word": 2,
              "expected": "0000bfff",
              "actual": "2d388000"
            }
          },
          "reason": "function bytes differ"
        }
      ],
      "claim_limits": [
        "A unique match identifies this source/compiler/flags/reference probe only.",
        "It does not establish the original compiler ID without an independently evidenced retail function/reference pair.",
        "This runner executes compiler and objcopy argv from the local manifest."
      ],
      "unit": "parser_lookup",
      "package_members": [
        {
          "candidate": "ee-gcc2.9-991111-01",
          "archive": "ee-gcc2.9-991111-01.tar.xz",
          "sha256": "ed684fd98f89d36b0121caab311052089103e3b36241fcef4338cc9ea41c75b8",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 154155,
              "sha256": "64d0a50fef499da0b98177eb5e79e41dfb066ad44246b137c78a266ef97ee265"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.9-ee-991111-01/cc1",
              "bytes": 4794381,
              "sha256": "b9aef69f93efb949f15ea58189e8eef4a002b9fe4de5d3fcf89c34e1244ec026"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.9-ee-991111-01/cpp",
              "bytes": 241396,
              "sha256": "f85a54d241e019993fa7a06285d3677856b3b431e10318a587ab029373c603d7"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 2210289,
              "sha256": "296af123052ee39d175e5b3254102aafca105d4f6e975b351a13867f59b04019"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.96",
          "archive": "ee-gcc2.96.tar.xz",
          "sha256": "0590d2ca9da8f5903889d66761220d14b47a8d14ba987ca53db84a1650a1fd0a",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 333402,
              "sha256": "b8c284d16c9c0a0e8788e9522c46881e224ad01fa1c732aed43f821cc32f168b"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.96-ee-001003-1/cc1",
              "bytes": 5526661,
              "sha256": "59ec92b3f9f3513e0633331af304733e3094de30884e662a8cb584a51c1c42b5"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.96-ee-001003-1/cpp0",
              "bytes": 421478,
              "sha256": "f6f6b598f39649edfe171d6da8c7f91d07f2b87c2aeeffffbc5f566bfb1a39a9"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 2169068,
              "sha256": "b8cfdb6ecb6931642914020f92a62e653378f57230eed4895f69afa050d47b5e"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc3.2-030926",
          "archive": "ee-gcc3.2-030926.tar.gz",
          "sha256": "6b92b61e40f80835b165d14fadd57d4046dbee82195599f791626180fe79b8e9",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 335156,
              "sha256": "8ba17b0f2cbcc87b31bb164766bc3e7e340f714adfb518bc4634a6f1ffda8951"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/3.2-ee-030926/cc1",
              "bytes": 9764536,
              "sha256": "da4fec4d48d91e62fd968f76acb16981dd8131d02f27c1b7559f0e903b590eb6"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/3.2-ee-030926/cpp0",
              "bytes": 703785,
              "sha256": "2d1a4b260e143a8b467bb7609cb3fd60ae541174ffff78d922feb2d7fbb0e218"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 5887159,
              "sha256": "d04424acb1359b31b3ad138f8d17876623ffe9182497ff4516055b71f22bf2fa"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc3.2-040921",
          "archive": "ee-gcc3.2-040921.tar.xz",
          "sha256": "8c60ca7482523190e999524a7e4de2379dcf7ffee543c1b5663bfdf6a80ebf0f",
          "members": {
            "driver": {
              "member": "bin/ee-gcc",
              "bytes": 265116,
              "sha256": "a5095b5d7b55f91535b12e48e9d808170fa9fb8c0620c43c2fb61379b1a3663a"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/3.2-ee-040921/cc1",
              "bytes": 7201720,
              "sha256": "0bcc90bd23e10698e75047db9a84ea47e753791115fdd23d6f637a544f6d257d"
            },
            "cpp": {
              "member": "bin/ee-cpp",
              "bytes": 266763,
              "sha256": "ed76fe8e08c13c749d59a458d21c912567b10e5e01bff028a4147debd56d15e6"
            },
            "gnu_assembler": {
              "member": "ee/bin/as",
              "bytes": 3706255,
              "sha256": "cf85edec3ea30b0918e8a78ac49affca111a45e5b0ca9a776b6ded5c0118379b"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.95.2-273a",
          "archive": "ee-gcc2.95.2-273a.tar.gz",
          "sha256": "ee9d9a7fccb59aebfa78a5587f6f8059660b91f705acddbc292ad2243c8e562e",
          "members": {
            "driver": {
              "member": "bin/ee-gcc.exe",
              "bytes": 122880,
              "sha256": "ab787f9bda2531e116f420eec639e7d34bcc92caf4eb8d3dc71fefddffd3fcfc"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.95.2/cc1.exe",
              "bytes": 1773568,
              "sha256": "2aaf3d22ce5c3508ecba15f16b06737713263e6aee289ca1e43d3ff9c17d964f"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.95.2/cpp.exe",
              "bytes": 110592,
              "sha256": "f7db993de8745339ec71cf10d5fe9e7772d75e79a037e97809ed5e34ea3150c3"
            },
            "gnu_assembler": {
              "member": "lib/gcc-lib/ee/2.95.2/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "member": "lib/gcc-lib/ee/2.95.2/specs",
              "bytes": 4260,
              "sha256": "372d6255779b9214f7f980a8289461209c9be4cb12a91c6b4e01e14c0f91070c"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.95.3-114",
          "archive": "ee-gcc2.95.3-114.tar.gz",
          "sha256": "dbc2c8c764631788d4cbb4c848c3cb0002fded0f4a95bae39e6d8b794391a6cb",
          "members": {
            "driver": {
              "member": "bin/ee-gcc.exe",
              "bytes": 122880,
              "sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1654784,
              "sha256": "7bccdee8d6cc6bc56a84824cadb9c5ce546a1aa7f9b836447d2482408c5c5832"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "271e9a55b782153acf303566c93c18ea30253e9c14d4df4daa55c521ead92eef"
            },
            "gnu_assembler": {
              "member": "lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "member": "lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        },
        {
          "candidate": "ee-gcc2.95.3-136",
          "archive": "ee-gcc2.95.3-136.tar.gz",
          "sha256": "3b6ae6897229ad005aaf1b0afaa1f3cb46e74b4c21a42e01130c07c0c598067f",
          "members": {
            "driver": {
              "member": "bin/ee-gcc.exe",
              "bytes": 122880,
              "sha256": "522d28f9d74ddfce89568437156c8ee323c806de525d99907f698050dee8d81e"
            },
            "cc1": {
              "member": "lib/gcc-lib/ee/2.95.3/cc1.exe",
              "bytes": 1708032,
              "sha256": "0393bcd31f91a6b9f0255db97f1cc99eba78ee8fc003e9a04dfabed1ae1d522e"
            },
            "cpp": {
              "member": "lib/gcc-lib/ee/2.95.3/cpp.exe",
              "bytes": 159744,
              "sha256": "b9c50aa66f9cf5dbd80b2affe9874ec7674b7328965c629476f6ad7c77943154"
            },
            "gnu_assembler": {
              "member": "lib/gcc-lib/ee/2.95.3/as.exe",
              "bytes": 622592,
              "sha256": "7f504e571215fead2a15a14520bd22dc13507a1f13b479ca8c06a165f4a886a4"
            },
            "specs": {
              "member": "lib/gcc-lib/ee/2.95.3/specs",
              "bytes": 4260,
              "sha256": "7b5520c0d9d04623b899ba80dbd713635a0aa17f0e58f7ba58b30c443cd48d76"
            }
          },
          "source_disposition": "Exact corresponding source/notices remain unresolved under #21."
        }
      ],
      "package_identity_status": "pass"
    }
  ],
  "runtime_identity": {
    "linux-tools": {
      "image_id": "sha256:4fbdbf2a3bdeb29e3a9fff22f322e6cf5dd45131af51b89501352bd2ef7402ca",
      "platform": "linux/amd64"
    },
    "wine-compiler": {
      "image_id": "sha256:ef74eccc9bb960737d53d635a6b67692e8eef92c01b0dc8980ed9bc539f4a4ba",
      "platform": "linux/amd64"
    }
  },
  "decision": {
    "bytes": 5756,
    "sha256": "e69f06929fded9db6fb085cfa29bcae7cd89088652d27431fd7718e9e29e6078"
  },
  "local_work": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-if5l6kuy",
  "historical_identity_status": "incomplete: exact corresponding compiler source/package binding remains #21; a unique panel profile is bounded to these source/flag/runtime/link inputs."
}
```
