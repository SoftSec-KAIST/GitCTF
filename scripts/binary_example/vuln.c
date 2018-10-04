#include <stdio.h>
#include <stdlib.h>

int main()
{
    char buf[10];
    gets(buf);
    puts(buf);
    fflush(stdout);
    if(!strcmp(buf, "bug"))
    {
        system("/bin/bash");
    }
    return 0;
}
