
undefined8 FUN_00101332(void)

{
  long lVar1;
  
  FUN_00101249();
  puts("pwn sanity check ehe");
  printf("ups, i leak my secret : %p\n",FUN_00101272);
  lVar1 = ptrace(PTRACE_TRACEME,0,0,0);
  if (lVar1 < 0) {
    puts("debugger??? i thought u were better");
                    /* WARNING: Subroutine does not return */
    exit(0);
  }
  FUN_001012ce();
  return 0;
}

