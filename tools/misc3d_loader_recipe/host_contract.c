/* Synthetic imported-service contract. Runs hand-written source, never retail. */
#include "misc3d_loader.h"
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <string.h>

int misc3d_db_id, misc3d_state_c8, misc3d_state_cc, misc3d_state_d0, misc3d_state_d4;
void *misc3d_optional_object;
const char misc3d_source_file[]="source", misc3d_database_name[]="database";
const char misc3d_name_optional_first[]="first", misc3d_name_cc[]="cc", misc3d_name_c8[]="c8";
const char misc3d_name_d0[]="d0", misc3d_name_d4[]="d4", misc3d_name_required_a[]="a";
const char misc3d_name_required_b[]="b", misc3d_name_optional_last[]="last";
const char misc3d_error_loaded[]="loaded", misc3d_error_d4[]="missing-d4";
const char misc3d_error_required_a[]="missing-a", misc3d_error_required_b[]="missing-b";
static const char *names[]={misc3d_name_optional_first,misc3d_name_cc,misc3d_name_c8,
    misc3d_name_d0,misc3d_name_d4,misc3d_name_required_a,misc3d_name_required_b,misc3d_name_optional_last};
static int query, mode, error_line, prepared, finished, first_null, setter_a, setter_b;
static unsigned long long storage[8];
static jmp_buf trap;
int misc3d_load_database(const char *name) { assert(name==misc3d_database_name); return 0x310000; }
int misc3d_find_resource(int database,const char *name) {
    int index=query++; assert(database==0x310000 && index<8 && name==names[index]);
    /* Prior results must have reached their cells before the next lookup. */
    if(index==2)assert(misc3d_state_cc==101);
    if(index==3)assert(misc3d_state_c8==102);
    if(index==4)assert(misc3d_state_d0==103);
    if((mode==1 && (index==0||index==7)) || (mode>=2 && index==mode+2))return -1;
    return 100+index;
}
void *misc3d_resource_object(int resource) { assert(resource>=100&&resource<108); return storage; }
void misc3d_set_first_object(void *object) { first_null=object==0; }
void misc3d_prepare_object(void *object) { assert(object==storage); prepared++; assert(storage[7]==(0xfedcba9876543210ULL&~0x58ULL|0x22ULL)); }
void misc3d_set_required_a(void *object) { assert(object==storage); setter_a++; }
void misc3d_set_required_b(void *object) { assert(object==storage); setter_b++; }
void misc3d_finish_resources(void) { assert(setter_a==1&&setter_b==1); finished++; }
void misc3d_loader_error(const char *file,int line,const char *message) {
    assert(file==misc3d_source_file);
    assert(message==(line==45?misc3d_error_loaded:line==104?misc3d_error_d4:line==131?misc3d_error_required_a:misc3d_error_required_b));
    error_line=line; longjmp(trap,1);
}
int main(void) {
    int scenario;
    for(scenario=0;scenario<6;scenario++) {
        mode=scenario; query=error_line=prepared=finished=first_null=setter_a=setter_b=0;
        misc3d_db_id=scenario==5?42:-1;
        misc3d_state_c8=misc3d_state_cc=misc3d_state_d0=misc3d_state_d4=-1;
        misc3d_optional_object=(void *)&query;
        storage[7]=0xfedcba9876543210ULL;
        if(setjmp(trap)==0)fr2_misc3d_load();
        if(scenario<2) {
            assert(query==8&&error_line==0&&finished==1&&prepared==1);
            assert(first_null==(scenario==1));
            assert(misc3d_optional_object==(scenario==1?(void *)&query:(void *)storage));
            assert(misc3d_state_d4==104);
        } else {
            int expected=scenario==2?104:scenario==3?131:scenario==4?144:45;
            assert(error_line==expected&&finished==0);
            assert(query==(scenario==5?0:scenario+3));
        }
    }
    puts("PASS synthetic loader call/state/flag/error/optional contracts (6 scenarios)");
    return 0;
}
