#!/usr/bin/python3
"""
Generates "turn_avoid_table" in "src/mixupcube_solve.c". See that file for a
complete description of the table.

Here are the turns that are currently avoided:
 * Turning the same face or slice twice (ex: LL', L2L)

"""

import sys
if sys.version_info < (3, 2):
    raise RuntimeError("Python version 3.2 or greater is required")

from itertools import product

from mixupcube import TURN_IDS

U1= 0; D1= 1; F1= 2; B1= 3; L1= 4; R1= 5;
U2= 6; D2= 7; F2= 8; B2= 9; L2=10; R2=11;
U3=12; D3=13; F3=14; B3=15; L3=16; R3=17;
M1=18; E1=19; S1=20; M2=21; E2=22; S2=23;
M3=24; E3=25; S3=26; M4=27; E4=28; S4=29;
M5=30; E5=31; S5=32; M6=33; E6=34; S6=35;
M7=36; E7=37; S7=38;

U_TURNS = (U1, U2, U3)
D_TURNS = (D1, D2, D3)
F_TURNS = (F1, F2, F3)
B_TURNS = (B1, B2, B3)
L_TURNS = (L1, L2, L3)
R_TURNS = (R1, R2, R3)
M_TURNS = (M1, M2, M3, M4, M5, M6, M7)
E_TURNS = (E1, E2, E3, E4, E5, E6, E7)
S_TURNS = (S1, S2, S3, S4, S5, S6, S7)


def add_avoid(table, prev_turn, turn):
    table[prev_turn] |= 1 << turn

def generate_table():
    table = [0 for turn in range(len(TURN_IDS)+1)]

    # Don't turn the same face or slice twice in a row
    for turn_set in (U_TURNS, D_TURNS, F_TURNS,
                     B_TURNS, L_TURNS, R_TURNS,
                     M_TURNS, E_TURNS, S_TURNS):
        for t1, t2 in product(turn_set, repeat=2):
            add_avoid(table, t1, t2)

    return table

def table_to_string(table):
    ret = []
    hex_fmt = "0x{:0>10x}, "
    fmt_6 = ("    "+hex_fmt*6).rstrip(" ")
    fmt_3 = ("    "+hex_fmt*3).rstrip(" ")
    fmt_1 = ("    "+hex_fmt*1).rstrip(" ")
    for a in range(0, 18, 6):
        ret.append(fmt_6.format(*table[a:a+6]))
    for a in range(18, 39, 3):
        ret.append(fmt_3.format(*table[a:a+3]))
    ret.append(fmt_1.format(0))  # Used for "no previous turn"

    return '\n'.join(ret)

if __name__ == "__main__":
    print(table_to_string(generate_table()))
