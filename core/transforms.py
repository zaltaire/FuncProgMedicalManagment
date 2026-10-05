from __future__ import annotations
import json
from datetime import datetime
from functools import reduce
from typing import Callable, Any
from core.domain import Patient, Doctor, Service, Appointment, Invoice

# Lab 1
def load_seed(path: str) -> tuple[
    tuple[Patient, ...], tuple[Doctor, ...], tuple[Service, ...],
    tuple[Appointment, ...], tuple[Invoice, ...]
]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    patients = tuple(Patient(**p) for p in data.get("patients", []))
    doctors = tuple(Doctor(**d) for d in data.get("doctors", []))
    
    def parse_service(s_dict: dict) -> Service:
        children_dicts = s_dict.get("children", [])
        children = tuple(parse_service(c) for c in children_dicts)
        return Service(code=s_dict["code"], title=s_dict["title"], price=s_dict["price"], children=children)
        
    services = tuple(parse_service(s) for s in data.get("services", []))
    
    appointments = tuple(
        Appointment(
            id=a["id"], patient_id=a["patient_id"], doctor_id=a["doctor_id"],
            when=datetime.fromisoformat(a["when"]), status=a["status"]
        ) for a in data.get("appointments", [])
    )
    
    invoices = tuple(
        Invoice(
            id=i["id"], patient_id=i["patient_id"], items=tuple(i["items"]),
            amount=i["amount"], insurance=i.get("insurance")
        ) for i in data.get("invoices", [])
    )
    
    return patients, doctors, services, appointments, invoices

def add_appointment(
    appts: tuple[Appointment, ...], new_appt: Appointment
) -> tuple[Appointment, ...]:
    return appts + (new_appt,)

def update_patient_contact(
    pats: tuple[Patient, ...], pid: str, contact: str
) -> tuple[Patient, ...]:
    return tuple(
        Patient(id=p.id, name=p.name, contact=contact) if p.id == pid else p
        for p in pats
    )

def total_revenue(invoices: tuple[Invoice, ...]) -> float:
    return reduce(lambda acc, inv: acc + inv.amount, invoices, 0.0)

# Lab 2
def by_doctor(doctor_id: str) -> Callable[[Appointment], bool]:
    def predicate(appt: Appointment) -> bool:
        return appt.doctor_id == doctor_id
    return predicate

def by_date_range(start: datetime, end: datetime) -> Callable[[Appointment], bool]:
    def predicate(appt: Appointment) -> bool:
        return start <= appt.when <= end
    return predicate

def make_price_adjuster(percent: float) -> Callable[[Service], Service]:
    def adjuster(srv: Service) -> Service:
        new_children = tuple(adjuster(child) for child in srv.children)
        return Service(
            code=srv.code, 
            title=srv.title, 
            price=srv.price * (1 + percent / 100.0), 
            children=new_children
        )
    return adjuster
