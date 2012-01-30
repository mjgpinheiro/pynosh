#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Creates meshes on a cube.
'''
import mesh
import numpy as np
#from math import sin, pi, atan, sqrt
from mesh import mesh
from mesh import magnetic_vector_potentials
import time
# ==============================================================================
def _main():

    # get the file name to be written to
    args = _parse_options()

    # circumcirlce radius
    cc_radius = 5.0
    lx = 2.0/np.sqrt(3.0) * cc_radius
    l = [lx, lx, lx]

    # create the mesh data structure
    print 'Create mesh...',
    start = time.time()
    if args.nx != 0:
        mymesh = _canonical(l, [args.nx, args.nx, args.nx])
    elif args.maxvol != 0.0:
        mymesh = _meshpy(l, args.maxvol)
    else:
        raise RuntimeError('Set either -c or -m.')
    elapsed = time.time() - start
    print 'done. (%gs)' % elapsed

    num_nodes = len(mymesh.nodes)
    print '\n%d nodes, %d elements\n' % (num_nodes, len(mymesh.cells))

    print 'Create values...',
    start = time.time()
    # create values
    X = np.empty( num_nodes, dtype = complex )
    for k, node in enumerate(mymesh.nodes):
        X[k] = complex( 1.0, 0.0 )
        #X[k] = complex( sin( x/lx * np.pi ), sin( y/ly * np.pi ) )
    elapsed = time.time()-start
    print 'done. (%gs)' % elapsed

    print 'Create thickness values...',
    start = time.time()
    # add thickness value
    thickness = np.empty( num_nodes, dtype = float )
    alpha = 1.0
    beta = 2.0
    for k, node in enumerate(mymesh.nodes):
        #thickness[k] = alpha + (beta-alpha) * (y/(0.5*ly))**2
        thickness[k] = 1.0
    elapsed = time.time()-start
    print 'done. (%gs)' % elapsed

    print 'Create mvp...',
    start = time.time()
    # add magnetic vector potential
    A = np.empty( (num_nodes,3), dtype = float )
    # exact corner of a cube
    phi = np.pi/4.0 # azimuth
    theta = np.arctan( 1.0/np.sqrt(2.0) ) # altitude
    height0 = 0.1
    height1 = 1.1
    radius = 2.
    for k, node in enumerate(mymesh.nodes):
        A[k,:] = magnetic_vector_potentials.mvp_z( node )
        #A[k,:] = magnetic_vector_potentials.mvp_magnetic_dot( node, radius, height0, height1 )
    elapsed = time.time()-start
    print 'done. (%gs)' % elapsed

    # write the mesh with data
    print 'Write to file...',
    start = time.time()
    mymesh.write(args.filename, {'psi': X, 'A': A, 'thickness': thickness})
    elapsed = time.time()-start
    print 'done. (%gs)' % elapsed

    return
# ==============================================================================
def _canonical(l, N):
    '''Canonical tetrahedrization of the cube.
    Input:
    Edge lenghts of the cube
    Number of nodes along the edges.
    '''

    # Generate suitable ranges for parametrization
    x_range = np.linspace( -0.5*l[0], 0.5*l[0], N[0] )
    y_range = np.linspace( -0.5*l[1], 0.5*l[1], N[1] )
    z_range = np.linspace( -0.5*l[2], 0.5*l[2], N[2] )

    print 'Create nodes...',
    start = time.time()
    # Create the vertices.
    num_nodes = N[0] * N[1] * N[2]
    nodes = []
    for x in x_range:
        for y in y_range:
            for z in z_range:
                nodes.append(np.array([x, y, z]))
    elapsed = time.time()-start
    print 'done. (%gs)' % elapsed

    print 'Create elements...',
    start = time.time()
    # Create the elements (cells).
    # There is 1 way to split a cube into 5 tetrahedra,
    # and 12 ways to split it into 6 tetrahedra.
    # See <http://private.mcnet.ch/baumann/Splitting%20a%20cube%20in%20tetrahedras2.htm>.
    # Also interesting: <http://en.wikipedia.org/wiki/Marching_tetrahedrons>.
    num_cubes = (N[0]-1) * (N[1]-1) * (N[2]-1)
    num_cells = 5 * num_cubes
    #dt = np.dtype( [ (int, 4), (int) ] )
    elems = []
    for i in range(N[0] - 1):
        for j in range(N[1] - 1):
            for k in range(N[2] - 1):
                # Switch the element styles to make sure the edges match at
                # the faces of the cubes.
                if ( i+j+k ) % 2 == 0:
                    elems.append( mesh.Cell( [ N[2] * ( N[1]*i     + j   ) + k,
                                               N[2] * ( N[1]*i     + j+1 ) + k,
                                               N[2] * ( N[1]*(i+1) + j   ) + k,
                                               N[2] * ( N[1]*i     + j   ) + k+1
                                             ]
                                           )
                                )
                    elems.append( mesh.Cell( [ N[2] * ( N[1]*i     + j+1 ) + k,
                                               N[2] * ( N[1]*(i+1) + j+1 ) + k,
                                               N[2] * ( N[1]*(i+1) + j   ) + k,
                                               N[2] * ( N[1]*(i+1) + j+1 ) + k+1
                                             ]
                                           )
                                )
                    elems.append( mesh.Cell( [ N[2] * ( N[1]*i     + j+1 ) + k,
                                               N[2] * ( N[1]*(i+1) + j   ) + k,
                                               N[2] * ( N[1]*i     + j   ) + k+1,
                                               N[2] * ( N[1]*(i+1) + j+1 ) + k+1
                                             ]
                                           )
                                )
                    elems.append( mesh.Cell( [ N[2] * ( N[1]*i     + j+1 ) + k,
                                               N[2] * ( N[1]*i     + j   ) + k+1,
                                               N[2] * ( N[1]*i     + j+1 ) + k+1,
                                               N[2] * ( N[1]*(i+1) + j+1 ) + k+1
                                             ],
                                           )
                                )
                    elems.append( mesh.Cell( [ N[2] * ( N[1]*(i+1) + j   ) + k,
                                               N[2] * ( N[1]*i     + j   ) + k+1,
                                               N[2] * ( N[1]*(i+1) + j+1 ) + k+1,
                                               N[2] * ( N[1]*(i+1) + j   ) + k+1
                                             ]
                                           )
                                )
                else:
                    # Like the previous one, but flipped along the first
                    # coordinate: i+1 -> i, i -> i+1.
                    elems.append( mesh.Cell( [ N[2] * ( N[1]*(i+1) + j   ) + k,
                                               N[2] * ( N[1]*(i+1) + j+1 ) + k,
                                               N[2] * ( N[1]*i     + j   ) + k,
                                               N[2] * ( N[1]*(i+1) + j   ) + k+1
                                            ]
                                          )
                                )
                    elems.append( mesh.Cell( [ N[2] * ( N[1]*(i+1) + j+1 ) + k,
                                               N[2] * ( N[1]*i     + j+1 ) + k,
                                               N[2] * ( N[1]*i     + j   ) + k,
                                               N[2] * ( N[1]*i     + j+1 ) + k+1
                                             ]
                                           )
                                )
                    elems.append( mesh.Cell( [ N[2] * ( N[1]*(i+1) + j+1 ) + k,
                                               N[2] * ( N[1]*i     + j   ) + k,
                                               N[2] * ( N[1]*(i+1) + j   ) + k+1,
                                               N[2] * ( N[1]*i     + j+1 ) + k+1
                                             ]
                                           )
                                )
                    elems.append( mesh.Cell( [ N[2] * ( N[1]*(i+1) + j+1 ) + k,
                                               N[2] * ( N[1]*(i+1) + j   ) + k+1,
                                               N[2] * ( N[1]*(i+1) + j+1 ) + k+1,
                                               N[2] * ( N[1]*i     + j+1 ) + k+1
                                             ]
                                           )
                                )
                    elems.append( mesh.Cell( [ N[2] * ( N[1]*i     + j   ) + k,
                                               N[2] * ( N[1]*(i+1) + j   ) + k+1,
                                               N[2] * ( N[1]*i     + j+1 ) + k+1,
                                               N[2] * ( N[1]*i     + j   ) + k+1
                                             ]
                                           )
                                )


    mymesh = mesh.Mesh(nodes, elems)

    return mymesh
# ==============================================================================
def _meshpy(l, max_volume):
    import mesh.meshpy_interface

    # Corner points of the cube
    points = [ ( -0.5*l[0], -0.5*l[1], -0.5*l[2] ),
               (  0.5*l[0], -0.5*l[1], -0.5*l[2] ),
               (  0.5*l[0],  0.5*l[1], -0.5*l[2] ),
               ( -0.5*l[0],  0.5*l[1], -0.5*l[2] ),
               ( -0.5*l[0], -0.5*l[1],  0.5*l[2] ),
               (  0.5*l[0], -0.5*l[1],  0.5*l[2] ),
               (  0.5*l[0],  0.5*l[1],  0.5*l[2] ),
               ( -0.5*l[0],  0.5*l[1],  0.5*l[2] ) ]
    facets = [ [0,1,2,3],
               [4,5,6,7],
               [0,4,5,1],
               [1,5,6,2],
               [2,6,7,3],
               [3,7,4,0] ]

    # create the mesh
    print 'Create mesh...',
    start = time.time()
    mymesh = mesh.meshpy_interface.create_mesh( max_volume, points, facets )
    elapsed = time.time()-start
    print 'done. (%gs)' % elapsed

    return mymesh
# ==============================================================================
def _parse_options():
    '''Parse input options.'''
    import argparse

    parser = argparse.ArgumentParser( description = 'Construct a trival tetrahedrization of a cube.' )


    parser.add_argument( 'filename',
                         metavar = 'FILE',
                         type    = str,
                         help    = 'file to be written to'
                       )

    parser.add_argument( '--canonical', '-c',
                         metavar = 'NX',
                         dest='nx',
                         nargs='?',
                         type=int,
                         const=0,
                         default=0,
                         help='canonical tetrahedrization with NX discretization points along each axis'
                       )

    parser.add_argument( '--meshpy', '-m',
                         metavar = 'MAXVOL',
                         dest='maxvol',
                         nargs='?',
                         type=float,
                         const=0.0,
                         default=0.0,
                         help='meshpy tetrahedrization with MAXVOL maximum tetrahedron volume'
                       )

    args = parser.parse_args()

    return args
# ==============================================================================
if __name__ == "__main__":
    _main()
# ==============================================================================
