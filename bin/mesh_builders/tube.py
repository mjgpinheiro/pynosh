#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Creates a simplistic triangular mesh on a M\"obius strip.
'''
from mesh import mesh
import numpy as np
# ==============================================================================
def _main():
    # get the file name to be written to
    args = _parse_options()

    # Number of nodes along the width of the strip (>= 2)
    # Choose it such that we have approximately square boxes.
    nw = int( round( args.width * args.n/(2*np.pi*args.radius) ) ) 

    # Generate suitable ranges for parametrization
    u_range = np.linspace( 0.0, 2*np.pi, num = args.n, endpoint = False )
    v_range = np.linspace( -0.5*args.width, 0.5*args.width, num = nw )

    # Create the vertices.
    nodes = []
    for u in u_range:
        x = args.radius * np.cos(u)
        y = args.radius * np.sin(u)
        for v in v_range:
            nodes.append(np.array([x, y, v]))

    # create the elements (cells)
    elems = []
    for i in xrange(args.n - 1):
        for j in xrange(nw - 1):
            elems.append(mesh.Cell([ i*nw + j, (i + 1)*nw + j + 1,  i     *nw + j + 1 ]))
            elems.append(mesh.Cell([ i*nw + j, (i + 1)*nw + j    , (i + 1)*nw + j + 1 ]))
    # close the geometry
    for j in xrange(nw - 1):
        elems.append(mesh.Cell([ (args.n - 1)*nw + j, j + 1 , (args.n - 1)*nw + j + 1 ]))
        elems.append(mesh.Cell([ (args.n - 1)*nw + j, j     , j + 1  ]))

    # create the mesh data structure
    mymesh = mesh.Mesh(nodes, elems)
    num_nodes = len(mymesh.nodes)

    # add values
    X = np.empty(num_nodes, dtype = complex)
    for k, node in enumerate(mymesh.nodes):
        X[k] = complex(1.0, 0.0)

    # Add values for thickness:
    # Make it somewhat thicker at the boundaries.
    thickness = np.empty( num_nodes, dtype = float )
    alpha = 0.5 # thickness at the center of the tube
    beta = 2.0 # thickness at the boundary
    t = (beta-alpha) / (0.5*args.width)**2
    for k, node in enumerate(mymesh.nodes):
        thickness[k] = 1.0
        #thickness[k] = alpha + t * nodes[k].coords[2]**2

    # create the mesh
    mymesh.write(args.filename, {'psi': X, 'thickness': thickness})

    return
# ==============================================================================
def _parse_options():
    '''Parse input options.'''
    import argparse

    parser = argparse.ArgumentParser( description = 'Construct a triangulation of a tube.' )

    parser.add_argument( 'filename',
                         metavar = 'FILE',
                         type    = str,
                         help    = 'file to be written to'
                       )

    parser.add_argument( '--radius','-r',
                         metavar = 'RADIUS',
                         dest='radius',
                         nargs='?',
                         type=float,
                         const=1.0,
                         default=1.0,
                         help    = 'radius of the tube (default: 1.0)'
                       )

    parser.add_argument( '--width','-w',
                         metavar = 'WIDTH',
                         dest='width',
                         nargs='?',
                         type=float,
                         const=1.0,
                         default=1.0,
                         help    = 'width of the tube (default: 1.0)'
                       )

    parser.add_argument( '--numpoints','-n',
                         metavar = 'NUMPOINTS',
                         dest='n',
                         nargs='?',
                         type=float,
                         const=30,
                         default=30,
                         help='number of nodes along the length of the strip (default: 30)'
                       )

    return parser.parse_args()
# ==============================================================================
if __name__ == "__main__":
    _main()
# ==============================================================================
