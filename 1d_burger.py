#! /usr/bin/env python
#
from fenics import *
import numpy as np
import scipy.linalg as spla
import matplotlib.pyplot as plt
from solvers import CustomSolver
from problems import CustomProblem

def burgers_time_viscous ( e_num, nu ):

#*****************************************************************************80
#
## burgers_time_viscous, 1D time-dependent viscous Burgers equation.
#
#  Discussion:
#
#    dudt - nu u" + u del u = 0,
#    -1 < x < 1, 0 < t
#    u(-1,t) = -1, u(1,t) = 1
#    u(x,0) = x
#
#    This equation is nonlinear in U.
#
#  Licensing:
#
#    This code is distributed under the GNU LGPL license.
#
#  Modified:
#
#    21 October 2018
#
#  Author:
#
#    John Burkardt
#
#  Parameters:
#
#    Input, integer E_NUM, the number of elements to use.
#
#    Input, real NU, the viscosity, which should be positive.
#    The larger it is, the smoother the solution will be.
#


  print ( '' )
  print ( '  Number of elements is %d' % ( e_num ) )
  print ( '  Viscosity set to %g' % ( nu ) )

  class PeriodicBoundary(SubDomain):

    # Left boundary is "target domain" G
    def inside(self, x, on_boundary):
      return bool(x[0] < DOLFIN_EPS and x[0] > -DOLFIN_EPS and on_boundary)

    # Map right boundary (H) to left boundary (G)
    def map(self, x, y):
      y[0] = x[0] - 2.0

# Create periodic boundary condition
  pbc = PeriodicBoundary()
#
#  Create a mesh on the interval [0,+1].
#
  x_left = 0.0
  x_right = +2.0
  mesh = IntervalMesh ( e_num, x_left, x_right )
#
#  Define the function space to be of Lagrange type
#  using piecewise linear basis functions.
#
  t_num = 1000
  k = 0
  t = 0.0

  t_plot = 0.0
  t_final = 0.5

  V = FunctionSpace ( mesh, "CG", 1)
  snapshots = np.zeros((e_num+1, t_num+1))
#
#  Define the boundary conditions.
 # if X <= XLEFT + eps, then U = U_LEFT
 # if X_RIGHT - eps <= X, then U = U_RIGHT

  u_left = +1.0
  def on_left ( x, on_boundary ):
    return ( on_boundary and near ( x[0], x_left ) )
  bc_left = DirichletBC ( V, u_left, on_left )

  u_right = +1.0
  def on_right ( x, on_boundary ):
    return ( on_boundary and near ( x[0], x_right ) )
  bc_right = DirichletBC ( V, u_right, on_right )

  bc = [ bc_left, bc_right ]
  # bc = []

  # Sub domain for Periodic boundary condition


#
#  Define the initial condition.
#
  # u_init = Expression ( "x[0]", degree = 1 )
  u_init = Expression ( "x[0] < 1 ? 1+A*(sin(2*pi*x[0]-pi/2)+1) : 1", degree = 1, A = nu/2 )
  # u_init = Expression ( "1+A*(sin(10*pi*x[0]-pi/2)+1)", degree = 1, A = nu/2 )

#
#  Define the trial functions (u) and test functions (v).
#
  u = Function ( V )
  u_old = Function ( V )
  v = TestFunction ( V )
#
#  Set U and U0 by interpolation.
#
  u.interpolate ( u_init )
  u_old.assign ( u )
#
#  Set the time step.
#  We need a UFL version "DT" for the function F,
#  and a Python version "dt" to do a conditional in the time loop.
#


  DT = Constant ( t_final/t_num )
  dt = t_final/t_num
#
#  Set the source term.
#
  f = Expression ( "0.0", degree = 0 )
#
#  Write the function to be satisfied.
#
  n = FacetNormal ( mesh )
#
#  Write the function F.
#
  # F = \
  # ( \
  #   dot ( u - u_old, v ) / DT \
  # + nu * inner ( grad ( u ), grad ( v ) ) \
  # + inner ( u * u.dx(0), v ) \
  # - dot ( f, v ) \
  # ) * dx

  F = \
  ( \
    dot ( u - u_old, v ) / DT \
  + inner ( u * u.dx(0), v ) \
  - dot ( f, v ) \
  ) * dx
#
#  Specify the jacobian.
#
  J = derivative ( F, u )
#
#  Do the time integration.
#





  while ( True ):

    if ( k % 25 == 0 ):
      # arr = u.vector().get_local()
      # snapshots[:,k] = arr
      # plot ( u, title = ( 'burgers time viscous %g' % ( t ) ) )
      plt.plot(V.tabulate_dof_coordinates(), u.vector().get_local())
      plt.grid ( True )
      filename = ( 'burgers_time_viscous_%d.png' % ( k ) )
      plt.savefig ( filename )
      print ( 'Graphics saved as "%s"' % ( filename ) )
      plt.close ( )
      t_plot = t_plot + 0.1

    if ( t_final <= t - dt):
      print ( '' )
      print ( 'Reached final time.' )
      break

    arr = u.vector().get_local()
    snapshots[:,k] = arr

    k = k + 1
    t = t + dt

    # solve ( F == 0, u, bc, J = J )
    problem = NonlinearVariationalProblem(F,u,bc,J);
    solver = NonlinearVariationalSolver(problem);
    solver.solve();

    u_old.assign ( u )



  return snapshots

def pod(snapshots, nu):
    podmodes, svals, _ = spla.svd(snapshots, full_matrices=False)
    filename = ( 'burgers_viscous_%g.png' % ( nu ) )
    plt.semilogy(svals, '.')
    plt.grid ( True )
    plt.title('$\mu = $' + str(nu))
    plt.savefig ( filename )

    # find pod dimension
    err_tol = 1e-5
    poddim = 1
    err = 1 - np.sum(svals[:poddim])/np.sum(svals)
    while (err > err_tol):
        poddim += 1
        err = 1 - np.sum(svals[:poddim])/np.sum(svals)

    print(poddim)

def burgers_time_viscous_test ( ):

#*****************************************************************************80
#
## burgers_time_viscous_test tests burgers_time_viscous.
#
#  Licensing:
#
#    This code is distributed under the GNU LGPL license.
#
#  Modified:
#
#    21 October 2018
#
#  Author:
#
#    John Burkardt
#
  import time

  print ( time.ctime ( time.time() ) )
#
#  Report level = only warnings or higher.
#
  # level = 30
  # set_log_level ( level )

  # print ( '' )
  # print ( 'burgers_time_viscous_test:' )
  # print ( '  FENICS/Python version' )
  # print ( '  Solve the time-dependent 1d viscous Burgers equation.' )

  e_num = 1000
  # nu = 0.05
  # nus = [1/10**i for i in range(11)]
  nus = [1.0]
  for nu in nus:
      print( 'nu = %g' % ( nu ) )
      snapshots = burgers_time_viscous ( e_num, nu )
      # svd
      pod(snapshots, nu)
#
#  Terminate.
#
  # print ( "" )
  # print ( "burgers_time_viscous_test:" )
  # print ( "  Normal end of execution." )
  # print ( '' )
  # print ( time.ctime ( time.time() ) )



  return

if ( __name__ == '__main__' ):

  burgers_time_viscous_test ( )