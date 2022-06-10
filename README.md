# ECA
a program for generating colormaps of elementary cellular automata

I gained an interest in cellular automata after reading the science fiction book _Permutation City_ by Greg Egan, and did a bit of studying about them after
finishing the book. I learned about von Neumann neighborhoods, Conway's Game of Life, and Wolfram's elementary cellular automata, the latter of which I thought
would be the perfect opportunity to get some good practice coding while learning about something interesting. There are already programs which do this exact thing
available elsewhere, but I thought it would be fun to build a program from scratch which can run the elementary cellular automata rules on binary input states
of arbitrary length. I wanted this to be fully customizable, so that a user could run any ECA rule for any number of generations, as well as being able to select
various boundary conditions. I think it is extremely interesting to see such a clear visualization that simple, deterministic computational rules can generate
both patterns of chaotic randomness, and also complex, persistent forms of information across generations.

Here is an example of a colormap output for rule 110:
![rule110_example](https://user-images.githubusercontent.com/33963737/172966363-37ddc5d7-dbc2-443d-a601-2b43f0935051.png)
