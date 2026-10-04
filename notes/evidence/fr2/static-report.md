# Static: pass

3,446 functions match the saved inventory; [functions.tsv](functions.tsv) lists every entry. The complete private export hash and all provenance are retained in [static-result.json](static-result.json). Full selected bodies, blocks and references are in [loader-instructions.json](loader-instructions.json); accepted instruction evidence is in [loader-map.json](loader-map.json).

| Stage | Original Jev support / confidence / action | Final disposition |
| --- | --- | --- |
| initialization | 0.49 / 0.24 / review | accepted after independent reasoner review |
| lookup | 0.77 / 0.65 / review | accepted after independent reasoner review |
| chunk_read | 0.87 / 0.81 / auto | accepted after independent reasoner review |
| raw_transfer | 0.9 / 0.85 / auto | accepted after independent reasoner review |
| decompression | 0.87 / 0.81 / auto | accepted after independent reasoner review |
| consumption | 0.87 / 0.81 / auto | accepted after independent reasoner review |

The second audit remains visible, including its unsupported low-confidence lookup result. Complete-body review resolves the required claims; Jev review actions have not been converted to auto. Clean table correlation matches all 48 segments and 1,037 records, with a 125000 LBA adjustment. Measured runtime selects separate async entries `001069f0`/`00106ef8`. Native decompilation, exact original types and full asset semantics remain unresolved.
