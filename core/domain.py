from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Patient:
    """Пациент клиники"""
    id: str
    name: str
    contact: str


@dataclass(frozen=True)
class Doctor:
    """Врач"""
    id: str
    name: str
    specialty: str


@dataclass(frozen=True)
class Service:
    """Медицинская услуга (может содержать вложенные дочерние услуги)"""
    code: str
    title: str
    price: float
    children: tuple["Service", ...] = ()


@dataclass(frozen=True)
class Appointment:
    """Запись на прием"""
    id: str
    patient_id: str
    doctor_id: str
    when: datetime
    status: str  # Возможные значения: "new", "canceled", "done"


@dataclass(frozen=True)
class Invoice:
    """Счет на оплату"""
    id: str
    patient_id: str
    items: tuple[str, ...]  # Список кодов/названий услуг
    amount: float
    insurance: str | None = None