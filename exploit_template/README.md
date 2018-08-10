# Exploit Docker Template

A Dockerfile template for building an exploit in Git-based CTF. An exploit in
Git-based CTF is a program running in a Docker container.

# Usage

You can modify the [`Dockerfile`](Dockerfile) to create an exploit docker. In
the Dockerfile, you should place your exploit script at `/bin/exploit`. Your
exploit script/program (`/bin/exploit`) should take both ip and port number as
command-line arguments: you should be able to run the exploit with `/bin/exploit
[ip] [port]`. Your exploit should read the flag placed in `/var/ctf/flag` and
print it to standard output.

# Example

Below is an example that shows how you can create an exploit docker. We assume
that a simple shell service is running at port 4000: `nc -l -p 4000 -e /bin/sh`.

1. Modify the Dockerfile as follows.

    ```dockerfile
    FROM debian:latest

    # =========Install your package=========
    RUN apt-get update && apt-get install -y \
          make \
          gcc  \
          python
    # ======================================

    # ======================================
    # Build your exploit here
    # ======================================


    # ======Build and run your exploit=====
    COPY exploit /bin/
    # ======================================
    ```

2. Create a python script `./exploit` and make it executable: `chmod +x
   ./exploit`. The script should look as follows:

    #### exploit
    ```python
    #!/usr/bin/env python

    from socket import *
    import sys

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    BUFSIZE = 1024
    ADDR = (HOST, PORT)

    s = socket(AF_INET, SOCK_STREAM)
    try:
        s.connect(ADDR)
    except Exception as e:
        print('Cannot connect to the server.')
        sys.exit()

    s.send('cat /var/ctf/flag\n')
    flag = s.recv(BUFSIZE)
    flag = flag.rstrip()
    sys.stdout.write(flag)
    ```

3. Run the [gitctf script](../scripts): `./gitctf.py exec exploit --exploit-dir
   [DIR] --service-name SrvName --ip 127.0.0.1 --port 4000`. Assuming that the
   target service is running at localhost port 4000, you can simply run:
   ``./gitctf.py exec exploit --exploit-dir [DIR] --service-name SrvName``.
