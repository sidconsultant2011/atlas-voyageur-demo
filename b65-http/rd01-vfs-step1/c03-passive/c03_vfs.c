/* ATLAS SEC01 C03-3: separate experimental VFS, normal COMMIT only.
   No xDelete BEFORE_DELEGATE, no fault injection, no live journal reads. */
#define _POSIX_C_SOURCE 200809L
#include <sqlite3.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define MAX_FILES 16
#define MAX_BYTES (1024*1024)
typedef struct {sqlite3_file base; sqlite3_file *inner; int slot;} Obs;
typedef struct {char path[1024]; unsigned char *data,*present; size_t size; int generation,kind,closed,deleted,error,writes,truncates;} Record;
static sqlite3_vfs *parent; static sqlite3_vfs wrapper;
static Record rec[MAX_FILES]; static int used=0,overflow=0;
static int kind_for(int f){if(f&SQLITE_OPEN_MASTER_JOURNAL)return 2;if(f&SQLITE_OPEN_MAIN_JOURNAL)return 1;return 0;}
static int record_open(const char*z,int kind){
 if(!z||!kind)return -1;
 if(used>=MAX_FILES){overflow=1;return -1;}
 int i=used++;Record*r=&rec[i];memset(r,0,sizeof(*r));
 if(strlen(z)>=sizeof(r->path)){overflow=1;r->error=1;return -1;}
 strcpy(r->path,z);r->kind=kind;r->generation=i+1;
 r->data=calloc(MAX_BYTES,1);r->present=calloc(MAX_BYTES,1);
 if(!r->data||!r->present){overflow=1;r->error=1;}
 return i;
}
static int cl(sqlite3_file*f){Obs*w=(Obs*)f;int r=w->inner->pMethods->xClose(w->inner);if(w->slot>=0)rec[w->slot].closed=1;free(w->inner);return r;}
static int rd(sqlite3_file*f,void*b,int n,sqlite3_int64 o){Obs*w=(Obs*)f;return w->inner->pMethods->xRead(w->inner,b,n,o);}
static int wr(sqlite3_file*f,const void*b,int n,sqlite3_int64 o){
 Obs*w=(Obs*)f;int ok=w->inner->pMethods->xWrite(w->inner,b,n,o);
 if(w->slot>=0){Record*r=&rec[w->slot];r->writes++;
  if(ok!=SQLITE_OK||n<0||o<0||(uint64_t)o+(uint64_t)n>MAX_BYTES||!r->data||!r->present){r->error=1;overflow=1;}
  else{memcpy(r->data+o,b,(size_t)n);memset(r->present+o,1,(size_t)n);if((size_t)(o+n)>r->size)r->size=(size_t)(o+n);}}
 return ok;
}
static int tr(sqlite3_file*f,sqlite3_int64 n){Obs*w=(Obs*)f;int result=w->inner->pMethods->xTruncate(w->inner,n);if(w->slot>=0){Record*r=&rec[w->slot];r->truncates++;if(result!=SQLITE_OK||n<0||n>MAX_BYTES){r->error=1;overflow=1;}else {if((size_t)n<r->size){memset(r->present+n,0,r->size-(size_t)n);memset(r->data+n,0,r->size-(size_t)n);}r->size=(size_t)n;}}return result;}
static int sy(sqlite3_file*f,int n){Obs*w=(Obs*)f;return w->inner->pMethods->xSync(w->inner,n);}
static int sz(sqlite3_file*f,sqlite3_int64*n){Obs*w=(Obs*)f;return w->inner->pMethods->xFileSize(w->inner,n);}
static int lk(sqlite3_file*f,int n){Obs*w=(Obs*)f;return w->inner->pMethods->xLock(w->inner,n);}
static int ul(sqlite3_file*f,int n){Obs*w=(Obs*)f;return w->inner->pMethods->xUnlock(w->inner,n);}
static int rs(sqlite3_file*f,int*n){Obs*w=(Obs*)f;return w->inner->pMethods->xCheckReservedLock(w->inner,n);}
static int fc(sqlite3_file*f,int n,void*p){Obs*w=(Obs*)f;return w->inner->pMethods->xFileControl(w->inner,n,p);}
static int ss(sqlite3_file*f){Obs*w=(Obs*)f;return w->inner->pMethods->xSectorSize(w->inner);}
static int dc(sqlite3_file*f){Obs*w=(Obs*)f;return w->inner->pMethods->xDeviceCharacteristics(w->inner);}
static const sqlite3_io_methods io={1,cl,rd,wr,tr,sy,sz,lk,ul,rs,fc,ss,dc};
static int op(sqlite3_vfs*v,const char*z,sqlite3_file*f,int flags,int*out){
 (void)v;Obs*w=(Obs*)f;memset(w,0,sizeof(*w));w->slot=-1;
 w->inner=calloc(1,(size_t)parent->szOsFile);if(!w->inner)return SQLITE_NOMEM;
 int result=parent->xOpen(parent,z,w->inner,flags,out);
 if(result==SQLITE_OK){w->base.pMethods=&io;int kind=kind_for(flags);if(kind){w->slot=record_open(z,kind);if(w->slot<0)overflow=1;}}
 else{free(w->inner);w->inner=0;}
 return result;
}
/* C03-R02: result of native xDelete and certainty of file attribution
   are independent. No observation can rewrite a native SQLite result.
   A closed historical incarnation not yet proven deleted remains a candidate. */
static int deletion_events=0,delete_assigned=0,delete_ambiguous=0;
static int delete_no_match=0,delete_failed=0,delete_unclosed=0;
static int attribute_delete(const char*z,int native_result){
 deletion_events++;
 if(native_result!=SQLITE_OK){delete_failed++;return native_result;}
 if(!z){delete_no_match++;return native_result;}
 int candidate=-1,count=0;
 for(int i=0;i<used;i++){
  if(!rec[i].deleted && strcmp(rec[i].path,z)==0){
   candidate=i;count++;
  }
 }
 if(count==0){delete_no_match++;return native_result;}
 if(count!=1){delete_ambiguous++;return native_result;}
 /* xClose is a positive lifecycle signal, not a proof of inode identity.
    Require one closed, otherwise still-open candidate for proof rejection. */
 if(!rec[candidate].closed){delete_unclosed++;return native_result;}
 rec[candidate].deleted=1;
 delete_assigned++;
 return native_result;
}
static int de(sqlite3_vfs*v,const char*z,int n){
 (void)v;
 int result=parent->xDelete(parent,z,n);
 return attribute_delete(z,result);
}
/* Test-only seams: replay synthetic lifecycle cases, without OS file deletion.
   They exercise exactly the helper called AFTER the native xDelete callback. */
void c03_test_reset(void){
 for(int i=0;i<used;i++){free(rec[i].data);free(rec[i].present);}
 memset(rec,0,sizeof(rec));used=0;overflow=0;
 deletion_events=delete_assigned=delete_ambiguous=0;
 delete_no_match=delete_failed=delete_unclosed=0;
}
int c03_test_open(const char*z,int kind,int closed){
 int slot=record_open(z,kind);
 if(slot>=0)rec[slot].closed=closed?1:0;
 return slot;
}
int c03_test_delete(const char*z,int native_result){
 return attribute_delete(z,native_result);
}
int c03_delete_stats(int*events,int*assigned,int*ambiguous,int*unmatched,int*failed,int*unclosed){
 if(!events||!assigned||!ambiguous||!unmatched||!failed||!unclosed)return -1;
 *events=deletion_events;*assigned=delete_assigned;
 *ambiguous=delete_ambiguous;*unmatched=delete_no_match;
 *failed=delete_failed;*unclosed=delete_unclosed;
 return 0;
}
static int ac(sqlite3_vfs*v,const char*z,int n,int*out){(void)v;return parent->xAccess(parent,z,n,out);}
static int fp(sqlite3_vfs*v,const char*z,int n,char*out){(void)v;return parent->xFullPathname(parent,z,n,out);}
static void* dl(sqlite3_vfs*v,const char*z){(void)v;return parent->xDlOpen(parent,z);}
static void er(sqlite3_vfs*v,int n,char*z){(void)v;parent->xDlError(parent,n,z);}
static void(*ds(sqlite3_vfs*v,void*h,const char*z))(void){(void)v;return parent->xDlSym(parent,h,z);}
static void dc2(sqlite3_vfs*v,void*h){(void)v;parent->xDlClose(parent,h);}
static int ra(sqlite3_vfs*v,int n,char*z){(void)v;return parent->xRandomness(parent,n,z);}
static int sl(sqlite3_vfs*v,int n){(void)v;return parent->xSleep(parent,n);}
static int ti(sqlite3_vfs*v,double*d){(void)v;return parent->xCurrentTime(parent,d);}
static int le(sqlite3_vfs*v,int n,char*z){(void)v;return parent->xGetLastError?parent->xGetLastError(parent,n,z):0;}
static int t64(sqlite3_vfs*v,sqlite3_int64*n){(void)v;return parent->xCurrentTimeInt64?parent->xCurrentTimeInt64(parent,n):SQLITE_ERROR;}
int c03_register(void){
 parent=sqlite3_vfs_find(0);if(!parent)return SQLITE_NOTFOUND;
 wrapper=*parent;wrapper.zName="atlas_c03_passive";wrapper.szOsFile=sizeof(Obs);wrapper.iVersion=2;
 wrapper.xOpen=op;wrapper.xDelete=de;wrapper.xAccess=ac;wrapper.xFullPathname=fp;
 wrapper.xDlOpen=dl;wrapper.xDlError=er;wrapper.xDlSym=ds;wrapper.xDlClose=dc2;
 wrapper.xRandomness=ra;wrapper.xSleep=sl;wrapper.xCurrentTime=ti;wrapper.xGetLastError=le;wrapper.xCurrentTimeInt64=t64;
 return sqlite3_vfs_register(&wrapper,0);
}
int c03_overflow(void){return overflow;}
int c03_count(void){return used;}
int c03_info(int idx,char*path,int cap,int*kind,int*generation,int*closed,int*deleted,int*error,int*writes,int*truncates){
 if(idx<0||idx>=used||cap<1)return -1;
 Record*r=&rec[idx];if((int)strlen(r->path)>=cap)return -2;
 strcpy(path,r->path);*kind=r->kind;*generation=r->generation;*closed=r->closed;*deleted=r->deleted;
 *error=r->error;*writes=r->writes;*truncates=r->truncates;return (int)r->size;
}
int c03_copy(int idx,unsigned char*bytes,unsigned char*present,int cap){
 if(idx<0||idx>=used||cap<(int)rec[idx].size)return -1;
 Record*r=&rec[idx];memcpy(bytes,r->data,r->size);memcpy(present,r->present,r->size);return (int)r->size;
}
const char*c03_sqlite_version(void){return sqlite3_libversion();}
const void*c03_sqlite_symbol(void){return (const void*)&sqlite3_vfs_find;}
