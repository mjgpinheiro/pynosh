#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Creates a mesh on a hexahedron in the x-y-plane.
'''
import vtk
from mesh import mesh
import numpy as np
from cmath import sin, pi
import time
# ==============================================================================
def _main():

    # get command line arguments
    args = _parse_options()

    # Circumcircle radius of the triangle.
    cc_radius = 5.0

    # Create initial nodes/elements.
    tilt = 0.0
    num_nodes = 7
    nodes = np.empty(num_nodes, dtype = np.dtype((float,3)))
    nodes[0] = np.array([0.0, 0.0, 0.0])
    for k in xrange(6):
        phi = (tilt + k/3.0) * pi
        nodes[k+1] = cc_radius * np.array([np.cos(phi), np.sin(phi), 0])

    edgesNodes = np.array([np.array([0,1]),
                           np.array([0,2]),
                           np.array([0,3]),
                           np.array([0,4]),
                           np.array([0,5]),
                           np.array([0,6]),
                           np.array([1,2]),
                           np.array([2,3]),
                           np.array([3,4]),
                           np.array([4,5]),
                           np.array([5,6]),
                           np.array([6,1])])

    cellNodes = np.array([np.array([0, 1, 2]),
                          np.array([0, 2, 3]),
                          np.array([0, 3, 4]),
                          np.array([0, 4, 5]),
                          np.array([0, 5, 6]),
                          np.array([0, 6, 1])])
    cellEdges = np.array([np.array([0,6,1]),
                          np.array([1,7,2]),
                          np.array([2,8,3]),
                          np.array([3,9,4]),
                          np.array([4,10,5]),
                          np.array([5,11,0])])

    # Create mesh data structure.
    mymesh = mesh.Mesh(nodes, cellNodes,
                       edgesNodes = edgesNodes, cellsEdges = cellEdges)

    # Refine..
    print 'Mesh refinement...',
    start = time.time()
    for k in xrange(args.ref_steps):
        mymesh.refine()
    elapsed = time.time()-start
    print 'done. (%gs)' % elapsed

    num_nodes = len( mymesh.nodes )

    # create values
    print 'Create values...',
    start = time.time()
    import random, cmath
    X = np.empty( num_nodes, dtype = complex )
    for k, node in enumerate(mymesh.nodes):
        #X[k] = cmath.rect( random.random(), 2.0 * pi * random.random() )
        X[k] = complex(1.0, 0.0)
    elapsed = time.time()-start
    print 'done. (%gs)' % elapsed

    # Add magnetic vector potential.
    print 'Create mvp...',
    start = time.time()
    A = np.empty(num_nodes, dtype = np.dtype((float,3)))
    from mesh import magnetic_vector_potentials
    height0 = 0.1
    height1 = 1.1
    radius = 2.0
    for k, node in enumerate(mymesh.nodes):
        A[k] = magnetic_vector_potentials.mvp_z( node )
        #A[k] = magnetic_vector_potentials.mvp_magnetic_dot( node, radius, height0, height1 )
    elapsed = time.time()-start
    print 'done. (%gs)' % elapsed

    # write the mesh
    print 'Write mesh...',
    start = time.time()
    mymesh.write( args.filename, {'psi':X, 'A':A} )
    elapsed = time.time()-start
    print 'done. (%gs)' % elapsed

    print '\n%d nodes, %d elements' % (num_nodes, len(mymesh.cellsNodes))

    return
# ==============================================================================
def _parse_options():
    '''Parse input options.'''
    import argparse

    parser = argparse.ArgumentParser( description = 'Construct triangulation of a hexahedron.' )


    parser.add_argument( 'filename',
                         metavar = 'FILE',
                         type    = str,
                         help    = 'file to be written to'
                       )

    parser.add_argument( '--refinements', '-r',
                         metavar='NUM_REFINEMENTS',
                         dest='ref_steps',
                         nargs='?',
                         type=int,
                         const=0,
                         default=0,
                         help='number of mesh refinement steps to be performed (default: 0)'
                       )

    args = parser.parse_args()

    return args
# ==============================================================================
if __name__ == "__main__":
    _main()
# ==============================================================================
