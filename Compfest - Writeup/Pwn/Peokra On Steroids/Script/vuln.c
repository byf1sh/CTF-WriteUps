
/* WARNING: Removing unreachable block (ram,0x0010142a) */
/* WARNING: Removing unreachable block (ram,0x00101430) */

int vuln(void)

{
  int iVar1;
  ssize_t sVar2;
  long in_FS_OFFSET;
  int local_3c;
  int local_38;
  int i;
  char *local_30;
  char buffer [24];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  local_30 = buffer;
  local_3c = 0;
  puts("Halo, aku Peokra!! Aku bikin program yang bisa nerima input dari kalian.");
  printf(&DAT_001020b0);
  __isoc99_scanf(&DAT_001020f4,&local_3c);
  local_30 = local_30 + (long)local_3c * 4;
  puts("Sekarang input, tapi kalian gak boleh masukin huruf \'n\' ya:");
  sVar2 = read(0,buffer,16);
  local_3c = (int)sVar2;
  local_38 = 1;
  i = 0;
  do {
    if (local_3c + -1 <= i) {
LAB_0010144e:
      if (local_38 == 0) {
        puts(&DAT_00102138);
        iVar1 = 0;
      }
      else {
        printf("Kamu menginput: ");
        iVar1 = printf(buffer);
      }
      if (local_10 == *(long *)(in_FS_OFFSET + 0x28)) {
        return iVar1;
      }
                    /* WARNING: Subroutine does not return */
      __stack_chk_fail();
    }
    if (buffer[i] == 'n') {
      local_38 = 0;
      goto LAB_0010144e;
    }
    i = i + 1;
  } while( true );
}

