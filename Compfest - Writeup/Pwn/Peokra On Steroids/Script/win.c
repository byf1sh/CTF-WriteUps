
int win(void)

{
  int iVar1;
  FILE *__stream;
  long in_FS_OFFSET;
  char local_118 [264];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  puts("Semoga masih gampang banged yh");
  __stream = fopen("flag.txt","r");
  if (__stream == (FILE *)0x0) {
    printf("File flag.txt does not exist! >:(");
    iVar1 = 0x45;
  }
  else {
    fgets(local_118,0x100,__stream);
    iVar1 = puts(local_118);
  }
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return iVar1;
}

