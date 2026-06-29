# curl the duck — v1t CTF 2026

**Category:** Misc  
**Flag:** `v1t{ducky_quacky}`

---

## Process

Visit `v1t.site/duck` — save the response (use `-L` to follow redirects):

```
curl -L v1t.site/duck -o duck
```

Inspect the binary:

```
strings duck
```

Output is full of ANSI escape sequences (`[0;31m`, `[38;5;223;49m`, etc.), but buried in the noise is an endpoint list:

```
$ curl v1t.site/ping
$ curl v1t.site/help
$ curl v1t.site/duck    -> Duck
$ curl v1t.site/flag    -> Flag for v1t ctf 2026
```

Fetch the flag endpoint:

```
curl -L v1t.site/flag -o flag
```

The raw file wraps every character in ANSI color codes — the terminal renders colored art but the flag text is unreadable as-is. Strip the escape sequences:

```
cat flag | sed 's/\x1b\[[0-9;]*m//g'
```

- `\x1b` — ESC byte (0x1b)
- `\[[0-9;]*m` — bracket + numeric params + `m` terminator
- removes all color/style sequences, leaving plain ASCII

Result:

```
             ████   █████        ███     █████                     █████                                                                   █████                 ███    
            ░░███  ░░███        ██░     ░░███                     ░░███                                                                   ░░███                 ░░░██   
 █████ █████ ░███  ███████     ██     ███████  █████ ████  ██████  ░███ █████ █████ ████            ████████ █████ ████  ██████    ██████  ░███ █████ █████ ████  ░░██  
░░███ ░░███  ░███ ░░░███░    ███     ███░░███ ░░███ ░███  ███░░███ ░███░░███ ░░███ ░███            ███░░███ ░░███ ░███  ░░░░░███  ███░░███ ░███░░███ ░░███ ░███    ░░███
 ░███  ░███  ░███   ░███    ░░░██   ░███ ░███  ░███ ░███ ░███ ░░░  ░██████░   ░███ ░███           ░███ ░███  ░███ ░███   ███████ ░███ ░░░  ░██████░   ░███ ░███     ██░ 
 ░░███ ███   ░███   ░███ ███  ░░██  ░███ ░███  ░███ ░███ ░███  ███ ░███░░███  ░███ ░███           ░███ ░███  ░███ ░███  ███░░███ ░███  ███ ░███░░███  ░███ ░███    ██   
  ░░█████    █████  ░░█████    ░░███░░████████ ░░████████░░██████  ████ █████ ░░███████  █████████░░███████  ░░████████░░████████░░██████  ████ █████ ░░███████  ███    
   ░░░░░    ░░░░░    ░░░░░      ░░░  ░░░░░░░░   ░░░░░░░░  ░░░░░░  ░░░░ ░░░░░   ░░░░░███ ░░░░░░░░░  ░░░░░███   ░░░░░░░░  ░░░░░░░░  ░░░░░░  ░░░░ ░░░░░   ░░░░░███ ░░░     
                                                                               ███ ░███                ░███                                            ███ ░███         
                                                                              ░░██████                 █████                                          ░░██████          
                                                                               ░░░░░░                 ░░░░░                                            ░░░░░░           
```

Block letters spell out: `v1t{ducky_quacky}`

---

**Flag:** `v1t{ducky_quacky}`
