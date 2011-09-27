from pypy.translator.stm._rffi_stm import *
from pypy.translator.stm.rstm import *
from pypy.rpython.annlowlevel import llhelper


def test_stm_getfield():
    A = lltype.Struct('A', ('x', lltype.Signed), ('y', lltype.Signed))
    a = lltype.malloc(A, immortal=True, flavor='raw')
    a.x = -611
    a.y = 0
    def callback1(x):
        assert a.x == -611
        assert stm_getfield(a, 'x') == -611
        p = lltype.direct_fieldptr(a, 'x')
        p = rffi.cast(rffi.VOIDPP, p)
        stm_write_word(p, rffi.cast(rffi.VOIDP, 42 * a.y))
        assert stm_getfield(a, 'x') == 42 * a.y
        assert a.x == -611 # xxx still the old value when reading non-transact.
        if a.y < 10:
            a.y += 1    # non-transactionally
            abort_and_retry()
        else:
            return lltype.nullptr(rffi.VOIDP.TO)
    descriptor_init()
    perform_transaction(llhelper(CALLBACK, callback1),
                        lltype.nullptr(rffi.VOIDP.TO))
    descriptor_done()
    assert a.x == 420

def test_stm_setfield():
    A = lltype.Struct('A', ('x', lltype.Signed), ('y', lltype.Signed))
    a = lltype.malloc(A, immortal=True, flavor='raw')
    a.x = -611
    a.y = 0
    def callback1(x):
        assert a.x == -611
        assert stm_getfield(a, 'x') == -611
        stm_setfield(a, 'x', 42 * a.y)
        assert stm_getfield(a, 'x') == 42 * a.y
        assert a.x == -611 # xxx still the old value when reading non-transact.
        if a.y < 10:
            a.y += 1    # non-transactionally
            abort_and_retry()
        else:
            return lltype.nullptr(rffi.VOIDP.TO)
    descriptor_init()
    perform_transaction(llhelper(CALLBACK, callback1),
                        lltype.nullptr(rffi.VOIDP.TO))
    descriptor_done()
    assert a.x == 420
