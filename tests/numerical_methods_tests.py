import numerical_methods
import numpy as np
import scipy
import unittest
# ==============================================================================
class TestLinearSolvers(unittest.TestCase):
    # --------------------------------------------------------------------------
    def setUp(self):
        return
    # --------------------------------------------------------------------------
    def _create_sym_matrix( self, num_unknowns ):
        A = np.random.rand(num_unknowns, num_unknowns)
        A = 0.5 * ( A + A.transpose() )
        return A
    # --------------------------------------------------------------------------
    def _create_spd_matrix( self, num_unknowns ):
        A = self._create_sym_matrix( num_unknowns )
        # Make sure that the lowest eigenvalue is 1.
        D,V = np.linalg.eig( A )
        A = A + (1.0-min(D)) * np.eye( num_unknowns )
        return A
    # --------------------------------------------------------------------------
    def _create_sym_indef_matrix( self, num_unknowns ):
        A = self._create_sym_matrix( num_unknowns )
        # Make sure that the lowest eigenvalue is -1 and the largest 1.
        D,V = np.linalg.eig( A )
        I = np.eye( num_unknowns ) 
        A = 2.0 / (max(D)-min(D)) * (A - min(D) * I) - 1.0 * I
        return A
    # --------------------------------------------------------------------------
    def test_cg_dense(self):
        # Create dense problem.
        num_unknowns = 5
        A = self._create_spd_matrix( num_unknowns )
        rhs = np.random.rand(num_unknowns)
        x0 = np.zeros( num_unknowns )
        # Solve using CG.
        tol = 1.0e-13
        x, info = numerical_methods.cg( A, rhs, x0, tol=tol )
        # Make sure the method converged.
        self.assertEqual(info, 0)
        # Check the residual.
        res = rhs - np.dot(A, x)
        self.assertAlmostEqual( np.linalg.norm(res), 0.0, delta=tol )
    # --------------------------------------------------------------------------
    def test_cg_sparse(self):
        # Create sparse problem.
        num_unknowns = 100
        data = np.array([ -1.0 * np.ones(num_unknowns),
                           2.0 * np.ones(num_unknowns),
                          -1.0 * np.ones(num_unknowns)
                       ])
        diags = np.array([-1,0,1])
        A = scipy.sparse.spdiags(data, diags, num_unknowns, num_unknowns)
        rhs = np.random.rand(num_unknowns)
        x0 = np.zeros( num_unknowns )
        # Solve using CG.
        tol = 1.0e-11
        x, info = numerical_methods.cg( A, rhs, x0, tol=tol )
        # Make sure the method converged.
        self.assertEqual(info, 0)
        # Check the residual.
        res = rhs - A * x
        self.assertAlmostEqual( np.linalg.norm(res), 0.0, delta=tol )
    # --------------------------------------------------------------------------
    def test_minres_dense(self):
        # Create regular dense problem.
        num_unknowns = 5
        A = self._create_sym_indef_matrix( num_unknowns )
        rhs = np.random.rand( num_unknowns )
        x0 = np.zeros( num_unknowns )
        # Solve using MINRES.
        tol = 1.0e-13
        x, info = numerical_methods.minres( A, rhs, x0, tol=tol )
        # Make sure the method converged.
        self.assertEqual(info, 0)
        # Check the residual.
        res = rhs - np.dot(A, x)
        self.assertAlmostEqual( np.linalg.norm(res), 0.0, delta=tol )
    # --------------------------------------------------------------------------
    def test_minres_dense_complex(self):
        # Create regular dense problem.
        num_unknowns = 3
        A = np.array( [[1,-2+1j,0], [-2-1j,2,-1], [0,-1,3]] )
        rhs = np.ones( num_unknowns )
        x0 = np.zeros( num_unknowns )
        # Solve using MINRES.
        tol = 1.0e-15
        x, info = numerical_methods.minres( A, rhs, x0, tol=tol )
        # Make sure the method converged.
        self.assertEqual(info, 0)
        # Check the residual.
        res = rhs - np.dot(A, x)
        self.assertAlmostEqual( np.linalg.norm(res), 0.0, delta=tol )
    # --------------------------------------------------------------------------
    def test_minres_sparse(self):
        # Create sparse symmetric problem.
        num_unknowns = 100
        data = np.array([ -1.0 * np.ones(num_unknowns),
                           2.0 * np.ones(num_unknowns),
                          -1.0 * np.ones(num_unknowns)
                       ])
        diags = np.array([-1,0,1])
        A = scipy.sparse.spdiags(data, diags, num_unknowns, num_unknowns)
        rhs = np.random.rand(num_unknowns)
        x0 = np.zeros( num_unknowns )
        # Solve using CG.
        tol = 1.0e-11
        x, info = numerical_methods.cg( A, rhs, x0, tol=tol )
        # Make sure the method converged.
        self.assertEqual(info, 0)
        # Check the residual.
        res = rhs - A * x
        self.assertAlmostEqual( np.linalg.norm(res), 0.0, delta=tol )
    # --------------------------------------------------------------------------
    def test_lobpcg(self):
        num_unknowns = 5
        data = np.array([ -1.0 * np.ones(num_unknowns),
                           2.0 * np.ones(num_unknowns),
                          -1.0 * np.ones(num_unknowns)
                       ])
        diags = np.array([-1,0,1])
        A = scipy.sparse.spdiags(data, diags, num_unknowns, num_unknowns)
        rhs = np.random.rand(num_unknowns)
        x0 = np.zeros( (num_unknowns,1) )
        x0[:,0] = np.random.rand( num_unknowns )
        w, v = scipy.sparse.linalg.lobpcg(A, x0, maxiter=10000, largest=True, verbosityLevel=0 )
        tol = 1.0e-11
        res = A*v - w*v
        self.assertAlmostEqual( np.linalg.norm(res), 0.0, delta=tol )
    # --------------------------------------------------------------------------
# ==============================================================================
if __name__ == '__main__':
    unittest.main()
# ==============================================================================
