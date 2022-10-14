
import glob
from pdb import line_prefix
from scipy.optimize import least_squares
from sympy import fps, li
from geometry import Trilateration, Circle, Point
import sys
import os
#from RfToF_Board_Anchor import Swarmbee
#from radius import find_radius
import matplotlib.pyplot as plt
import json
import imageio

def solve_history(history: [Trilateration], guess=Circle(0, 0, 0)):
    """solves a list of Trilateration objects. Remembers last guess"""
    if isinstance(history, list):
      for item in history:
        guess = solve(item, guess)
    else:
        guess = solve(history, guess)  


def solve(trilateration, guess: Circle = Circle(0, 0, 0)) -> Circle:
    """stores a trilateration result and returns it"""
    result = easy_least_squares(trilateration.beacons, guess)
    trilateration.result = result
    return result


def get_intersect(circle_1: Circle, circle_2: Circle) -> Point:
    """Returns the positive intersection point of two circles"""
    d = circle_2.center.x - circle_1.center.x
    x = (circle_1.radius**2 - circle_2.radius**2 + d**2)/(2*d)
    y = (circle_1.radius**2 - x**2)**0.5
    return Point(x, y)


def easy_least_squares(beacons: list, guess=Circle(0, 0, 0)) -> Circle:
    """Finds a trilateration result for multiple beacons"""
    g = (guess.center.x, guess.center.y, guess.radius)
    result = least_squares(equations, g, args=[beacons])
    xf, yf, rf = result.x
    return Circle(xf, yf, rf)


def equations(guess, crls: [Circle]):
    """equations to find an optimized solution for"""
    eqs = []
    x, y, r = guess
    for circle in crls:
        eqs.append(((x - circle.center.x) ** 2 + (y - circle.center.y) ** 2 - (circle.radius - r) ** 2))
    return eqs

def main():

    with open("/home/rushabh/Desktop/Becker Mining Positioning System/Software/trilateration/result.txt") as f:
        r = f.readlines() 
        #r = line
    r_list = list(map(float,r))

    x1,y1 = 0,0
    x2,y2 = 1009,0
    x3,y3 = 541,937
    x_pts = [x1,x2,x3]
    y_pts = [y1,y2,y3]

    x_ = []
    y_ = []

    for i in range(len(r_list)//3):
        print(i)
        r = [r_list[3*i], r_list[3*i+1], r_list[3*i+2]]
        r = r
        print(r)

        circ1 = Circle(x1,y1,(r[0]))
        circ2 = Circle(x2,y2,(r[1]))
        circ3 = Circle(x3,y3,(r[2]))

        tri = Trilateration([circ1, circ2, circ3])
        solve_history(tri)
        tri_result = tri.result

        print(tri_result)

        center = tri_result.center
        x = center.x
        x_.append(x)
        y = center.y
        y_.append(y)
        r = tri_result.radius

        fig, ax = plt.subplots()

        circle1 = plt.Circle((x,y), r,facecolor="none",edgecolor="blue")
        target_pts = plt.scatter(x_pts, y_pts, marker="x", s=100, c='red')
        center_point= plt.scatter(x_,y_,marker="x", s=50, c='blue')
        ax.legend([circle1, target_pts], ['Location', 'Anchors'])
        plt.xlabel("X in cm")
        plt.ylabel("Y in cm")
        plt.title("2D Position Estimation")
        plt.grid(True)
        plt.xlim([-100,1200])
        plt.ylim([-100,1200])

        ax.add_patch(circle1)
        # ax.add_patch(target_pts)

        fig.savefig(f'plotcircle_{i}.png')
    
    img_list = glob.glob("*.png")
    images = []
    for img in img_list:
        data = imageio.imread(img)
        images.append(data)
    imageio.mimsave("imgs.gif", images, fps=1)


if __name__ == "__main__":
    main()