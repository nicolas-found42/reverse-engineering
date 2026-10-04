// SPDX-License-Identifier: GPL-3.0-or-later
// Assertion body composed with exact pristine and patched emitter templates
// by verify_ee_fpu_experiment.py. This is synthetic-only; no game code runs.
int main() {
 std::fesetround(FE_TONEAREST);
 auto bits=[](float v){uint32_t b;std::memcpy(&b,&v,4);return b;};
 auto req=[](bool ok,const char *s){if(!ok){std::fprintf(stderr,"FAIL %s\n",s);std::exit(1);}};
 req(base_cvt(1.75f)==2 && cand_cvt(1.75f)==1,"actual CVT.W.S +fraction baseline fail/candidate pass");
 req(base_cvt(-1.75f)==-2 && cand_cvt(-1.75f)==-1,"actual CVT.W.S -fraction baseline fail/candidate pass");
 req(cand_cvt(1073741824.0f)==1073741824 && cand_cvt(-1073741824.0f)==-1073741824,"actual CVT.W.S exponent boundary");
 req(cand_cvt(2147483648.0f)==INT32_MAX && cand_cvt(-2147483904.0f)==INT32_MIN,"actual CVT.W.S guarded saturation");
 uint32_t zf=0;
 req(bits(base_min(+0.0f,-0.0f))!=0x80000000u && bits(cand_min(+0.0f,-0.0f,zf))==0x80000000u,"actual MIN.S (+0,-0) negative control");
 zf=0;req(bits(cand_min(-0.0f,+0.0f,zf))==0x80000000u,"actual MIN.S (-0,+0)");
 zf=0;req(bits(cand_min(+0.0f,+0.0f,zf))==0,"actual MIN.S (+0,+0)");
 zf=0;req(bits(cand_min(-0.0f,-0.0f,zf))==0x80000000u,"actual MIN.S (-0,-0)");
 zf=0;
 req(bits(base_max(-0.0f,+0.0f))!=0 && bits(cand_max(-0.0f,+0.0f,zf))==0,"actual MAX.S (-0,+0) negative control");
 zf=0;req(bits(cand_max(+0.0f,-0.0f,zf))==0,"actual MAX.S (+0,-0)");
 zf=0;req(bits(cand_max(+0.0f,+0.0f,zf))==0,"actual MAX.S (+0,+0)");
 zf=0;req(bits(cand_max(-0.0f,-0.0f,zf))==0x80000000u,"actual MAX.S (-0,-0)");
 uint32_t f=0xffffffffu; (void)cand_min(0.0f,-0.0f,f); req(f==(0xffffffffu&~0xc000u),"MIN.S only clears O/U cause");
 f=0xffffffffu; (void)cand_max(0.0f,-0.0f,f); req(f==(0xffffffffu&~0xc000u),"MAX.S only clears O/U cause");
 f=0xa5a5ffffu & ~(0x00030000u|0x40u); uint32_t before=f;
 req(bits(base_sqrt(-4.0f,f))!=bits(2.0f),"actual SQRT.S negative baseline control");
 f=0xa5a5ffffu & ~(0x00030000u|0x40u); before=f;
 req(bits(cand_sqrt(-4.0f,f))==bits(2.0f),"actual SQRT.S negative perfect square");
 req((f&0x00030000u)==0x00020000u && (f&0x40u),"SQRT.S sets I/SI and clears D");
 req((f&~(0x00030000u|0x40u))==(before&~(0x00030000u|0x40u)),"SQRT.S preserves unrelated cause/sticky/control bits");
 f=0xffffffffu; before=f;
 req(bits(cand_sqrt(4.0f,f))==bits(2.0f),"SQRT.S positive exact root");
 req((f&0x00030000u)==0,"SQRT.S positive root clears I/D cause bits");
 req((f&~0x00030000u)==(before&~0x00030000u),"SQRT.S positive root preserves sticky and unrelated bits");
 f=0xffffffffu; before=f; req(bits(cand_sqrt(-0.0f,f))==0x80000000u,"SQRT.S preserves negative zero");
 req((f&0x30000u)==0 && (f&~0x30000u)==(before&~0x30000u),"SQRT.S zero clears causes only");
 req(std::isnan(base_sqrt(-4.0f,f)),"baseline sqrtf negative yields host NaN");
 std::puts("PASS: exact pristine/patched emitter templates; bounded manual-derived controls");
}
