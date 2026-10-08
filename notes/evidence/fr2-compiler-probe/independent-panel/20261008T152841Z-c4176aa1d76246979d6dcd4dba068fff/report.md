# compiler-profile-independent: fail

Invalid: independent compiler units contradict a single matching profile

```json
{
  "profile_status": "fail",
  "selected_id": null,
  "surviving_candidates": [],
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
      "matches": []
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
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/manifest.json",
        "bytes": 27280,
        "sha256": "93c5bde969deeff4088dbefe23500b9d3595e29bc658abce0aa0d3328c723eb9"
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
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.c",
        "bytes": 627,
        "sha256": "44b17bacf38c4a9befdb77dca2b137ac1e0826cb595ad7dd87c4775dfa5375bc"
      },
      "reference": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/reference.bin",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/bin/ee-gcc",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-_6kjtjyi/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-_6kjtjyi/candidate.o",
              "bytes": 2000,
              "sha256": "95aa9b9637f5f81318c2b767195a07bf1aeb38b1a4a2c5d1860e08e8518455a3"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-_6kjtjyi/prepared.o",
              "bytes": 1904,
              "sha256": "8449d9f796b99660552e5a8b50e2db5ae46b9f4dd7f380a02af3834e0ab5403c"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-_6kjtjyi/linked.o",
              "bytes": 14696,
              "sha256": "8402fedc5f4239cbc322dbb1315f0855136ba433b1d35d3bc3610881e306241c"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-_6kjtjyi/function.bin",
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
          "compile_stderr": "Using builtin specs.\ngcc version 2.9-ee-991111-01\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/cc1 /tools/compiler-profile-gsg9vgj_/accessor/candidate.c -G8 -lang-c -iprefix /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/ -quiet -dumpbase candidate.c -undef -D__GNUC__=2 -D__GNUC_MINOR__=9 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float -version -ffunction-sections -O2 -o /tmp/ccJQozZA.s\nGNU C version 2.9-ee-991111-01 (ee) compiled by GNU C version 2.7.2.3.\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/../../../../ee/bin/as -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-_6kjtjyi/candidate.o /tmp/ccJQozZA.s\nGNU assembler version 2.9-ee-991111 (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "95aa9b9637f5f81318c2b767195a07bf1aeb38b1a4a2c5d1860e08e8518455a3",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-_6kjtjyi/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-_6kjtjyi/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-_6kjtjyi/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-_6kjtjyi/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-_6kjtjyi/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-_6kjtjyi/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-xfg9xxic/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-xfg9xxic/candidate.o",
              "bytes": 2144,
              "sha256": "de2350d1e2a60da59638c7a8eaf5fa87c7530ddc5747559a974ddeca6f6a7666"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-xfg9xxic/prepared.o",
              "bytes": 1968,
              "sha256": "2b35991d4f88a20427f469b73786d3d51273e982460a731ecb6faa6815c2f537"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-xfg9xxic/linked.o",
              "bytes": 14696,
              "sha256": "363a944f502524c0d3650e808a9ff24f2ddc505fa6d28387995fc73067b48998"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-xfg9xxic/function.bin",
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
          "compile_stderr": "Using builtin specs.\ngcc version 2.96-ee-001003-1\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/ -D__GNUC__=2 -D__GNUC_MINOR__=96 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/accessor/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/cc5CU5iM.s\nGNU CPP version 2.96-ee-001003-1 (cpplib)\n [AL 1.1, MM 40] BSD Mips\nGNU C version 2.96-ee-001003-1 (ee) compiled by GNU C version 2.9-gnupro-99r1.\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/sys-include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/sys-include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/../../../../ee/bin/as -G8 -EL -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-xfg9xxic/candidate.o /tmp/cc5CU5iM.s\nGNU assembler version 2.10-ee-001003-1 (ee) using BFD version 2.10-ee-001003\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "de2350d1e2a60da59638c7a8eaf5fa87c7530ddc5747559a974ddeca6f6a7666",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-xfg9xxic/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-xfg9xxic/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-xfg9xxic/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-xfg9xxic/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-xfg9xxic/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-xfg9xxic/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-5tovmamb/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-5tovmamb/candidate.o",
              "bytes": 1860,
              "sha256": "32dc339f7edd35ee335dc154b97c85bbc433168489d550da70d3a8a16e4ba657"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-5tovmamb/prepared.o",
              "bytes": 1860,
              "sha256": "4b31f053475c9b4c0069e1f6096e2293d9f13f32a85392d6a765a9e6f6a06cdc"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-5tovmamb/linked.o",
              "bytes": 14640,
              "sha256": "3c7b57ff963ad5096ed9b64a2e65aa333fd8d12f24f6df6ec1769563b0dda8d0"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-5tovmamb/function.bin",
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
          "compile_stderr": "Reading specs from /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/specs\nConfigured with: /proj/ee-toolchain/ee-gcc-3.2-final-rc2/release-src/ee-gcc/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-030926\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/accessor/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccBOylyn.s\nGNU CPP version 3.2-ee-030926 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-030926 (ee)\n\tcompiled by GNU C version 3.2.\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-5tovmamb/candidate.o /tmp/ccBOylyn.s\nGNU assembler version 2.12-ee-030926 (ee) using BFD version 2.12-ee-030926 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "32dc339f7edd35ee335dc154b97c85bbc433168489d550da70d3a8a16e4ba657",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-5tovmamb/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-5tovmamb/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-5tovmamb/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-5tovmamb/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-5tovmamb/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-5tovmamb/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-scp7je_4/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-scp7je_4/candidate.o",
              "bytes": 1860,
              "sha256": "32dc339f7edd35ee335dc154b97c85bbc433168489d550da70d3a8a16e4ba657"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-scp7je_4/prepared.o",
              "bytes": 1860,
              "sha256": "4b31f053475c9b4c0069e1f6096e2293d9f13f32a85392d6a765a9e6f6a06cdc"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-scp7je_4/linked.o",
              "bytes": 14640,
              "sha256": "3c7b57ff963ad5096ed9b64a2e65aa333fd8d12f24f6df6ec1769563b0dda8d0"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-scp7je_4/function.bin",
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
          "compile_stderr": "Using built-in specs.\nConfigured with: ../src/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-040921\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/accessor/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccmJlQdb.s\nGNU CPP version 3.2-ee-040921 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-040921 (ee)\n\tcompiled by GNU C version 3.2.2 20030222 (Red Hat Linux 3.2.2-5).\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-scp7je_4/candidate.o /tmp/ccmJlQdb.s\nGNU assembler version 2.12-ee-040921 (ee) using BFD version 2.12-ee-040921 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "32dc339f7edd35ee335dc154b97c85bbc433168489d550da70d3a8a16e4ba657",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-scp7je_4/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-scp7je_4/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-scp7je_4/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-scp7je_4/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-scp7je_4/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-scp7je_4/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-k099w75f/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-k099w75f/candidate.o",
              "bytes": 2004,
              "sha256": "e58b04c7cefd75667d548b6cbe46509350beadb20a823023eb95445132a87c36"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-k099w75f/prepared.o",
              "bytes": 1908,
              "sha256": "9f2885077bcff86936c88d6b2f12b386820c86d5f08749ce38e076c3b3581a7a"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-k099w75f/linked.o",
              "bytes": 14696,
              "sha256": "6c304052c26ee3414cc85fabe32c6486e8aa050ae682fe973b7406c1fc4552e8"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-k099w75f/function.bin",
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
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.2-EE\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/accessor/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.2 v2 [AL 1.1, MM 40] BSD Mips\n#include \"...\" search starts here:\nEnd of search list.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.2 SN BUILD v2.73a for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-k099w75f/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "e58b04c7cefd75667d548b6cbe46509350beadb20a823023eb95445132a87c36",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-k099w75f/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-k099w75f/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-k099w75f/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-k099w75f/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-k099w75f/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-k099w75f/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-4i46rj0a/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-4i46rj0a/candidate.o",
              "bytes": 2004,
              "sha256": "e58b04c7cefd75667d548b6cbe46509350beadb20a823023eb95445132a87c36"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-4i46rj0a/prepared.o",
              "bytes": 1908,
              "sha256": "9f2885077bcff86936c88d6b2f12b386820c86d5f08749ce38e076c3b3581a7a"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-4i46rj0a/linked.o",
              "bytes": 14696,
              "sha256": "6c304052c26ee3414cc85fabe32c6486e8aa050ae682fe973b7406c1fc4552e8"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-4i46rj0a/function.bin",
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
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/accessor/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.05 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-114/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.14 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-4i46rj0a/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "e58b04c7cefd75667d548b6cbe46509350beadb20a823023eb95445132a87c36",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-4i46rj0a/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-4i46rj0a/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-4i46rj0a/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-4i46rj0a/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-4i46rj0a/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-4i46rj0a/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-sgiloepd/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-sgiloepd/candidate.o",
              "bytes": 2004,
              "sha256": "9155ee40d08d20182ddcc2fab37fe397b47c7d2676c18d55fb38dd5e6d97cc12"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-sgiloepd/prepared.o",
              "bytes": 1908,
              "sha256": "aa7cdb284bd2eab2234bbe97a5982fa4f09963cd986ec2b4c80d2c8aed4b7375"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-sgiloepd/linked.o",
              "bytes": 14696,
              "sha256": "f6de26b412cab021dbbd5707e7444598438ae289880aa2f9ab473a10accde330"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-sgiloepd/function.bin",
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
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/accessor/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.12 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-136/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.36 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-sgiloepd/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "9155ee40d08d20182ddcc2fab37fe397b47c7d2676c18d55fb38dd5e6d97cc12",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-sgiloepd/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-sgiloepd/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/candidate.ld",
            "--defsym=misc3d_db_id=0x00290ac4",
            "--defsym=report_error=0x00105888",
            "--defsym=_gp=0x00295d70",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-sgiloepd/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-sgiloepd/prepared.o"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_get_database_id=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-sgiloepd/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/accessor/objects/fr2-compiler-probe-sgiloepd/linked.o"
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
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/manifest.json",
        "bytes": 29641,
        "sha256": "3d73d102cfa08ea1646663a8c06a2d798b6260294a0336305e9b6b5cf24caddb"
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
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c",
        "bytes": 384,
        "sha256": "a447ce7bffe4ab51cf7151f0d504d1e7a83e5cd6e715cb981a582c89f101e19f"
      },
      "reference": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/reference.bin",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/bin/ee-gcc",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-zdswaqui/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-zdswaqui/candidate.o",
              "bytes": 1716,
              "sha256": "4b9172f4787c5a0cc7816c7d51d6d12f515513a457ee6d8b291b8ead5ea97812"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-zdswaqui/prepared.o",
              "bytes": 1628,
              "sha256": "a711151893b814f6f407137b4df588a373f2453e30cfd8cfdf5fd7afe9ffe2a9"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-zdswaqui/linked.o",
              "bytes": 7524,
              "sha256": "2dd045e1f2c7e9ab6ae1d5008cf5ed6ac9ef2a4ffa406aa28f92b5f7ac4b91c8"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-zdswaqui/function.bin",
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
          "compile_stderr": "Using builtin specs.\ngcc version 2.9-ee-991111-01\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/cc1 /tools/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c -G8 -lang-c -iprefix /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/ -quiet -dumpbase candidate.c -undef -D__GNUC__=2 -D__GNUC_MINOR__=9 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float -version -ffunction-sections -O2 -o /tmp/ccVIxFJP.s\nGNU C version 2.9-ee-991111-01 (ee) compiled by GNU C version 2.7.2.3.\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/../../../../ee/bin/as -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-zdswaqui/candidate.o /tmp/ccVIxFJP.s\nGNU assembler version 2.9-ee-991111 (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "4b9172f4787c5a0cc7816c7d51d6d12f515513a457ee6d8b291b8ead5ea97812",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-zdswaqui/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-zdswaqui/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-zdswaqui/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-zdswaqui/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-zdswaqui/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-zdswaqui/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-mndkcmi7/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-mndkcmi7/candidate.o",
              "bytes": 1856,
              "sha256": "beaebc0db4ae3b7c7754423b9224bbf31e3f69121496a2597d1d58e6dcca1f6c"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-mndkcmi7/prepared.o",
              "bytes": 1700,
              "sha256": "a1fc1edbb3c2a040642f9d75ed06069d5047d881c23d0aca235b28757f80547a"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-mndkcmi7/linked.o",
              "bytes": 7524,
              "sha256": "2dd045e1f2c7e9ab6ae1d5008cf5ed6ac9ef2a4ffa406aa28f92b5f7ac4b91c8"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-mndkcmi7/function.bin",
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
          "compile_stderr": "Using builtin specs.\ngcc version 2.96-ee-001003-1\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/ -D__GNUC__=2 -D__GNUC_MINOR__=96 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccH0Gl0s.s\nGNU CPP version 2.96-ee-001003-1 (cpplib)\n [AL 1.1, MM 40] BSD Mips\nGNU C version 2.96-ee-001003-1 (ee) compiled by GNU C version 2.9-gnupro-99r1.\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/sys-include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/sys-include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/../../../../ee/bin/as -G8 -EL -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-mndkcmi7/candidate.o /tmp/ccH0Gl0s.s\nGNU assembler version 2.10-ee-001003-1 (ee) using BFD version 2.10-ee-001003\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "beaebc0db4ae3b7c7754423b9224bbf31e3f69121496a2597d1d58e6dcca1f6c",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-mndkcmi7/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-mndkcmi7/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-mndkcmi7/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-mndkcmi7/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-mndkcmi7/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-mndkcmi7/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-730b6hni/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-730b6hni/candidate.o",
              "bytes": 1640,
              "sha256": "26b2681b5f6ef5b77fdfb27cf56a6afb09929ed8290c58f94838b8ff2814e763"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-730b6hni/prepared.o",
              "bytes": 1640,
              "sha256": "1b02b1f7c3c506d7aeae37ff2e3b4396a92b958d9a22ec2561fd22e777711b25"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-730b6hni/linked.o",
              "bytes": 7488,
              "sha256": "067a64a191ad2a79c1723c929d35fc847498ae6427ba69ce9f0e2e2e6a2a870a"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-730b6hni/function.bin",
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
          "compile_stderr": "Reading specs from /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/specs\nConfigured with: /proj/ee-toolchain/ee-gcc-3.2-final-rc2/release-src/ee-gcc/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-030926\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/cctUzBmf.s\nGNU CPP version 3.2-ee-030926 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-030926 (ee)\n\tcompiled by GNU C version 3.2.\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-730b6hni/candidate.o /tmp/cctUzBmf.s\nGNU assembler version 2.12-ee-030926 (ee) using BFD version 2.12-ee-030926 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "26b2681b5f6ef5b77fdfb27cf56a6afb09929ed8290c58f94838b8ff2814e763",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-730b6hni/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-730b6hni/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-730b6hni/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-730b6hni/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-730b6hni/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-730b6hni/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-2r8p8d46/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-2r8p8d46/candidate.o",
              "bytes": 1640,
              "sha256": "26b2681b5f6ef5b77fdfb27cf56a6afb09929ed8290c58f94838b8ff2814e763"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-2r8p8d46/prepared.o",
              "bytes": 1640,
              "sha256": "1b02b1f7c3c506d7aeae37ff2e3b4396a92b958d9a22ec2561fd22e777711b25"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-2r8p8d46/linked.o",
              "bytes": 7488,
              "sha256": "067a64a191ad2a79c1723c929d35fc847498ae6427ba69ce9f0e2e2e6a2a870a"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-2r8p8d46/function.bin",
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
          "compile_stderr": "Using built-in specs.\nConfigured with: ../src/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-040921\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccGx4oE5.s\nGNU CPP version 3.2-ee-040921 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-040921 (ee)\n\tcompiled by GNU C version 3.2.2 20030222 (Red Hat Linux 3.2.2-5).\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-2r8p8d46/candidate.o /tmp/ccGx4oE5.s\nGNU assembler version 2.12-ee-040921 (ee) using BFD version 2.12-ee-040921 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "26b2681b5f6ef5b77fdfb27cf56a6afb09929ed8290c58f94838b8ff2814e763",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-2r8p8d46/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-2r8p8d46/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-2r8p8d46/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-2r8p8d46/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-2r8p8d46/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-2r8p8d46/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-lzrfpcas/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-lzrfpcas/candidate.o",
              "bytes": 1716,
              "sha256": "4b9172f4787c5a0cc7816c7d51d6d12f515513a457ee6d8b291b8ead5ea97812"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-lzrfpcas/prepared.o",
              "bytes": 1628,
              "sha256": "a711151893b814f6f407137b4df588a373f2453e30cfd8cfdf5fd7afe9ffe2a9"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-lzrfpcas/linked.o",
              "bytes": 7524,
              "sha256": "2dd045e1f2c7e9ab6ae1d5008cf5ed6ac9ef2a4ffa406aa28f92b5f7ac4b91c8"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-lzrfpcas/function.bin",
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
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.2-EE\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.2 v2 [AL 1.1, MM 40] BSD Mips\n#include \"...\" search starts here:\nEnd of search list.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.2 SN BUILD v2.73a for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-lzrfpcas/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "4b9172f4787c5a0cc7816c7d51d6d12f515513a457ee6d8b291b8ead5ea97812",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-lzrfpcas/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-lzrfpcas/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-lzrfpcas/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-lzrfpcas/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-lzrfpcas/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-lzrfpcas/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-k3ev5dbq/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-k3ev5dbq/candidate.o",
              "bytes": 1716,
              "sha256": "4b9172f4787c5a0cc7816c7d51d6d12f515513a457ee6d8b291b8ead5ea97812"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-k3ev5dbq/prepared.o",
              "bytes": 1628,
              "sha256": "a711151893b814f6f407137b4df588a373f2453e30cfd8cfdf5fd7afe9ffe2a9"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-k3ev5dbq/linked.o",
              "bytes": 7524,
              "sha256": "2dd045e1f2c7e9ab6ae1d5008cf5ed6ac9ef2a4ffa406aa28f92b5f7ac4b91c8"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-k3ev5dbq/function.bin",
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
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.05 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-114/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.14 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-k3ev5dbq/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "4b9172f4787c5a0cc7816c7d51d6d12f515513a457ee6d8b291b8ead5ea97812",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-k3ev5dbq/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-k3ev5dbq/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-k3ev5dbq/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-k3ev5dbq/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-k3ev5dbq/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-k3ev5dbq/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-l23sfwse/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-l23sfwse/candidate.o",
              "bytes": 1716,
              "sha256": "4b9172f4787c5a0cc7816c7d51d6d12f515513a457ee6d8b291b8ead5ea97812"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-l23sfwse/prepared.o",
              "bytes": 1628,
              "sha256": "a711151893b814f6f407137b4df588a373f2453e30cfd8cfdf5fd7afe9ffe2a9"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-l23sfwse/linked.o",
              "bytes": 7524,
              "sha256": "2dd045e1f2c7e9ab6ae1d5008cf5ed6ac9ef2a4ffa406aa28f92b5f7ac4b91c8"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-l23sfwse/function.bin",
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
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/misc3d_reset/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.12 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-136/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.36 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-l23sfwse/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "4b9172f4787c5a0cc7816c7d51d6d12f515513a457ee6d8b291b8ead5ea97812",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-l23sfwse/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-l23sfwse/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-l23sfwse/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-l23sfwse/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_misc3d_reset=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-l23sfwse/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/misc3d_reset/objects/fr2-compiler-probe-l23sfwse/linked.o"
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
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/manifest.json",
        "bytes": 29167,
        "sha256": "41cd6ff3cd5b2e09b7600c31a8e798176df34d4aa6f379f8113e11983161ad96"
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
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.c",
        "bytes": 551,
        "sha256": "92f4fe16d604fce7638e7a056d0db1bd60ff8f0cceb034f8fbfaec68f6cdf99e"
      },
      "reference": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/reference.bin",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/bin/ee-gcc",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-j9voiq_e/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-j9voiq_e/candidate.o",
              "bytes": 1576,
              "sha256": "44cad3392f33517b5b1d9db1280e6bc0dbbbea5010f48fff7be56e9804ef65cf"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-j9voiq_e/prepared.o",
              "bytes": 1484,
              "sha256": "f6c586a96cb83901596da970cdea97df5d4d6455c062a5e1266d54de083dc84e"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-j9voiq_e/linked.o",
              "bytes": 49372,
              "sha256": "60b672c1b43be547b8a74aab62001c530a4645f539865279a01ca0cdd2b67d8c"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-j9voiq_e/function.bin",
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
          "compile_stderr": "Using builtin specs.\ngcc version 2.9-ee-991111-01\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/cc1 /tools/compiler-profile-gsg9vgj_/entity_set_first/candidate.c -G8 -lang-c -iprefix /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/ -quiet -dumpbase candidate.c -undef -D__GNUC__=2 -D__GNUC_MINOR__=9 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float -version -ffunction-sections -O2 -o /tmp/ccY7gUCb.s\nGNU C version 2.9-ee-991111-01 (ee) compiled by GNU C version 2.7.2.3.\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/../../../../ee/bin/as -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-j9voiq_e/candidate.o /tmp/ccY7gUCb.s\nGNU assembler version 2.9-ee-991111 (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "44cad3392f33517b5b1d9db1280e6bc0dbbbea5010f48fff7be56e9804ef65cf",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-j9voiq_e/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-j9voiq_e/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-j9voiq_e/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-j9voiq_e/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-j9voiq_e/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-j9voiq_e/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-trhaycz3/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-trhaycz3/candidate.o",
              "bytes": 1744,
              "sha256": "e2b45791a8f24a50df64031c7580db199490c1127e02a1a2f03ff0841151d9bc"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-trhaycz3/prepared.o",
              "bytes": 1580,
              "sha256": "8809704b21a9d39a3c83f43a3fdc6283ae30baec77efdf3b5411efa42d130c2e"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-trhaycz3/linked.o",
              "bytes": 49396,
              "sha256": "9ba9d4d5175d8b3c0951b7378354fe75062ad82f49cf88c4cfd3789ca060a761"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-trhaycz3/function.bin",
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
          "compile_stderr": "Using builtin specs.\ngcc version 2.96-ee-001003-1\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/ -D__GNUC__=2 -D__GNUC_MINOR__=96 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/entity_set_first/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccwWasWj.s\nGNU CPP version 2.96-ee-001003-1 (cpplib)\n [AL 1.1, MM 40] BSD Mips\nGNU C version 2.96-ee-001003-1 (ee) compiled by GNU C version 2.9-gnupro-99r1.\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/sys-include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/sys-include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/../../../../ee/bin/as -G8 -EL -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-trhaycz3/candidate.o /tmp/ccwWasWj.s\nGNU assembler version 2.10-ee-001003-1 (ee) using BFD version 2.10-ee-001003\n",
          "compiler_output": {
            "status": "pass",
            "matched_bytes": 0,
            "object_sha256": "e2b45791a8f24a50df64031c7580db199490c1127e02a1a2f03ff0841151d9bc",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-trhaycz3/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-trhaycz3/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-trhaycz3/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-trhaycz3/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-trhaycz3/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-trhaycz3/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-ggbxstn1/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-ggbxstn1/candidate.o",
              "bytes": 1464,
              "sha256": "cabbe0e0cfbb2fa706da3bbce563536a8da393b267e6a397112a8636990c16c1"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-ggbxstn1/prepared.o",
              "bytes": 1464,
              "sha256": "fb3c591a472cf737f223429d2e62577c84b686ba7279ef7f932c16e234a9e273"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-ggbxstn1/linked.o",
              "bytes": 49344,
              "sha256": "1466c478b6fa54b64c3fbe625f8590449bf6b68cb368b7f54c6dddf657319959"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-ggbxstn1/function.bin",
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
          "compile_stderr": "Reading specs from /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/specs\nConfigured with: /proj/ee-toolchain/ee-gcc-3.2-final-rc2/release-src/ee-gcc/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-030926\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/entity_set_first/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccw3oFE0.s\nGNU CPP version 3.2-ee-030926 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-030926 (ee)\n\tcompiled by GNU C version 3.2.\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-ggbxstn1/candidate.o /tmp/ccw3oFE0.s\nGNU assembler version 2.12-ee-030926 (ee) using BFD version 2.12-ee-030926 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "cabbe0e0cfbb2fa706da3bbce563536a8da393b267e6a397112a8636990c16c1",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-ggbxstn1/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-ggbxstn1/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-ggbxstn1/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-ggbxstn1/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-ggbxstn1/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-ggbxstn1/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-peq25d9u/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-peq25d9u/candidate.o",
              "bytes": 1464,
              "sha256": "cabbe0e0cfbb2fa706da3bbce563536a8da393b267e6a397112a8636990c16c1"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-peq25d9u/prepared.o",
              "bytes": 1464,
              "sha256": "fb3c591a472cf737f223429d2e62577c84b686ba7279ef7f932c16e234a9e273"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-peq25d9u/linked.o",
              "bytes": 49344,
              "sha256": "1466c478b6fa54b64c3fbe625f8590449bf6b68cb368b7f54c6dddf657319959"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-peq25d9u/function.bin",
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
          "compile_stderr": "Using built-in specs.\nConfigured with: ../src/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-040921\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/entity_set_first/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/cc22OQTt.s\nGNU CPP version 3.2-ee-040921 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-040921 (ee)\n\tcompiled by GNU C version 3.2.2 20030222 (Red Hat Linux 3.2.2-5).\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-peq25d9u/candidate.o /tmp/cc22OQTt.s\nGNU assembler version 2.12-ee-040921 (ee) using BFD version 2.12-ee-040921 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "cabbe0e0cfbb2fa706da3bbce563536a8da393b267e6a397112a8636990c16c1",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-peq25d9u/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-peq25d9u/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-peq25d9u/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-peq25d9u/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-peq25d9u/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-peq25d9u/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-e6tomm8z/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-e6tomm8z/candidate.o",
              "bytes": 1596,
              "sha256": "d8bd6ffbbe4b2a6c806c28d9f1835085fe5252968dbc588e17bbe7ba5b1a334f"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-e6tomm8z/prepared.o",
              "bytes": 1504,
              "sha256": "782d96ed76e9baae8bc12101410910e29cf4390b57bb04e176c3e5d511745be1"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-e6tomm8z/linked.o",
              "bytes": 49392,
              "sha256": "1f5c7cb46f2ff54c07b64547a1f87662de5d4f1e1b5fc4ab82019a6ab9ab93d6"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-e6tomm8z/function.bin",
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
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.2-EE\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/entity_set_first/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.2 v2 [AL 1.1, MM 40] BSD Mips\n#include \"...\" search starts here:\nEnd of search list.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.2 SN BUILD v2.73a for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-e6tomm8z/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "d8bd6ffbbe4b2a6c806c28d9f1835085fe5252968dbc588e17bbe7ba5b1a334f",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-e6tomm8z/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-e6tomm8z/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-e6tomm8z/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-e6tomm8z/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-e6tomm8z/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-e6tomm8z/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-l_r6gl6b/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-l_r6gl6b/candidate.o",
              "bytes": 1596,
              "sha256": "d8bd6ffbbe4b2a6c806c28d9f1835085fe5252968dbc588e17bbe7ba5b1a334f"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-l_r6gl6b/prepared.o",
              "bytes": 1504,
              "sha256": "782d96ed76e9baae8bc12101410910e29cf4390b57bb04e176c3e5d511745be1"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-l_r6gl6b/linked.o",
              "bytes": 49392,
              "sha256": "1f5c7cb46f2ff54c07b64547a1f87662de5d4f1e1b5fc4ab82019a6ab9ab93d6"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-l_r6gl6b/function.bin",
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
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/entity_set_first/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.05 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-114/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.14 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-l_r6gl6b/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "d8bd6ffbbe4b2a6c806c28d9f1835085fe5252968dbc588e17bbe7ba5b1a334f",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-l_r6gl6b/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-l_r6gl6b/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-l_r6gl6b/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-l_r6gl6b/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-l_r6gl6b/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-l_r6gl6b/linked.o"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-vnn3iixj/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-vnn3iixj/candidate.o",
              "bytes": 1596,
              "sha256": "e2c13e2a4a6afe7f174cb7200cbb448bfea036a3bb47e97e8e59aaf1b209e2e8"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-vnn3iixj/prepared.o",
              "bytes": 1504,
              "sha256": "c31b53d1007506ffcfa80073013f99b72857ff5a7ed29dfb20b800c55d21023a"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-vnn3iixj/linked.o",
              "bytes": 49392,
              "sha256": "eced011426cc306910d7b932aefeb2d5e692fcdcf2c84e67426b62f183fd35c5"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-vnn3iixj/function.bin",
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
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/entity_set_first/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.12 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-136/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.36 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-vnn3iixj/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "e2c13e2a4a6afe7f174cb7200cbb448bfea036a3bb47e97e8e59aaf1b209e2e8",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-vnn3iixj/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-vnn3iixj/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-vnn3iixj/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-vnn3iixj/prepared.o",
            "--defsym=fr2_entity_error=0x001b0770",
            "--defsym=fr2_set_first_file=0x0025eba8",
            "--defsym=_gp=0x00295d70"
          ],
          "link_returncode": 0,
          "link_stderr": "",
          "effective_objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_entity_set_first=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-vnn3iixj/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/entity_set_first/objects/fr2-compiler-probe-vnn3iixj/linked.o"
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
      "status": "fail",
      "selected_id": null,
      "matches": [],
      "failures": [
        "ee-gcc2.9-991111-01",
        "ee-gcc2.96",
        "ee-gcc3.2-030926",
        "ee-gcc3.2-040921",
        "ee-gcc2.95.2-273a",
        "ee-gcc2.95.3-114",
        "ee-gcc2.95.3-136"
      ],
      "errors": [],
      "incomplete": [],
      "manifest": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/manifest.json",
        "bytes": 29644,
        "sha256": "ba9d5e0b63650050d7d9bc80640edee64c3520b8ccb7568de440a785eafc428d"
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
          "source_sha256": "0291458181f0285f69011bd6e926bd98966ac74bdd713e66915a0c7bef098a8d",
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
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.c",
        "bytes": 662,
        "sha256": "0291458181f0285f69011bd6e926bd98966ac74bdd713e66915a0c7bef098a8d"
      },
      "reference": {
        "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/reference.bin",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.9-991111-01/bin/ee-gcc",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2ukf6p7x/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2ukf6p7x/candidate.o",
              "bytes": 1776,
              "sha256": "72b0ea1c9596d61996d8ea16306c1943a47db7d5c9243a4c974023422e592403"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2ukf6p7x/prepared.o",
              "bytes": 1688,
              "sha256": "f9a1092c1fd52a193061f44eff1ec9fb8ab3a4708e2ba4b7a495bb1e055df457"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2ukf6p7x/linked.o",
              "bytes": 48668,
              "sha256": "c231f2936df44f423bf57ece4903d3363bb6225628b42dd3e7d50231ae393ec9"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2ukf6p7x/function.bin",
              "bytes": 96,
              "sha256": "9d963d5ea2dc433a74fb916cff4beaaf620872529187803a5096d3f9cb063d19"
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
          "compile_stderr": "Using builtin specs.\ngcc version 2.9-ee-991111-01\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/cc1 /tools/compiler-profile-gsg9vgj_/parser_lookup/candidate.c -G8 -lang-c -iprefix /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/ -quiet -dumpbase candidate.c -undef -D__GNUC__=2 -D__GNUC_MINOR__=9 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float -version -ffunction-sections -O2 -o /tmp/ccQYKNRH.s\nGNU C version 2.9-ee-991111-01 (ee) compiled by GNU C version 2.7.2.3.\n /tools/candidates/ee-gcc2.9-991111-01/bin/../lib/gcc-lib/ee/2.9-ee-991111-01/../../../../ee/bin/as -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2ukf6p7x/candidate.o /tmp/ccQYKNRH.s\nGNU assembler version 2.9-ee-991111 (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "72b0ea1c9596d61996d8ea16306c1943a47db7d5c9243a4c974023422e592403",
            "text_sha256": "acd448f18a61d71c73ca31d27dc1dce5c56a9665a4ec66c9bc50301b80621269",
            "text_bytes": 96,
            "relocations": [
              {
                "offset": 0,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 12,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 44,
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
                "offset": 48,
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
              "offset": 80,
              "reason": "function length differs",
              "expected_bytes": 80,
              "actual_bytes": 96
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2ukf6p7x/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2ukf6p7x/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2ukf6p7x/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2ukf6p7x/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2ukf6p7x/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2ukf6p7x/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "9d963d5ea2dc433a74fb916cff4beaaf620872529187803a5096d3f9cb063d19",
          "actual_bytes": 96,
          "reference_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "reference_bytes": 80,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 80,
            "first_difference": {
              "offset": 0,
              "address": "0018b840",
              "file_offset": "0008c840",
              "word": 0,
              "expected": "f0ffbd27",
              "actual": "2400023c"
            }
          },
          "reason": "function bytes differ"
        },
        {
          "id": "ee-gcc2.96",
          "status": "fail",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.96/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-f1fss23l/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-f1fss23l/candidate.o",
              "bytes": 1912,
              "sha256": "d9358068a7879666e0c591a9b99e60a0428207035ebec3b0f991eacebc52ea3d"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-f1fss23l/prepared.o",
              "bytes": 1752,
              "sha256": "d5d9da34d94ea68bbe2e252eaa174e26b28403bc658db0a947e8e0abe6615311"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-f1fss23l/linked.o",
              "bytes": 48672,
              "sha256": "0757a888dc5303b5eb66e619108e4a92914e24cccb37abc8585ec79f6efaf5c6"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-f1fss23l/function.bin",
              "bytes": 100,
              "sha256": "7b0d17ae2a9f2cd76c96bcf053dfb54795a084f652f7014ab880d2e8f78a51b8"
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
          "compile_stderr": "Using builtin specs.\ngcc version 2.96-ee-001003-1\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/ -D__GNUC__=2 -D__GNUC_MINOR__=96 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/parser_lookup/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/cchnV5RT.s\nGNU CPP version 2.96-ee-001003-1 (cpplib)\n [AL 1.1, MM 40] BSD Mips\nGNU C version 2.96-ee-001003-1 (ee) compiled by GNU C version 2.9-gnupro-99r1.\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/sys-include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc2.96/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/2.96-ee-001003-1/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/sys-include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc2.96/bin/../lib/gcc-lib/ee/2.96-ee-001003-1/../../../../ee/bin/as -G8 -EL -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-f1fss23l/candidate.o /tmp/cchnV5RT.s\nGNU assembler version 2.10-ee-001003-1 (ee) using BFD version 2.10-ee-001003\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "d9358068a7879666e0c591a9b99e60a0428207035ebec3b0f991eacebc52ea3d",
            "text_sha256": "33c4cf633f729e0c146e7ee094f33db051b9b40b7296ef20296b302dd778d887",
            "text_bytes": 100,
            "relocations": [
              {
                "offset": 4,
                "type": 5,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 12,
                "type": 6,
                "symbol_index": 11,
                "mask": "0000ffff"
              },
              {
                "offset": 36,
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
                "offset": 40,
                "type": 5,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 60,
                "type": 6,
                "symbol_index": 13,
                "mask": "0000ffff"
              },
              {
                "offset": 64,
                "type": 4,
                "symbol_index": 14,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 80,
              "reason": "function length differs",
              "expected_bytes": 80,
              "actual_bytes": 100
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-f1fss23l/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-f1fss23l/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-f1fss23l/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-f1fss23l/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-f1fss23l/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-f1fss23l/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "7b0d17ae2a9f2cd76c96bcf053dfb54795a084f652f7014ab880d2e8f78a51b8",
          "actual_bytes": 100,
          "reference_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "reference_bytes": 80,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 12,
            "section_bytes": 80,
            "first_difference": {
              "offset": 12,
              "address": "0018b84c",
              "file_offset": "0008c84c",
              "word": 3,
              "expected": "2d388000",
              "actual": "00b64524"
            }
          },
          "reason": "function bytes differ"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-030926/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-0p9gf236/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-0p9gf236/candidate.o",
              "bytes": 1636,
              "sha256": "25b87715f63d66ecc1a2787c81d5346b536abbc640b38476a714db1f43305ca1"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-0p9gf236/prepared.o",
              "bytes": 1636,
              "sha256": "f8f894a320517ddf2d82a5049e2a6cfe15f60da7727fd33f14d4359c9909e471"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-0p9gf236/linked.o",
              "bytes": 48612,
              "sha256": "e2ae917e1b9623dcf6e68855326debe01884566fc0711c8da140cad6648080c1"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-0p9gf236/function.bin",
              "bytes": 96,
              "sha256": "edc0856b406f95a0ab7fd3f6b4a1523667b2d2621f7d7831bdf48c5931265f1d"
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
          "compile_stderr": "Reading specs from /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/specs\nConfigured with: /proj/ee-toolchain/ee-gcc-3.2-final-rc2/release-src/ee-gcc/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-030926\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/parser_lookup/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/cc3IobBH.s\nGNU CPP version 3.2-ee-030926 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-030926 (ee)\n\tcompiled by GNU C version 3.2.\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-030926/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-030926/bin/../lib/gcc-lib/ee/3.2-ee-030926/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-0p9gf236/candidate.o /tmp/cc3IobBH.s\nGNU assembler version 2.12-ee-030926 (ee) using BFD version 2.12-ee-030926 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "25b87715f63d66ecc1a2787c81d5346b536abbc640b38476a714db1f43305ca1",
            "text_sha256": "dc3cc3039efe8855c73b77e591048e268c237110b9a77a517aa0269cfb566c49",
            "text_bytes": 96,
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
                "offset": 24,
                "type": 6,
                "symbol_index": 9,
                "mask": "0000ffff"
              },
              {
                "offset": 40,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 48,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 44,
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
                "offset": 56,
                "type": 4,
                "symbol_index": 12,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 80,
              "reason": "function length differs",
              "expected_bytes": 80,
              "actual_bytes": 96
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-0p9gf236/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-0p9gf236/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-0p9gf236/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-0p9gf236/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-0p9gf236/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-0p9gf236/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "edc0856b406f95a0ab7fd3f6b4a1523667b2d2621f7d7831bdf48c5931265f1d",
          "actual_bytes": 96,
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc3.2-040921/bin/ee-gcc",
            "-G8",
            "-O2",
            "-fno-optimize-sibling-calls",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-qf4rlsxy/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-qf4rlsxy/candidate.o",
              "bytes": 1636,
              "sha256": "25b87715f63d66ecc1a2787c81d5346b536abbc640b38476a714db1f43305ca1"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-qf4rlsxy/prepared.o",
              "bytes": 1636,
              "sha256": "f8f894a320517ddf2d82a5049e2a6cfe15f60da7727fd33f14d4359c9909e471"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-qf4rlsxy/linked.o",
              "bytes": 48612,
              "sha256": "e2ae917e1b9623dcf6e68855326debe01884566fc0711c8da140cad6648080c1"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-qf4rlsxy/function.bin",
              "bytes": 96,
              "sha256": "edc0856b406f95a0ab7fd3f6b4a1523667b2d2621f7d7831bdf48c5931265f1d"
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
          "compile_stderr": "Using built-in specs.\nConfigured with: ../src/configure --prefix=/usr/local/sce/ee/gcc --target=ee --enable-c-cpplib --without-sim --disable-sim --enable-c-mbchar --enable-threads\nThread model: eekernel\ngcc version 3.2-ee-040921\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/cc1 -lang-c -v -iprefix /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/ -D__GNUC__=3 -D__GNUC_MINOR__=2 -D__GNUC_PATCHLEVEL__=0 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__ee__ -D__mips__ -D__MIPSEL__ -D__R5900__ -D__mips__ -D_MIPSEL -D_R5900 -D__ee__ -D__mips -D__MIPSEL -D__R5900 -D__mips -D__OPTIMIZE__ -D__STDC_HOSTED__=1 -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__= unsigned int -D__PTRDIFF_TYPE__= int -D__mips_fpr=32 -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/parser_lookup/candidate.c -G8 -quiet -dumpbase candidate.c -O2 -version -fno-optimize-sibling-calls -ffunction-sections -o /tmp/ccIQqVez.s\nGNU CPP version 3.2-ee-040921 (cpplib) [AL 1.1, MM 40] BSD Mips\nGNU C version 3.2-ee-040921 (ee)\n\tcompiled by GNU C version 3.2.2 20030222 (Red Hat Linux 3.2.2-5).\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/tools/candidates/ee-gcc3.2-040921/ee/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/include\"\nignoring nonexistent directory \"/usr/local/sce/ee/gcc/lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/include\"\n#include \"...\" search starts here:\nEnd of search list.\n /tools/candidates/ee-gcc3.2-040921/bin/../lib/gcc-lib/ee/3.2-ee-040921/../../../../ee/bin/as -G8 -O2 -mdebug -v -o /tools/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-qf4rlsxy/candidate.o /tmp/ccIQqVez.s\nGNU assembler version 2.12-ee-040921 (ee) using BFD version 2.12-ee-040921 20020315\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "25b87715f63d66ecc1a2787c81d5346b536abbc640b38476a714db1f43305ca1",
            "text_sha256": "dc3cc3039efe8855c73b77e591048e268c237110b9a77a517aa0269cfb566c49",
            "text_bytes": 96,
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
                "offset": 24,
                "type": 6,
                "symbol_index": 9,
                "mask": "0000ffff"
              },
              {
                "offset": 40,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 48,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 44,
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
                "offset": 56,
                "type": 4,
                "symbol_index": 12,
                "mask": "03ffffff"
              }
            ],
            "claim_limit": "Non-relocated instruction bits only; no relocation, placement or byte-match proof.",
            "first_difference": {
              "offset": 80,
              "reason": "function length differs",
              "expected_bytes": 80,
              "actual_bytes": 96
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-qf4rlsxy/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-qf4rlsxy/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-qf4rlsxy/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-qf4rlsxy/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-qf4rlsxy/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-qf4rlsxy/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "edc0856b406f95a0ab7fd3f6b4a1523667b2d2621f7d7831bdf48c5931265f1d",
          "actual_bytes": 96,
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.2-273a/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-ubt59jf1/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-ubt59jf1/candidate.o",
              "bytes": 1776,
              "sha256": "8b1e6a0f1ba31c8191aebd581be749ec8e1a7327b62b6b9c365c0c9beca7945e"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-ubt59jf1/prepared.o",
              "bytes": 1688,
              "sha256": "ef9e15addff95e5dd4924a49d08177d9793e41e32a4dacc3a542bdccf1d514cd"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-ubt59jf1/linked.o",
              "bytes": 48668,
              "sha256": "395b03eb5c84f7831c76969f253e7a3b22091218d5bbe17a22dbc13ccb30cad4"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-ubt59jf1/function.bin",
              "bytes": 96,
              "sha256": "762f7f5f72a8bc108e1c3283f287b19da96d0164f9d893dfac115aa76b4caf33"
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
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.2-EE\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/parser_lookup/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.2 v2 [AL 1.1, MM 40] BSD Mips\n#include \"...\" search starts here:\nEnd of search list.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.2 SN BUILD v2.73a for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.2-273a\\bin\\..\\lib/gcc-lib/ee\\2.95.2\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-ubt59jf1/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "8b1e6a0f1ba31c8191aebd581be749ec8e1a7327b62b6b9c365c0c9beca7945e",
            "text_sha256": "90d3aea7d1e2c2b0fdda988805549ae7cdeae519a81856bbc658004b7760cd15",
            "text_bytes": 96,
            "relocations": [
              {
                "offset": 0,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 8,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 32,
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
                "offset": 36,
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
              "offset": 80,
              "reason": "function length differs",
              "expected_bytes": 80,
              "actual_bytes": 96
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-ubt59jf1/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-ubt59jf1/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-ubt59jf1/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-ubt59jf1/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-ubt59jf1/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-ubt59jf1/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "762f7f5f72a8bc108e1c3283f287b19da96d0164f9d893dfac115aa76b4caf33",
          "actual_bytes": 96,
          "reference_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "reference_bytes": 80,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 80,
            "first_difference": {
              "offset": 0,
              "address": "0018b840",
              "file_offset": "0008c840",
              "word": 0,
              "expected": "f0ffbd27",
              "actual": "2400023c"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-114/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-e_f22yoa/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-e_f22yoa/candidate.o",
              "bytes": 1776,
              "sha256": "8b1e6a0f1ba31c8191aebd581be749ec8e1a7327b62b6b9c365c0c9beca7945e"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-e_f22yoa/prepared.o",
              "bytes": 1688,
              "sha256": "ef9e15addff95e5dd4924a49d08177d9793e41e32a4dacc3a542bdccf1d514cd"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-e_f22yoa/linked.o",
              "bytes": 48668,
              "sha256": "395b03eb5c84f7831c76969f253e7a3b22091218d5bbe17a22dbc13ccb30cad4"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-e_f22yoa/function.bin",
              "bytes": 96,
              "sha256": "762f7f5f72a8bc108e1c3283f287b19da96d0164f9d893dfac115aa76b4caf33"
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
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/parser_lookup/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.05 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-114/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.14 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-114\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-e_f22yoa/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "8b1e6a0f1ba31c8191aebd581be749ec8e1a7327b62b6b9c365c0c9beca7945e",
            "text_sha256": "90d3aea7d1e2c2b0fdda988805549ae7cdeae519a81856bbc658004b7760cd15",
            "text_bytes": 96,
            "relocations": [
              {
                "offset": 0,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 8,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 32,
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
                "offset": 36,
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
              "offset": 80,
              "reason": "function length differs",
              "expected_bytes": 80,
              "actual_bytes": 96
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-e_f22yoa/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-e_f22yoa/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-e_f22yoa/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-e_f22yoa/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-e_f22yoa/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-e_f22yoa/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "762f7f5f72a8bc108e1c3283f287b19da96d0164f9d893dfac115aa76b4caf33",
          "actual_bytes": 96,
          "reference_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "reference_bytes": 80,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 80,
            "first_difference": {
              "offset": 0,
              "address": "0018b840",
              "file_offset": "0008c840",
              "word": 0,
              "expected": "f0ffbd27",
              "actual": "2400023c"
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-wine-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/candidates/ee-gcc2.95.3-136/bin/ee-gcc.exe",
            "-G8",
            "-O2",
            "-v",
            "-ffunction-sections",
            "-c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.c",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2hnrs5kq/candidate.o"
          ],
          "objcopy_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
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
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2hnrs5kq/candidate.o",
              "bytes": 1776,
              "sha256": "e67d0cb8d96f2ac5afa1819ee2e79bd72fdcdddfc371a36991024ecbdaaf8345"
            },
            "prepared_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2hnrs5kq/prepared.o",
              "bytes": 1688,
              "sha256": "322d5cdc352485eaae8b2457ebf9ca3a054bf02de3191a428d6a0d23b33dcc93"
            },
            "linked_object": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2hnrs5kq/linked.o",
              "bytes": 48668,
              "sha256": "058cfe170395ead3f00422818556804c8dad40544a007bd7688f365e4f8e2aa7"
            },
            "extracted_function": {
              "path": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2hnrs5kq/function.bin",
              "bytes": 96,
              "sha256": "f690b99b79a60a8c1bfcb82937020995c5ef0f07b0a909a36e648a580554e4cf"
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
          "compile_stderr": "wine: created the configuration directory '/root/.wine'\nwine: configuration in L\"/root/.wine\" has been updated.\nReading specs from Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\specs\ngcc driver version 2.9-ee-991111b/r4 executing gcc version 2.95.3-EE\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cpp.exe -lang-c -v -I Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\ -D__GNUC__=2 -D__GNUC_MINOR__=95 -Dmips -DMIPSEL -DR5900 -D_mips -D_MIPSEL -D_R5900 -D__mips__ -D__MIPSEL__ -D__R5900__ -D___mips__ -D_MIPSEL -D_R5900 -D__mips -D__MIPSEL -D__R5900 -D___mips -D__OPTIMIZE__ -D__LANGUAGE_C -D_LANGUAGE_C -DLANGUAGE_C -D__SIZE_TYPE__=unsigned -D__PTRDIFF_TYPE__=int -D__LONG_MAX__=9223372036854775807L -U__mips -D__mips=3 -D__mips64 -D__mips_eabi -D__mips_single_float /tools/compiler-profile-gsg9vgj_/parser_lookup/candidate.c C:\\users\\root\\Temp\\ccGaaaaa.i\nGNU CPP version 2.95.3 SN BUILD v2.12 for Sony Playstation 2\n#include \"...\" search starts here:\n#include <...> search starts here:\n Z:/tools/candidates/ee-gcc2.95.3-136/bin/../lib/gcc-lib/ee/2.95.3\n /usr/include\nEnd of search list.\nThe following default directories have been omitted from the search path:\n \n \n \n \nEnd of omitted list.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\cc1.exe C:\\users\\root\\Temp\\ccGaaaaa.i -G8 -quiet -dumpbase candidate.c -O2 -version -ffunction-sections -o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU C version 2.95.3 SN BUILD 1.36 for Playstation2 (ee) compiled by CC.\n Z:\\tools\\candidates\\ee-gcc2.95.3-136\\bin\\..\\lib/gcc-lib/ee\\2.95.3\\as.exe -G8 -O2 -v -mabi=eabi -o /tools/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2hnrs5kq/candidate.o C:\\users\\root\\Temp\\cccbaaaa.s\nGNU assembler version 2.9-ee-991111b (ee) using BFD version 2.9-ee-991111\n",
          "compiler_output": {
            "status": "fail",
            "matched_bytes": 0,
            "object_sha256": "e67d0cb8d96f2ac5afa1819ee2e79bd72fdcdddfc371a36991024ecbdaaf8345",
            "text_sha256": "ea481bd3fc588dde5bcd252a78746024327fdb003008f79a7770810c1c43c096",
            "text_bytes": 96,
            "relocations": [
              {
                "offset": 0,
                "type": 5,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 8,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 24,
                "type": 6,
                "symbol_index": 10,
                "mask": "0000ffff"
              },
              {
                "offset": 32,
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
                "offset": 36,
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
              "offset": 80,
              "reason": "function length differs",
              "expected_bytes": 80,
              "actual_bytes": 96
            }
          },
          "prepare_object_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--strip-symbol=gcc2_compiled.",
            "--strip-symbol=__gnu_compiled_c",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2hnrs5kq/candidate.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2hnrs5kq/prepared.o"
          ],
          "prepare_object_returncode": 0,
          "prepare_object_stderr": "",
          "link_argv": [
            "/bin/bash",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-ld",
            "-m",
            "elf32ltsmip",
            "-T",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/candidate.ld",
            "-o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2hnrs5kq/linked.o",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2hnrs5kq/prepared.o",
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
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/docker-linux-exec.sh",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers",
            "mips-linux-gnu-objcopy",
            "--dump-section",
            ".text.fr2_parser_lookup=/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2hnrs5kq/function.bin",
            "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_/parser_lookup/objects/fr2-compiler-probe-2hnrs5kq/linked.o"
          ],
          "objcopy_returncode": 0,
          "objcopy_stderr": "",
          "actual_sha256": "f690b99b79a60a8c1bfcb82937020995c5ef0f07b0a909a36e648a580554e4cf",
          "actual_bytes": 96,
          "reference_sha256": "5db6c503d534639373829ff7848a39c6ba4481e727b9596a4bfe54f776bbfe5d",
          "reference_bytes": 80,
          "gate": {
            "section": ".text",
            "scope": "mixed",
            "status": "fail",
            "reason": "bytes",
            "matched_bytes": 0,
            "section_bytes": 80,
            "first_difference": {
              "offset": 0,
              "address": "0018b840",
              "file_offset": "0008c840",
              "word": 0,
              "expected": "f0ffbd27",
              "actual": "2400023c"
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
    "sha256": "275ec2d410e4becbb33d99a1d7a8b7f1fb340f226ce4ccfc4f4474a15bb90673"
  },
  "local_work": "/Users/Nicolas/Documents/github/hermes/spec-5-tools/compilers/compiler-profile-gsg9vgj_",
  "historical_identity_status": "incomplete: exact corresponding compiler source/package binding remains #21; a unique panel profile is bounded to these source/flag/runtime/link inputs."
}
```
