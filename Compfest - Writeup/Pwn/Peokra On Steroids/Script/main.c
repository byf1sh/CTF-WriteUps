
void main(void)

{
  setvbuf(stdout,(char *)0x0,2,0);
  setvbuf(stdin,(char *)0x0,2,0);
  setvbuf(stderr,(char *)0x0,2,0);
  vuln();
                    /* WARNING: Subroutine does not return */
  exit(1);
}

