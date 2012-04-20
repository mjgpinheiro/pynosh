'''Module that provides magnetic vector potentials.'''
import numpy as np
from math import cos, sin
cdef extern from "math.h":
    void sincosf(float x, float *sin, float *cos)
    float sqrtf(float x)
# ==============================================================================
def constant_x( X ):
    '''Magnetic vector potential corresponding to the field B=(1,0,0).'''
    if len(X.shape) == 2:
        # array of data points
        return np.array([np.zeros(X.shape[0])
                         -0.5 * X[:,2],
                          0.5 * X[:,1]]
                         ).T
    else:
        # Just one point.
        return [ 0.0, -0.5*X[2], 0.5*X[1] ]
# ==============================================================================
def constant_y( X ):
    '''Magnetic vector potential corresponding to the field B=(0,1,0).'''
    if len(X.shape) == 2:
        # array of data points
        return np.array([ 0.5 * X[:,2],
                         np.zeros(X.shape[0])
                         -0.5 * X[:,0]]
                         ).T
    else:
        # Just one point.
        return [ 0.5*X[2], 0.0, -0.5*X[0] ]
# ==============================================================================
def constant_z( X ):
    '''Magnetic vector potential corresponding to the field B=(0,0,1).'''
    if len(X.shape) == 2:
        if X.shape[1] == 2:
            return np.array([-0.5 * X[:,1],
                              0.5 * X[:,0]]
                             ).T
        elif X.shape[1] == 3:
            return np.array([-0.5 * X[:,1],
                              0.5 * X[:,0],
                             np.zeros(X.shape[0])]
                             ).T
        else:
            raise ValueError('Coordinate data not understood.')
    else:
        # Just one point.
        return [ -0.5*X[1], 0.5*X[0], 0.0 ]
# ==============================================================================
def field2potential(X, B):
    '''Converts a spatially constant magnetic field B at X
    into a corresponding potential.'''
    # This is one particular choice that works.
    return 0.5 * np.cross(B, X)
# ==============================================================================
def spherical( X, phi, theta ):
    '''Magnetic vector potential corresponding to the field
           B=( cos(theta)cos(phi), cos(theta)sin(phi), sin(theta) ),
       i.e., phi\in(0,2pi) being the azimuth, theta\in(-pi,pi) the altitude.
       The potentials parallel to the Cartesian axes can be recovered by
           mvp_x = mvp_spherical( ., 0   , 0    ),
           mvp_y = mvp_spherical( ., 0   , pi/2 ),
           mvp_z = mvp_spherical( ., pi/2, *    ).'''
    return [ -0.5 * np.sin(theta)               * X[1]
             +0.5 * np.cos(theta) * np.sin(phi) * X[2],
              0.5 * np.sin(theta)               * X[0]
             -0.5 * np.cos(theta) * np.cos(phi) * X[2],
              0.5 * np.cos(theta) * np.cos(phi) * X[1]
             -0.5 * np.cos(theta) * np.sin(phi) * X[0] ]
# ==============================================================================
def magnetic_dipole(x, x0, m):
   '''Magnetic vector potential for the static dipole at x0
   with orientation m.'''
   r = x - x0
   # npsum(...) = ||r||^3 row-wise;
   # np.cross acts on rows by default;
   # The ".T" magic makes sure that each row of np.cross(m, r)
   # gets divided by the corresponding entry in ||r||^3.
   return (np.cross(m, r).T / np.sum(np.abs(r)**2,axis=-1)**(3./2)).T
# ==============================================================================
def magnetic_dot(float x, float y,
                 float magnet_radius,
                 float height0,
                 float height1
                 ):
    '''Magnetic vector potential corresponding to the field that is induced
    by a cylindrical magnetic dot, centered at (0,0,0.5*(height0+height1)),
    with the radius magnet_radius for objects in the x-y-plane.
    The potential is derived by interpreting the dot as an infinitesimal
    collection of magnetic dipoles, hence

       A(x) = \int_{dot} A_{dipole}(x-r) dr.

    Support for input valued (x,y,z), z!=0, is pending.
    '''
    cdef float pi = 3.141592653589793

    # Span a cartesian grid over the sample, and integrate over it.

    # For symmetry, choose a number that is divided by 4.
    cdef int n_phi = 100
    # Choose such that the quads at radius/2 are approximately squares.
    cdef int n_radius = int( round( n_phi / pi ) )

    cdef float dr = magnet_radius / n_radius

    cdef float ax = 0.0
    cdef float ay = 0.0
    cdef float beta, rad, r, r_3D0, r_3D1, alpha, x0, y0, x_dist, y_dist, sin_beta, cos_beta
    cdef int i_phi, i_radius

    # What we want to have is the value of
    #
    #    I(X) := \int_{dot} \|X-XX\|^{-3/2} (m\times(X-XX)) dXX
    # 
    # with
    # 
    #    X := (x, y, z)^T,
    #    XX := (xx, yy, zz)^T
    #
    # The integral in zz can be calculated analytically, such that
    #
    #    I = \int_{disk}
    #           [ - (z-zz) / (r2D*sqrt(r3D)) ]_{zz=h_0}^{h_1} ( -(y-yy), x-xx, 0)^T dxx dyy.
    # 
    # The integral over the disk is then approximated numerically by
    # the summation over little disk segments.
    # An alternative is to use cylindrical coordinates.
    #
    for i_phi in range(n_phi):
        beta = 2.0*pi/n_phi * i_phi
        sincosf(beta, &sin_beta, &cos_beta)
        for i_radius in range(n_radius):
            rad = magnet_radius / n_radius * (i_radius + 0.5)
            # r = squared distance between grid point X to the
            #     point (x,y) on the magnetic dot
            x_dist = x - rad * cos_beta
            y_dist = y - rad * sin_beta
            r = x_dist * x_dist + y_dist * y_dist
            if r > 1.0e-15:
                # 3D distance to point on lower edge (xi,yi,height0)
                r_3D0 = sqrtf( r + height0*height0 )
                # 3D distance to point on upper edge (xi,yi,height1)
                r_3D1 = sqrtf( r + height1*height1 )
                # Volume of circle segment = pi*anglar_width * r^2,
                # so the volume of a building brick of the discretization is
                #   V = pi/n_phi * [(r+dr/2)^2 - (r-dr/2)^2]
                #     = pi/n_phi * 2 * r * dr.
                alpha = ( height1/r_3D1 - height0/r_3D0 ) / r \
                      * pi / n_phi * (2.0*rad*dr) # volume
                ax += y_dist * alpha
                ay -= x_dist * alpha

    return [ ax, ay, 0.0 ]
# ==============================================================================
