import pytest
from datetime import datetime
from core.domain import Patient, Doctor, Service, Appointment, Invoice
from core.transforms import (
    add_appointment, update_patient_contact, total_revenue,
    by_doctor, by_date_range, make_price_adjuster
)
from core.recursion import flatten_services, find_service_by_code, sum_prices_recursive
from core.memo import predict_load
from core.ftypes import safe_find_patient, validate_invoice, Just, Nothing, Right, Left

# Dummy Data
p1 = Patient(id="p1", name="Alice", contact="111")
p2 = Patient(id="p2", name="Bob", contact="222")
d1 = Doctor(id="d1", name="Dr. Smith", specialty="Cardiology")
s1 = Service(code="s1", title="Consultation", price=100.0, children=())
s2 = Service(code="s2", title="Surgery", price=500.0, children=(s1,))
a1 = Appointment(id="a1", patient_id="p1", doctor_id="d1", when=datetime(2023, 1, 1, 10, 0), status="new")
a2 = Appointment(id="a2", patient_id="p2", doctor_id="d1", when=datetime(2023, 1, 2, 10, 0), status="new")
i1 = Invoice(id="i1", patient_id="p1", items=("s1",), amount=100.0, insurance=None)
i2 = Invoice(id="i2", patient_id="p2", items=("s2",), amount=500.0, insurance=None)

# Lab 1 Tests
def test_models_are_immutable():
    with pytest.raises(Exception):
        p1.name = "Eve"

def test_add_appointment():
    appts = (a1,)
    new_appts = add_appointment(appts, a2)
    assert len(new_appts) == 2
    assert new_appts[-1] == a2
    # Ensure immutability of original
    assert len(appts) == 1

def test_update_patient_contact():
    pats = (p1, p2)
    new_pats = update_patient_contact(pats, "p1", "333")
    assert new_pats[0].contact == "333"
    assert new_pats[1].contact == "222"
    assert pats[0].contact == "111"  # Original unchanged

def test_total_revenue():
    assert total_revenue((i1, i2)) == 600.0

def test_total_revenue_empty():
    assert total_revenue(()) == 0.0

# Lab 2 Tests
def test_by_doctor_closure():
    f = by_doctor("d1")
    assert f(a1) is True
    a3 = Appointment(id="a3", patient_id="p1", doctor_id="d2", when=datetime(2023, 1, 1), status="new")
    assert f(a3) is False

def test_by_date_range_closure():
    f = by_date_range(datetime(2023, 1, 1), datetime(2023, 1, 1, 23, 59))
    assert f(a1) is True
    assert f(a2) is False

def test_make_price_adjuster():
    f = make_price_adjuster(10.0) # +10%
    new_s2 = f(s2)
    assert new_s2.price == pytest.approx(550.0)
    assert new_s2.children[0].price == pytest.approx(110.0)
    # Original unchanged
    assert s2.price == pytest.approx(500.0)

def test_flatten_services():
    res = flatten_services((s2,))
    assert len(res) == 2
    assert res[0].code == "s2"
    assert res[1].code == "s1"

def test_find_service_by_code():
    res1 = find_service_by_code((s2,), "s1")
    assert res1 == s1
    res2 = find_service_by_code((s2,), "s3")
    assert res2 is None

def test_sum_prices_recursive():
    assert sum_prices_recursive(s1) == 100.0
    assert sum_prices_recursive(s2) == 600.0

# Lab 3 Tests
def test_predict_load_caching():
    import time
    appts = (a1, a2)
    start1 = time.time()
    res1 = predict_load("2023-01-01", appts)
    end1 = time.time()
    
    start2 = time.time()
    res2 = predict_load("2023-01-01", appts)
    end2 = time.time()
    
    assert res1 == res2
    assert res1 == (("d1", 1),)
    assert (end2 - start2) < (end1 - start1) # Cache hit should be faster

def test_predict_load_pure():
    appts = (a1, a2)
    # The output should only depend on inputs
    res1 = predict_load("2023-01-01", appts)
    res2 = predict_load("2023-01-02", appts)
    assert res1 == (("d1", 1),)
    assert res2 == (("d1", 1),)

def test_predict_load_empty():
    assert predict_load("2023-01-03", (a1, a2)) == ()

def test_predict_load_cache_info():
    # Calling cache_info to ensure lru_cache is actually applied
    assert hasattr(predict_load, "cache_info")

def test_predict_load_no_mutations():
    appts = (a1,)
    predict_load("2023-01-01", appts)
    # the input arguments shouldn't be altered
    assert len(appts) == 1
    assert appts[0] == a1

# Lab 4 Tests
def test_maybe_map():
    j = Just(5)
    assert isinstance(j.map(lambda x: x * 2), Just)
    assert j.map(lambda x: x * 2).get_or_else(0) == 10
    n = Nothing()
    assert isinstance(n.map(lambda x: x * 2), Nothing)
    assert n.map(lambda x: x * 2).get_or_else(0) == 0

def test_either_bind():
    r = Right(5)
    assert isinstance(r.bind(lambda x: Right(x * 2)), Right)
    assert r.bind(lambda x: Right(x * 2)).get_or_else(0) == 10
    
    l = Left("err")
    assert isinstance(l.bind(lambda x: Right(x * 2)), Left)

def test_safe_find_patient():
    res = safe_find_patient((p1, p2), "p1")
    assert isinstance(res, Just)
    assert res.get_or_else(None) == p1
    
    res2 = safe_find_patient((p1, p2), "p3")
    assert isinstance(res2, Nothing)

def test_validate_invoice_valid():
    res = validate_invoice(i1)
    assert isinstance(res, Right)
    assert res.get_or_else(None) == i1

def test_validate_invoice_invalid():
    bad_inv = Invoice(id="i3", patient_id="p1", items=(), amount=0.0)
    res = validate_invoice(bad_inv)
    assert isinstance(res, Left)
    # The error should be related to items
    assert res.error == "Invoice has no items"
