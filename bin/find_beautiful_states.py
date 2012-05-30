#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''Solve the Ginzburg--Landau equation.
'''
# ==============================================================================
import numpy as np

import pyginla.numerical_methods as nm
import pyginla.gp_modelevaluator as gm
import voropy
# ==============================================================================
def _main():
    args = _parse_input_arguments()

    # read the mesh
    print 'Reading the mesh...',
    mesh, point_data, field_data = voropy.read( args.filename )
    print 'done.'

    # build the model evaluator
    modeleval = gm.GrossPitaevskiiModelEvaluator(mesh,
                                                 g = field_data['g'],
                                                 V = point_data['V'],
                                                 A = point_data['A'],
                                                 mu = field_data['mu'])

    param_range = np.linspace(args.parameter_range[1],
                              args.parameter_range[0],
                              args.num_parameter_steps)
    print 'Looking for solutions for %s in' % args.parameter
    print param_range
    print
    find_beautiful_states(modeleval, args.parameter, param_range, args.forcing_term)
    return
# ==============================================================================
def find_beautiful_states( modeleval, param_name, param_range, forcing_term ):
    '''Loop through a set of parameters/initial states and try to find
    starting points that (quickly) lead to "interesting looking" solutions.
    Such solutions are filtered out only by their energy at the moment.'''

    # Define search space.
    # Don't use Mu=0 as the preconditioner is singular for mu=0, psi=0.
    Alpha = np.linspace(0.2, 1.0, 5)
    Frequencies = [0.0, 0.5, 1.0, 2.0]

    # initial guess
    num_nodes = len(modeleval.mesh.node_coords)

    # Compile the search space.
    # If all nodes sit in x-y-plane, the frequency loop in z-direction
    # can be ommitted.
    if modeleval.mesh.node_coords.shape[1]==2:
        search_space_k = [(a,b) for a in Frequencies for b in Frequencies]
    elif modeleval.mesh.node_coords.shape[1] == 3:
        search_space_k = [(a,b,c) for a in Frequencies for b in Frequencies for c in Frequencies]
    search_space = [(a,k) for a in reversed(Alpha) for k in search_space_k]

    solution_id = 0
    # Loop over problem parameters in reversed order:
    # This way, we'll find the states with many nodes first.
    for p in param_range:
        # Reset the solutions each time the problem parameters change.
        found_solutions = []
        # Loop over initial states.
        for alpha, k in search_space:
            modeleval.set_parameter(param_name, p)
            print '%s = %g; alpha = %g; k = %s' % (param_name, p, alpha, k,)
            # Set the intitial guess for Newton.
            if len(k) == 2:
                psi0 = alpha \
                     * np.cos(k[0] * np.pi * modeleval.mesh.node_coords[:,0]) \
                     * np.cos(k[1] * np.pi * modeleval.mesh.node_coords[:,1]) \
                     + 1j * 0
            elif len(k) == 3:
                psi0 = alpha \
                     * np.cos(k[0] * np.pi * modeleval.mesh.node_coords[:,0]) \
                     * np.cos(k[1] * np.pi * modeleval.mesh.node_coords[:,1]) \
                     * np.cos(k[2] * np.pi * modeleval.mesh.node_coords[:,2]) \
                     + 1j * 0
            else:
                raise RuntimeError('Illegal k.')

            print 'Performing Newton iteration...'
            # perform newton iteration
            newton_out = nm.newton(psi0[:,None],
                                   modeleval,
                                   linear_solver = nm.minres,
                                   linear_solver_maxiter = 500, #2*len(psi0),
                                   linear_solver_extra_args = {},
                                   nonlinear_tol = 1.0e-10,
                                   forcing_term = forcing_term,
                                   eta0 = 1.0e-10,
                                   use_preconditioner = True,
                                   deflation_generators = [ lambda x: 1j*x ],
                                   num_deflation_vectors = 0,
                                   debug=True,
                                   newton_maxiter = 50
                                   )
            print ' done.'

            print 'Num MINRES iterations:', [len(resvec) for resvec in newton_out['linear relresvecs']]
            print 'Newton residuals:', newton_out['Newton residuals']
            if newton_out['info'] == 0:
                num_newton_iters = len(newton_out['linear relresvecs'])
                psi = newton_out['x']
                # Use the energy as a measure for ruling out boring states
                # such as psi==0 or psi==1 overall.
                energy = modeleval.energy( psi )
                print 'Energy of solution state: %g.' % energy
                if energy > -0.999 and energy < -0.001:
                    # Store the file as VTU such that ParaView can loop through
                    # and display them at once. For this, also be sure to keep
                    # the file name in the format 'sdgfds-01414.vtu'.
                    filename = 'interesting-' \
                             + repr(num_newton_iters).rjust(2,'0') \
                             + repr(solution_id).rjust(3,'0') \
                             + '.vtu'
                    print 'Interesting state found for %s=%g!' % (param_name, p),
                    # Check if we already stored that one.
                    already_found = False
                    for state in found_solutions:
                        # Synchronize the complex argument.
                        state *= np.exp(1j * (np.angle(psi[0]) - np.angle(state[0])))
                        diff = psi - state
                        if modeleval.inner_product(diff, diff) < 1.0e-10:
                            already_found = True
                            break
                    if already_found:
                        print '-- But we already have that one.'
                    else:
                        found_solutions.append(psi)
                        print 'Storing in %s.' % filename
                        if len(k) == 2:
                            function_string = 'psi0(X) = %g * cos(%g*pi*x) * cos(%g*pi*y)' % (alpha, k[0], k[1])
                        elif len(k) == 3:
                            function_string = 'psi0(X) = %g * cos(%g*pi*x) * cos(%g*pi*y) * cos(%g*pi*z)' % (alpha, k[0], k[1], k[2])
                        else:
                            raise RuntimeError('Illegal k.')
                        modeleval.mesh.write(filename,
                                             point_data={'psi': psi,
                                                         'psi0': psi0,
                                                         'V': modeleval._V,
                                                         'A': modeleval._raw_magnetic_vector_potential
                                                         },
                                             field_data={'g': modeleval._g,
                                                         'mu': modeleval.mu,
                                                         'psi0(X)': function_string
                                                        }
                                             )
                        solution_id += 1
            print

    return
# ==============================================================================
def _parse_input_arguments():
    '''Parse input arguments.
    '''
    import argparse

    parser = argparse.ArgumentParser(description = 'Find solutions to a nonlinear Schrödinger equation.')

    parser.add_argument( 'filename',
                         metavar = 'FILE',
                         type    = str,
                         help    = 'File containing the geometry and initial state'
                       )

    parser.add_argument( '--parameter', '-p',
                         required = True,
                         choices = ['mu', 'g'],
                         type    = str,
                         help    = 'Which parameter to sweep'
                       )

    parser.add_argument( '--parameter-range', '-r',
                         required = True,
                         nargs = 2,
                         type    = float,
                         help    = 'Range for parameter sweep'
                       )

    parser.add_argument( '--num-parameter-steps', '-n',
                         metavar = 'NUMSTEPS',
                         required = True,
                         type    = int,
                         help    = 'Number of steps in the parameter range'
		       )

    parser.add_argument( '--forcing-term', '-f',
                         required = True,
                         choices = ['constant', 'type 1', 'type 2'],
                         type    = str,
                         help    = 'Forcing term for Newton''s method'
		       )

    return parser.parse_args()
# ==============================================================================
if __name__ == '__main__':
    _main()
# ==============================================================================
