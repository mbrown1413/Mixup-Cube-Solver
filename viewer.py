#!/usr/bin/python3

import sys
from math import radians

from mixupcube import MixupCube

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class CubeViewer():

    def __init__(self, cube):
        self.cube = cube
        self._rot_x = 0
        self._rot_y = 0
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

        glutDisplayFunc(self._draw)
        glutReshapeFunc(self._reshape)
        glutMouseFunc(self._mouse_callback)

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

        self.cube.draw()

        glFlush()
        glutSwapBuffers()

    def _init_camera(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(1, 1, 1,
                  0, 0, 0,
                  0, 1, 0)
        glRotate(self._rot_x, 0, -1, 0)
        glRotate(self._rot_y, 0, 0, -1)

    def _motion_callback(self, x, y):
        last_x, last_y = self._last_mouse_pos
        self._rot_x += (last_x - x) * 0.5
        self._rot_y += (last_y - y) * 0.5
        self._rot_x = self._rot_x % 360
        self._rot_y = self._rot_y % 360
        self._last_mouse_pos = (x, y)
        glutPostRedisplay()

    def _mouse_callback(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                self._left_mouse_down = True
                self._last_mouse_pos = (x, y)
                glutMotionFunc(self._motion_callback)
            else:
                self._left_mouse_down = False
                self._last_mouse_pos = None
                glutMotionFunc(None)

def main():
    import sys

    cube = MixupCube()
    if len(sys.argv) > 1:
        cube.turn(sys.argv[1])
    print cube
    viewer = CubeViewer(cube)

    glutMainLoop()

if __name__ == "__main__":
    main()
