Test results on the full dataset of 11,949 football articles:

| Version | Documents | Peak RAM | Elapsed |
| :--- | :--- | :--- | :--- |
| **eager (lists)** | 11,949 | 454.71 MB | 42.61 s |
| **lazy (generators)** | 11,949 | 5.78 MB | 15.03 s |

Loading the whole dataset into lists burns ~455 MB of RAM because Python has to hold millions of token objects simultaneously. The generator pipeline processes items on the fly, slashing memory usage down to 5.8 MB while running almost three times faster.
