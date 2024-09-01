
undefined8 FUN_001012ce(void)

{
  size_t sVar1;
  char local_28 [32];
  
  puts("try to hack me, if you can~");
  gets(local_28);
  sVar1 = strlen(local_28);
  if (10 < sVar1) {
    puts("u yap alot, that wont do :/");
                    /* WARNING: Subroutine does not return */
    exit(0);
  }
  puts("see ya");
  return 0;
}

