
Finds the shortest solution when given a mixed up 3x3x3 Mixup cube.

The 3x3x3 Mixup cube is a variant of the 3x3x3 Rubik's cube twisty puzzle. It's
a super fun puzzle to solve, so you should get one and try to solve it on your
own! Unlike a traditional Rubik's cube, the Mikup cube allows a slice to be
twisted 45 degrees, which can move edges to places normally occupied by faces,
and vice versa.



Motivation
==========

When I went looking for solutions to the Mixup cube, I didn't find anything
satisfactory. Sure, there are solutions, but it seems like there's a faster
way. For the original Rubik's cube, other people have put an enormous amount of
time into designing fast, optimal algorithms using computer programs. I aim to
do the same for the Mixup cube with this program.

Some of my inspiration comes from this [optimal
solver](https://github.com/brownan/Rubiks-Cube-Solver/) for the Rubik's cube.
Most of the concepts are the same here, just expanded for the Mixup cube.


Status
======

The program can solve the puzzle when it's not too far away from the solved
state. There is still a lot of work to do on optimization. It takes my computer
over 3-4 minutes to solve a cube that is 6 away from the solution.

There also isn't a good user interface yet. The python interface works well,
but the only user facing program is "viewer.py". I'm working on a user
interface to input the cube state and solve it.


Dependancies
============

You'll need:
 * Linux - I've only tested on Debian, but others distros should work.
 * C compiler - gcc and clang are tested, but others should work.
 * Make
 * Python 3.2 or greater - 2.6 or greater may work with minor modifications.
 * Python 3 OpenGL bindings - The Debian package for this was "python3-opengl".


Usage
=====

Compile the library using Make:

    $ make

Right now the only user interface is "viewer.py", which displays the puzzle
after a sequence of moves:

    $ python3 viewer.py "MU'M'R2"


Notation
========

The usual Rubik's cube face turns are pretty standard. By default, they are
clockwise 90 degree turns. Adding an apostrophe ('), pronounced "prime", means
a counter-clockwise turn. Adding a 2 after means a 180 degree turn. These
letters also identify the 6 faces of the cube.
* L - Left
* R - Right
* U - Up
* D - Down
* F - Front
* B - Back

Here are the slice moves of the Mixup cube. They are all 45 degree turns, moving pieces from edge slots to face slots and vice versa.
* M - Middle - Move the slice between L and R faces. The top comes towards the front face. The cubie in the UF slot will now be in the F slot.
* E - Equator - Move the slice between U and D faces. The left comes towards the front face. The cubie in the FL slot will now be in the F slot.
* S - Standing - Move the slice between F and B faces. The top comes towards the right face. The cubie in the UR slot will now be in the R slot.

TODO: Pictures!
