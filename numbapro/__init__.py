from __future__ import absolute_import, print_function
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

import warnings
import re
import numba
from numba import *

# Numba version checking
m = re.match(r"(\d+)\.(\d+)\.(\d+).*", numba.__version__)
NUMBA_VERSION_REQ = (0, 17, 0)
if m is None or tuple(map(int, m.groups())) < NUMBA_VERSION_REQ:
    warnings.showwarning(
        "Numba version too old; expecting %d.%d.%d" % NUMBA_VERSION_REQ,
        ImportWarning, __name__, 1)
del m

import numbapro._cuda    # import time sideeffect
from numbapro.decorators import autojit, jit
from numbapro.vectorizers import vectorize, guvectorize

def test():
    from numbapro import cuda

    try:
        print('NumbaPro Tests')

        def failfast(ok):
            if not ok:
                raise Exception('Test Failed')

        print('vectorizers'.center(80, '-'))
        import numbapro.vectorizers.tests

        failfast(numbapro.vectorizers.tests.test())

        print('cuda libraries locator'.center(80, '-'))
        import numba.cuda.cudadrv.libs

        failfast(numba.cuda.cudadrv.libs.test())

        check_cuda()

        if numbapro.cuda.is_available():
            print('cudadrv'.center(80, '-'))
            import numbapro.cudadrv.tests

            failfast(numbapro.cudadrv.tests.test())

            print('cudalib'.center(80, '-'))
            import numbapro.cudalib.tests

            failfast(numbapro.cudalib.tests.test())

            print('cudapy'.center(80, '-'))
            import numbapro.cudapy.tests

            failfast(numbapro.cudapy.tests.test())

            print('cudavec'.center(80, '-'))
            import numbapro.cudavec.tests

            failfast(numbapro.cudavec.tests.test())

        else:
            print('skipped cuda tests')
    except Exception as e:
        import traceback

        traceback.print_exc()
        print('Test failed')
        return False
    else:
        print('All test passed')
        return True


def check_cuda():
    from numba.cuda import is_available, cuda_error

    if not is_available():
        print("CUDA is not available")
        print(cuda_error())
        return

    from numba.cuda.cudadrv import libs
    from numbapro import cuda

    ok = True

    print('libraries detection'.center(80, '-'))
    if not libs.test():
        ok = False

    print('hardware detection'.center(80, '-'))
    if not cuda.detect():
        ok = False

    # result
    if not ok:
        print('FAILED')
    else:
        print('PASSED')
    return ok


def _initialize_all():
    """
    Initialize extensions to Numba
    """
    from numba.npyufunc import Vectorize, GUVectorize

    def init_vectorize():
        from numbapro.cudavec.vectorizers import CudaVectorize
        return CudaVectorize

    def init_guvectorize():
        from numbapro.cudavec.vectorizers import CudaGUFuncVectorize
        return CudaGUFuncVectorize

    Vectorize.target_registry.ondemand['gpu'] = init_vectorize
    Vectorize.target_registry.ondemand['cuda'] = init_vectorize
    GUVectorize.target_registry.ondemand['gpu'] = init_guvectorize
    GUVectorize.target_registry.ondemand['cuda'] = init_guvectorize

_initialize_all()
del _initialize_all

_initialization_completed = True
