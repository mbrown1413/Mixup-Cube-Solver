#!/usr/bin/python3

import sys
from math import radians

import numpy

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from mixupcube import MixupCube, CubieMismatchError


class CubeViewer():

    def __init__(self, cube):
        self.cube = cube
        self._cam_dist = 1.7
        self._cam_vec = numpy.array([1, 1, 1])  # From origin to camera
        self._cam_up = numpy.array([0, 1, 0])
        self._selected = None
        self._left_mouse_down = False
        self._last_mouse_pos = None
        self._win_width = 400
        self._win_height = 400

        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self._win_width, self._win_height)
        glutCreateWindow(b"Mixup Cube Viewer")

        glClearColor(0, 0, 0, 0)
        glShadeModel(GL_FLAT)
        glEnable(GL_NORMALIZE)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_DITHER)

        glutDisplayFunc(self._draw)
        glutReshapeFunc(self._reshape)
        glutMouseFunc(self._mouse_callback)
        glutKeyboardFunc(self._keyboard_callback)

        self._init_viewport()

    def _init_viewport(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0, 0, self._win_width, self._win_height)
        #TODO: Change fovy to make max(width, height) a 70 degree fov
        gluPerspective(70, self._win_width/self._win_height, 0.1, 4000)

    def _reshape(self, width, height):
        self._win_width = width
        self._win_height = height
        self._init_viewport()

    def _draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._init_camera()

        self.cube.draw(selected_slot=self._selected)

        glFlush()
        glutSwapBuffers()

    def _init_camera(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self._cam_vec = self._cam_vec / numpy.linalg.norm(self._cam_vec)
        cx, cy, cz = self._cam_vec * self._cam_dist
        ux, uy, uz = self._cam_up
        gluLookAt(cx, cy, cz,
                  0, 0, 0,
                  ux, uy, uz)

    def _motion_callback(self, x, y):
        last_x, last_y = self._last_mouse_pos
        self._last_mouse_pos = (x, y)
        if last_x != x or last_y != y:
            self._left_mouse_moved = True

        dx = x - last_x
        dy = y - last_y

        left_vec = numpy.cross(self._cam_vec, self._cam_up)
        self._cam_vec += left_vec * dx * 4 / self._win_width
        self._cam_vec += self._cam_up * dy * 4 / self._win_height
        self._cam_vec = self._cam_vec / numpy.linalg.norm(self._cam_vec)

        left_vec = numpy.cross(self._cam_vec, self._cam_up)
        self._cam_up = numpy.cross(left_vec, self._cam_vec)
        self._cam_up = self._cam_up / numpy.linalg.norm(self._cam_up)

        glutPostRedisplay()

    def _mouse_callback(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                self._left_mouse_down = True
                self._left_mouse_moved = False
                self._last_mouse_pos = (x, y)
                glutMotionFunc(self._motion_callback)

            else:
                self._left_mouse_down = False
                self._last_mouse_pos = None
                glutMotionFunc(None)

                if not self._left_mouse_moved:
                    self._selected = self._slot_at_pixel(x, y)
                    glutPostRedisplay()

        elif button == GLUT_RIGHT_BUTTON and state == GLUT_UP:
            self._selected = self._slot_at_pixel(x, y)
            glutPostRedisplay()

        elif button == GLUT_MIDDLE_BUTTON and state == GLUT_UP:
            to_swap = self._slot_at_pixel(x, y)
            if self._selected is not None and to_swap is not None:
                try:
                    self.cube.swap_cubies(self._selected, to_swap)
                    self._selected = to_swap
                    glutPostRedisplay()
                except CubieMismatchError:
                    pass  # Tried to swap corner with an edge or face

    def _keyboard_callback(self, key, x, y):
        if key == b'r' and self._selected is not None:
            self.cube.rotate_cubie(self._selected, 1)
            glutPostRedisplay()
        elif key == b'R' and self._selected is not None:
            self.cube.rotate_cubie(self._selected, -1)
            glutPostRedisplay()
        elif key == b's' or key == b'S':
            print("Solving {}".format(self.cube))
            solution = self.cube.solve()
            if solution:
                print(solution)
            else:
                print("Cube already solved")

    def _slot_at_pixel(self, x, y):
        """Returns the slit id at the pixel position (x, y)."""

        glClearColor(1, 1, 1, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._init_camera()

        self.cube.draw(slot_id_map=True)

        glFlush()
        glClearColor(0, 0, 0, 0)

        slot = glReadPixels(x, self._win_height - y, 1, 1, GL_RGB, GL_BYTE)[0][0][0]
        if slot < 0 or slot > 25:
            slot = None
        return slot


def main():
    import sys

    cube = MixupCube()
    if len(sys.argv) > 1:
        cube.turn(sys.argv[1])
    print(cube)
    viewer = CubeViewer(cube)
    #print(cube.is_solved())
    #print(cube.solve())

    glutMainLoop()

if __name__ == "__main__":
    main()
