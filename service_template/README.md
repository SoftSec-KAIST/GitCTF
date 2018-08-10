# Service Docker Template

A Dockerfile template for preparing a Git-based CTF service.

# Usage

You are free to modify the [`Dockerfile`](Dockerfile), but remember to not touch
the base image, and to `COPY` the flag file into the `/var/ctf` directory. The
`flag` file can be filled with a random string. This file is used to prove the
exploitability of an attack against your service. You can run your service in a
Docker container with `gitctf.py`.

# Example

Below is an example that shows how you can run a simple echo server inside a
Docker container.

1. Modify the Dockerfile as follows.

    ```dockerfile
    FROM debian:latest

    # =========Install your package=========
    RUN apt-get update && apt-get install -y \
    make \
    gcc  \
    xinetd
    # ======================================

    RUN mkdir -p /var/ctf
    COPY flag /var/ctf/

    # ======Build and run your service======
    ADD /service /src
    COPY echo_service /etc/xinetd.d/

    RUN cd /src; make
    WORKDIR /src

    RUN echo "echo_service 4000/tcp" >> /etc/services

    RUN service xinetd restart
    ENTRYPOINT [ "xinetd", "-dontfork" ]
    ```

2. Create a xinetd configuration file as follows. We assume that the name of the
   config file is `echo_service`.

    ```
    service echo_service
    {
        flags = REUSE
        socket_type = stream
        wait = no
        user = root
        server = /src/echo
        disable = no
        port = 4000
    }
    ```

3. Write a simple echo server in C. We assume that you create a directory called
   `service` and put your program in the directory.

    ```c
    /* service/echo.c */
    #include<stdio.h>
    #include<stdlib.h>
    #include<string.h>    //strlen
    #include<unistd.h>    //write

    int main()
    {
        char buf[256];
        while (1)
        {
            scanf("%s", buf);

            printf("%s\n", buf);
            fflush(stdout);
        }
        return 0;
    }
    ```

    ```makefile
    # service/Makefile
    CC = gcc
    TARGET = echo

    all: echo

    echo:
        $(CC) $(TARGET).c -o $(TARGET)

    clean:
        rm $(TARGET)
    ```

4. Finally, you run the [gitctf script](../scripts): `./gitctf.py exec service
   --service-dir [DIR] --service-name SrvName --host-port 4000 --service-port
   4000` in order to run your echo service in a Docker container. The service
   will listen on port 4000 of the host machine. Assuming the service port is
   4000, you can simply run your service with `./gitctf.py exec service
   --service-dir [DIR] --service-name SrvName`.
