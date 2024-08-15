# Compfest Definitely Safe Safe Program Writeup

### Source Code

In this challenge, the following code was provided:

```python
"""
Welcome to my first Python program!!!

This program will be able to execute most Python
statements just like the REPL, but I have made sure
to sanitize the input so you won't be able to hack
my computer!!!

But... if you somehow managed to hack my computer
here is a gift from me COMPFEST16{PART1_
"""

__file__ = "Nothing here..."

def safe(s):
    blacklist = ["os", "system", "\\", "(", ")", "io", "subprocess", "Popen", "=", "0", "1", "2", "+", "3", "4", "5", "PART2}","6", "7", "8", "9", "import", "-", "globals", "locals", "vars"]
    return not any(c in s for c in blacklist)


if __name__ == "__main__":
    while True:
        cmd = ascii(input(">>> "))
        print(cmd)
        if not safe(cmd):
            print("Not Allowed!!!")
            continue
            
        result = eval(eval(cmd))
        print(str(result)[:25])
```

The comment section explains that this program is similar to the Python `REPL`, and we might be able to use some commands to retrieve the flag.

Even though this code is designed like a Python `REPL`, many keywords are blacklisted such as `os`, `(`, `)`, `import`, `subprocess`, and many more, making it almost impossible to execute Remote Code Execution (RCE) on this program.

However, we can leverage Python dunder methods and code objects to retrieve the flag. Here are some interesting articles about dunder methods and code objects:

- [Functions and Code Objects](https://www.codeguage.com/courses/python/functions-code-objects)
- [Printing Python File's Docstring](https://stackoverflow.com/questions/7791574/how-can-i-print-a-python-files-docstring-when-executing-it)

### Flag Part 1

Reading the first part of the flag is fairly simple. By using the `__doc__` command, we can read the contents of the comment section or the document's docstring. However, the program only displays the first 25 characters, which presents a challenge.

We can use a command like `__doc__[281:]` to print the comment starting from the 281st character to the end, which will give us the first part of the flag. The problem is that we can't input numbers directly because all numbers are blacklisted.

To write numbers in `__doc__[<number>:]`, we can use the dunder method code objects that return numbers. Here's an example:

```python
>>> safe.__code__.co_argcount
1
>>> safe.__code__.co_firstlineno
15
>>> safe.__code__.co_stacksize
4
>>> safe.__code__.co_flags
3
```

We know that the flag starts at the 281st character, so we can use the above return values to write 281 in `__doc__` to get the first part of the flag. Here's an example:

```python
>>> safe.__code__.co_stacksize * safe.__code__.co_flags
12
>>> __doc__[safe.__code__.co_firstlineno**safe.__code__.co_flags // result:]
COMPFEST16{fake_flag_:v
```

The code above will print the docstring starting from the 281st character to the end, giving us the first part of the flag.

### Flag Part 2

To retrieve the second part of the flag, we need to look at the contents of the blacklist array, and the flag is located at the 17th element in the array. To view the flag, we can use Python code objects to retrieve it. Here's an example:

```python
# To get the flag, we need to execute the command safe.__code__.co_varnames[1][17]
# We can leverage code objects that return numbers to retrieve the flag
>>> safe.__code__.co_consts[safe.__code__.co_argcount][safe.__code__.co_stacksize * safe.__code__.co_stacksize]
th1s_1s_f4k3_fl4gg783s9dD
```

Thank you.
