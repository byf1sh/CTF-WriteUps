
void FUN_00101272(void)

{
  char local_118 [264];
  FILE *local_10;
  
  puts("ret2win or ret2me mwehehe");
  local_10 = fopen("flag.txt","r");
  fgets(local_118,0x100,local_10);
  puts(local_118);
  return;
}

