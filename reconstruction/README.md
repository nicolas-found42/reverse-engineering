# Reconstruction and drafts

This tree holds hand-written reconstruction permitted by
[LEGAL](../docs/LEGAL.md). The tracked
[misc3d database-id unit](ee/app3d/misc3d_db_id.c) is a bounded source-built probe;
its [evidence](../notes/evidence/fr2-first-unit/README.md) and
[ownership decision](../docs/adr/0005-game-owned-sdk-boundary.md) define its scope.

Use [drafts](drafts/README.md) for hand-written incomplete candidates. Drafts are
unbuilt by default: no scanner, report or wildcard build may treat their presence
as matched, complete or owned bytes. A near miss stays a draft with its failed
comparison and unresolved interfaces. Moving a draft into a source unit requires
a measured boundary, exact build/placement checks and retained negative controls.

Generated C, assembly and copied corpus/source material are forbidden here.
Original names and translation-unit structure require evidence; naming a file
after an address does not establish an original function.
