#!/usr/bin/env python

## 
 # -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "solver.py"
 #                                    created: 11/14/03 {3:47:20 PM} 
 #                                last update: 11/16/06 {2:36:00 PM} 
 #  Author: Jonathan Guyer <guyer@nist.gov>
 #  Author: Daniel Wheeler <daniel.wheeler@nist.gov>
 #  Author: James Warren   <jwarren@nist.gov>
 #    mail: NIST
 #     www: http://www.ctcms.nist.gov/fipy/
 #  
 # ========================================================================
 # This software was developed at the National Institute of Standards
 # and Technology by employees of the Federal Government in the course
 # of their official duties.  Pursuant to title 17 Section 105 of the
 # United States Code this software is not subject to copyright
 # protection and is in the public domain.  FiPy is an experimental
 # system.  NIST assumes no responsibility whatsoever for its use by
 # other parties, and makes no guarantees, expressed or implied, about
 # its quality, reliability, or any other characteristic.  We would
 # appreciate acknowledgement if the software is used.
 # 
 # This software can be redistributed and/or modified freely
 # provided that any derivative works bear some notice that they are
 # derived from it, and any modified versions bear some notice that
 # they have been modified.
 # ========================================================================
 #  
 #  Description: 
 # 
 #  History
 # 
 #  modified   by  rev reason
 #  ---------- --- --- -----------
 #  2003-11-14 JEG 1.0 original
 # ###################################################################
 ##

"""
The iterative solvers may output warnings if the solution is considered
unsatisfactory. If you are not interested in these warnings, you can invoke
python with a warning filter such as::
    
    $ python -Wignore::fipy.SolverConvergenceWarning myscript.py
    
If you are extremely concerned about your preconditioner for some reason, you 
can abort whenever it has problems with::
    
    $ python -Werror::fipy.PreconditionerWarning myscript.py
    
"""
__docformat__ = 'restructuredtext'

class SolverConvergenceWarning(Warning):
    def __init__(self, solver, iter, relres):
        self.solver = solver
        self.iter = iter
        self.relres = relres
    
    def __str__(self):
        return "%s failed. Iterations: %g. Relative error: %g" % (str(self.solver), self.iter, self.relres)

class MaximumIterationWarning(SolverConvergenceWarning):
    def __str__(self):
        return "Iterations: %g. Relative error: %g" % (self.iter, self.relres)
        
class PreconditionerWarning(SolverConvergenceWarning):
    pass
    
class IllConditionedPreconditionerWarning(PreconditionerWarning):
    def __str__(self):
        return "The system involving the preconditioner was ill-conditioned. Relative error: %g" % (self.relres)
    
class PreconditionerNotPositiveDefiniteWarning(PreconditionerWarning):
    def __str__(self):
        return "The preconditioning matrix does not appear to be positive definite. Relative error: %g" % (self.relres)
    
class MatrixIllConditionedWarning(SolverConvergenceWarning):
    def __str__(self):
        return "The matrix appears to be very ill-conditioned. Relative error: %g" % (self.relres)
    
class StagnatedSolverWarning(SolverConvergenceWarning):
    def __str__(self):
        return "The solver stagnated. Iterations: %g. Relative error: %g" % (self.iter, self.relres)
    
class ScalarQuantityOutOfRangeWarning(SolverConvergenceWarning):
    def __str__(self):
        return "A scalar quantity became too small or too large to continue computing. Iterations: %g. Relative error: %g" % (self.iter, self.relres)

class Solver:
    """
    The base `LinearXSolver` class.
    
    .. attention:: This class is abstract. Always create one of its subclasses.
    """

    def __init__(self, tolerance=1e-10, iterations=1000, steps=None):
        """
        Create a `Solver` object.

        :Parameters:
          - `tolerance`: The required error tolerance.
          - `iterations`: The maximum number of iterative steps to perform.
          - `steps`: A deprecated name for `iterations`.

        """
	self.tolerance = tolerance
        if steps is not None:
            import warnings
            warnings.warn("'iterations' should be used instead of 'steps'", DeprecationWarning, stacklevel=2)
            self.iterations = steps
        else:
            self.iterations = iterations
	
    def _solve(self, L, x, b):
	pass
        
    _warningList = (ScalarQuantityOutOfRangeWarning,
                    StagnatedSolverWarning,
                    MatrixIllConditionedWarning,
                    PreconditionerNotPositiveDefiniteWarning,
                    IllConditionedPreconditionerWarning,
                    MaximumIterationWarning)
    
    def _raiseWarning(self, info, iter, relres):
        # info is negative, so we list in reverse order so that 
        # info can be used as an index from the end
                       
        if info < 0:
            # is stacklevel=5 always what's needed to get to the user's scope?
            import warnings
            warnings.warn(self._warningList[info](self, iter, relres), stacklevel=5)
        
    def __repr__(self):
        return '%s(tolerance=%g, iterations=%g)' \
            % (self.__class__.__name__, self.tolerance, self.iterations)

    def _canSolveAssymetric(self):
        return True

    def _getMatrixClass(self):
        from fipy.tools.pysparseMatrix import _PysparseMatrix
        return _PysparseMatrix

    def setPreconditioner(self, preconditioner):
        """
        Define which preconditioner the solver should use.
        Only available for Trilinos solvers.
        
        :Parameters:
        - `preconditioner`: the preconditioner object to use.
        """
        import warnings 
        warnings.warn("This solver does not support user-specified preconditioners. That functionality is only available in the Trilinos solvers.", UserWarning, stacklevel=2)
