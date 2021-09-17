# foodpandacrawler
Uses https://github.com/openvenues/pypostal for address parsing. 
You will need to follow the instructions and install libpostal(some cursed C library) before your pypostal module will work.
If you get something like 'ImportError: libpostal.so.1: cannot open shared object file: No such file or directory' run an 'sudo ldconfig /usr/local/lib' inside the project folder. Now it should work.
Just made my life easier and yours harder.

