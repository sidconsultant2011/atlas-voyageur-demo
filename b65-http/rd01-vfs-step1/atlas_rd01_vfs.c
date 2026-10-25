/* ATLAS SEC01 RD01 prequalification G01/G02, isolated, NO crash injection. */
#define _POSIX_C_SOURCE 200809L
#include <sqlite3.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
typedef struct {sqlite3_file base;sqlite3_file *inner;char role[40];} Obs;
static sqlite3_vfs *parent;
static sqlite3_vfs wrapper;
static int output=-1;
static unsigned long serial=0;
static void emit(const char *ev,const char *role,int rc,int flags,const char *path){
 if(output<0)return;
 const char *base=path?strrchr(path,'/'):0;
 base=path?(base?base+1:path):"-";
 char buffer[512];
 int n=snprintf(buffer,sizeof(buffer),"%lu\t%ld\t%s\t%s\t%d\t%d\t%s\n",++serial,(long)getpid(),ev,role?role:"other",rc,flags,base);
 if(n>0&&n<(int)sizeof(buffer))(void)write(output,buffer,(size_t)n);
}
static const char *role(const char*z,int f){
 if(f&SQLITE_OPEN_MAIN_DB)return "main-db";
 if(f&SQLITE_OPEN_MAIN_JOURNAL)return "main-journal";
 if(f&SQLITE_OPEN_MASTER_JOURNAL)return "super-journal-candidate";
 if(f&SQLITE_OPEN_WAL)return "wal";
 if(z&&strstr(z,"-journal"))return "rollback-journal";
 if(z&&strstr(z,".sqlite"))return "attached-or-main-db";
 return "other";
}
static int cl(sqlite3_file*f){Obs*w=(Obs*)f;int r=w->inner->pMethods->xClose(w->inner);emit("xClose",w->role,r,0,0);free(w->inner);return r;}
static int rd(sqlite3_file*f,void*b,int n,sqlite3_int64 o){Obs*w=(Obs*)f;return w->inner->pMethods->xRead(w->inner,b,n,o);}
static int wr(sqlite3_file*f,const void*b,int n,sqlite3_int64 o){Obs*w=(Obs*)f;int r=w->inner->pMethods->xWrite(w->inner,b,n,o);emit("xWrite",w->role,r,n,0);return r;}
static int tr(sqlite3_file*f,sqlite3_int64 n){Obs*w=(Obs*)f;return w->inner->pMethods->xTruncate(w->inner,n);}
static int sy(sqlite3_file*f,int n){Obs*w=(Obs*)f;int r=w->inner->pMethods->xSync(w->inner,n);emit("xSync",w->role,r,n,0);return r;}
static int sz(sqlite3_file*f,sqlite3_int64*n){Obs*w=(Obs*)f;return w->inner->pMethods->xFileSize(w->inner,n);}
static int lk(sqlite3_file*f,int n){Obs*w=(Obs*)f;return w->inner->pMethods->xLock(w->inner,n);}
static int ul(sqlite3_file*f,int n){Obs*w=(Obs*)f;return w->inner->pMethods->xUnlock(w->inner,n);}
static int rs(sqlite3_file*f,int*n){Obs*w=(Obs*)f;return w->inner->pMethods->xCheckReservedLock(w->inner,n);}
static int fc(sqlite3_file*f,int n,void*p){Obs*w=(Obs*)f;int r=w->inner->pMethods->xFileControl(w->inner,n,p);emit("xFileControl",w->role,r,n,0);return r;}
static int ss(sqlite3_file*f){Obs*w=(Obs*)f;return w->inner->pMethods->xSectorSize(w->inner);}
static int dc(sqlite3_file*f){Obs*w=(Obs*)f;return w->inner->pMethods->xDeviceCharacteristics(w->inner);}
static const sqlite3_io_methods io={1,cl,rd,wr,tr,sy,sz,lk,ul,rs,fc,ss,dc};
static int op(sqlite3_vfs*v,const char*z,sqlite3_file*f,int flags,int*out){
 (void)v;Obs*w=(Obs*)f;memset(w,0,sizeof(*w));w->inner=calloc(1,(size_t)parent->szOsFile);
 if(!w->inner)return SQLITE_NOMEM;
 snprintf(w->role,sizeof(w->role),"%s",role(z,flags));
 int r=parent->xOpen(parent,z,w->inner,flags,out);
 emit("xOpen",w->role,r,flags,z);
 if(r==SQLITE_OK)w->base.pMethods=&io;else{free(w->inner);w->inner=0;}
 return r;
}
static int de(sqlite3_vfs*v,const char*z,int n){(void)v;int r=parent->xDelete(parent,z,n);emit("xDelete",role(z,0),r,n,z);return r;}
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
int atlas_rd01_register(const char*path){
 parent=sqlite3_vfs_find(0);if(!parent)return SQLITE_NOTFOUND;
 output=open(path,O_WRONLY|O_CREAT|O_TRUNC|O_CLOEXEC,0600);if(output<0)return SQLITE_CANTOPEN;
 wrapper=*parent;wrapper.zName="atlas_rd01_observer";wrapper.szOsFile=sizeof(Obs);wrapper.iVersion=2;
 wrapper.xOpen=op;wrapper.xDelete=de;wrapper.xAccess=ac;wrapper.xFullPathname=fp;
 wrapper.xDlOpen=dl;wrapper.xDlError=er;wrapper.xDlSym=ds;wrapper.xDlClose=dc2;
 wrapper.xRandomness=ra;wrapper.xSleep=sl;wrapper.xCurrentTime=ti;wrapper.xGetLastError=le;wrapper.xCurrentTimeInt64=t64;
 int r=sqlite3_vfs_register(&wrapper,0);emit("registered",parent->zName,r,sqlite3_libversion_number(),0);return r;
}
const char *atlas_rd01_sqlite_version(void){return sqlite3_libversion();}
const void *atlas_rd01_sqlite_symbol(void){return (const void*)&sqlite3_vfs_find;}
