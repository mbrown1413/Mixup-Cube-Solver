
import unittest

from mixupcube import MixupCube, CubieMismatchError, _rotate_turn

class TestCube(unittest.TestCase):

    def assertTurnsEqual(self, turns1, turns2):
        c1 = MixupCube()
        c1.turn(turns1)

        c2 = MixupCube()
        c2.turn(turns2)

        self.assertEqual(c1, c2, '"{}" != "{}"'.format(turns1, turns2))

    def assertTurnsNotEqual(self, turns1, turns2):
        c1 = MixupCube()
        c1.turn(turns1)

        c2 = MixupCube()
        c2.turn(turns2)

        self.assertNotEqual(c1, c2, '"{}" == "{}"'.format(turns1, turns2))

    def assertSolved(self, cube, *args):
        self.assertTrue(cube.is_solved(), *args)

    def assertSolvedTurns(self, turns):
        cube = MixupCube()
        cube.turn(turns)
        self.assertSolved(cube, 'Not in solved state: "{}"'.format(turns))

    def assertNotSolved(self, cube):
        self.assertFalse(cube.is_solved())

    def assertNotSolvedTurns(self, turns):
        cube = MixupCube()
        cube.turn(turns)
        self.assertNotSolved(cube)

    def assertCubeShaped(self, cube, *args):
        self.assertTrue(cube.is_cube_shape(), *args)

    def assertCubeShapedTurns(self, turns):
        cube = MixupCube()
        cube.turn(turns)
        self.assertCubeShaped(cube, 'Not in cube shape: "{}"'.format(turns))

    def assertNotCubeShaped(self, cube):
        self.assertFalse(cube.is_cube_shape())

    def assertNotCubeShapedTurns(self, turns):
        cube = MixupCube()
        cube.turn(turns)
        self.assertNotCubeShaped(cube)

    def assertSolvedDist(self, cube, dist, msg=""):
        solution = cube.solve(_return_turn_list=True)
        self.assertEqual(len(solution), dist, msg+'Solved with: "{}"'.format(solution))

        cube.turn(''.join(solution))
        self.assertSolved(cube, "Scrambled {} - Incorrect solution {}".format(msg, solution))

    def assertTurnsSolvedDist(self, turns, dist):
        cube = MixupCube()
        cube.turn(turns)
        self.assertSolvedDist(cube, dist, 'Turns "{}" '.format(turns))

    #
    # Tests
    #

    def test_cube_eq(self):
        self.assertTurnsEqual("RL", "LR")
        self.assertTurnsNotEqual("RL", "R'L")

        # Slice turns
        self.assertTurnsEqual("MR", "RM")
        self.assertTurnsNotEqual("MR", "MU")

        self.assertTurnsEqual("EU", "UE")
        self.assertTurnsNotEqual("ER", "RE")

        self.assertTurnsEqual("SF", "FS")
        self.assertTurnsNotEqual("SR", "RS")

        # Orientation of faces shouldn't matter
        self.assertTurnsEqual("", "M2E2 R E6M6 E2R'E6")  # U, F rotated
        self.assertTurnsEqual("", "E2S2 U S6E6 S2U'S6")  # D, R rotated
        self.assertTurnsEqual("", "S6E6 F E2S2 E6F'E2")  # B, L rotated

        # Orientation of edges and corners do matter
        self.assertTurnsNotEqual("", "ME2 R E6M' E2R'E6")  # UF rotated
        self.assertTurnsNotEqual("", "RUR'U'RUR' D RU'R'URU'R' D'")  # DFL/DFR rotated

    def test_simple_turns(self):
        self.assertTurnsEqual("RL", "LR")
        self.assertTurnsEqual("UD", "DU")
        self.assertTurnsEqual("FB", "BF")
        self.assertTurnsEqual("RL'", "L'R")
        self.assertTurnsEqual("UD'", "D'U")
        self.assertTurnsEqual("FB'", "B'F")
        self.assertTurnsEqual("R'L'", "L'R'")
        self.assertTurnsEqual("U'D'", "D'U'")
        self.assertTurnsEqual("F'B'", "B'F'")
        self.assertTurnsEqual("R2L2", "L2R2")
        self.assertTurnsEqual("F2B2", "B2F2")
        self.assertTurnsEqual("U2D2", "D2U2")

        # Slice turns
        self.assertTurnsEqual("MMM", "M3")
        self.assertTurnsEqual("MMMR", "RM3")
        self.assertTurnsEqual("", "M'M")
        self.assertTurnsEqual("EEE", "E3")
        self.assertTurnsEqual("EEEU", "UE3")
        self.assertTurnsEqual("", "E'E")
        self.assertTurnsEqual("SSS", "S3")
        self.assertTurnsEqual("SSSB", "BS3")
        self.assertTurnsEqual("", "S'S")

    def test_solved_states(self):
        rotations = (
            "",          # Rot 0 degrees
            "U' E2 D ",  # Rot 90 degrees clockwise
            "U2 E4 D2",  # Rot 180 degrees
            "U  E6 D'",  # Rot 90 degrees counter-clockwise
        )
        solved_turns = []
        for rot in rotations:
            solved_turns.append(rot+"")          # White on Top
            solved_turns.append(rot+"F2 S4 B2")  # White on Bottom
            solved_turns.append(rot+"F  S2 B'")  # White on Right
            solved_turns.append(rot+"F' S6 B ")  # White on Left
            solved_turns.append(rot+"L  M2 R'")  # White on Front
            solved_turns.append(rot+"L' M6 R ")  # White on Back

        # All of those sets of turns result in a solved cube
        for turns in solved_turns:
            self.assertSolvedTurns(turns)

    def test_not_solved(self):
        tests = (
            "R", "U", "M", "E", "S",
            "ME2 R E6M' E2R'E6",  # UF rotated
            "RUR'U'RUR' D RU'R'URU'R' D'",  # DFL/DFR rotated
        )
        for test in tests:
            self.assertNotSolvedTurns(test)

    def test_solved_to_cube(self):
        tests = ("",
            "R", "R'", "R2", "RR",
            "L", "L'", "L2", "LL",
            "U", "U'", "U2", "UU",
            "D", "D'", "D2", "DD",
            "F", "F'", "F2", "FF",
            "B", "B'", "B2", "BB",
            "M2", "M4", "M6", "MM",
            "E2", "E4", "E6", "EE",
            "S2", "S4", "S6", "SS",
            "ME2 R2 E6M' E2R2E6",  # UF rotated 180 degrees
            "RUR'U'RUR' D RU'R'URU'R' D'",  # DFL/DFR rotated
        )
        for test in tests:
            self.assertCubeShapedTurns(test)

    def test_not_solved_to_cube(self):
        tests = (
            "M", "M3", "M5", "M'",
            "E", "E3", "E5", "E'",
            "S", "S3", "S5", "S'",
            "ME2 R E6M' E2R'E6",  # UF rotated 90 degrees
            "MUM'",
            # Edges in edge slots are not rotated, but some edges are in face
            # slots.
            "MUM' U2E4D2 ME2 R E6M' E2R'E6",
        )
        for test in tests:
            self.assertNotCubeShapedTurns(test)

    def test_solve_dist(self):
        tests = (
            ("", 0),
            ("R ", 1), ("L ", 1), ("U ", 1), ("D ", 1), ("F ", 1), ("B ", 1),
            ("R'", 1), ("L'", 1), ("U'", 1), ("D'", 1), ("F'", 1), ("B'", 1),
            ("R2", 1), ("L2", 1), ("U2", 1), ("D2", 1), ("F2", 1), ("B2", 1),
            ("E ", 1), ("S ", 1), ("M ", 1),
            ("E2", 1), ("S2", 1), ("M2", 1),
            ("E3", 1), ("S3", 1), ("M3", 1),
            ("E4", 1), ("S4", 1), ("M4", 1),
            ("E5", 1), ("S5", 1), ("M5", 1),
            ("E6", 1), ("S6", 1), ("M6", 1),
            ("E'", 1), ("S'", 1), ("M'", 1),
            ("RU", 2),
            ("U2D2", 1),  # Solution: E4
            ("M2R'", 1),  # Solution: L
            ("S2F", 1),   # Solution: B'
            ("RUR", 3),
            ("LFD", 3),
            ("FDL", 3),
            ("L'F'D'", 3),  ("F'D'L'", 3),  ("L'FD'", 3),  ("F'DL'", 3),
            ("ML'F'D'", 4), ("MF'D'L'", 4), ("ML'FD'", 4), ("MF'DL'", 4),
            ("EL'F'D'", 4), ("EF'D'L'", 4), ("EL'FD'", 4), ("EF'DL'", 4),
            ("SL'F'D'", 4), ("SF'D'L'", 4), ("SL'FD'", 4), ("SF'DL'", 4),
            ("L'F'MD'", 4), ("F'D'ML'", 4), ("L'FMD'", 4), ("F'DML'", 4),
            ("L'F'ED'", 4), ("F'D'EL'", 4), ("L'FED'", 4), ("F'DEL'", 4),
            ("L'F'SD'", 4), ("F'D'SL'", 4), ("L'FSD'", 4), ("F'DSL'", 4),
            # These move the UFL piece most turns:
            ("FRB", 3),
            ("FRBL", 4),
            ("FRBLU", 5),
            ("UB'RD2", 4),
            ("UB'ERD2", 5),
            ("UB'MRD2", 5),
            ("UB'SRD2", 5),
        )
        for turns, dist in tests:
            self.assertTurnsSolvedDist(turns, dist)

class TestAxisTurns(unittest.TestCase):
    """Tests internal functions `_simplify_axis_turns` and `_rotate_turn`."""

    def test_rotate_turn(self):
        tests = (
            ("x",  "R", "R"),
            ("x2", "R", "R"),
            ("x3", "R", "R"),
            ("y",  "U", "U"),
            ("y2", "U", "U"),
            ("y3", "U", "U"),
            ("z",  "F", "F"),
            ("z2", "F", "F"),
            ("z3", "F", "F"),
        )
        for axis_turn, turn, result in tests:
            self.assertEqual(_rotate_turn(axis_turn, turn), result)


if __name__ == "__main__":
    unittest.main()
