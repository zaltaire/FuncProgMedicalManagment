from __future__ import annotations
from typing import Generic, TypeVar, Callable, Any
from core.domain import Patient, Invoice

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')

class Maybe(Generic[T]):
    def map(self, fn: Callable[[T], U]) -> 'Maybe[U]':
        raise NotImplementedError

    def bind(self, fn: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        raise NotImplementedError

    def get_or_else(self, default: U) -> T | U:
        raise NotImplementedError

class Just(Maybe[T]):
    def __init__(self, value: T):
        self.value = value

    def map(self, fn: Callable[[T], U]) -> 'Just[U]':
        return Just(fn(self.value))

    def bind(self, fn: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return fn(self.value)

    def get_or_else(self, default: U) -> T | U:
        return self.value

class Nothing(Maybe[T]):
    def map(self, fn: Callable[[T], U]) -> 'Nothing[U]':
        return Nothing()

    def bind(self, fn: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return Nothing()

    def get_or_else(self, default: U) -> T | U:
        return default

class Either(Generic[E, T]):
    def map(self, fn: Callable[[T], U]) -> 'Either[E, U]':
        raise NotImplementedError

    def bind(self, fn: Callable[[T], 'Either[E, U]']) -> 'Either[E, U]':
        raise NotImplementedError
        
    def get_or_else(self, default: U) -> T | U:
        raise NotImplementedError

class Left(Either[E, T]):
    def __init__(self, error: E):
        self.error = error

    def map(self, fn: Callable[[T], U]) -> 'Left[E, U]':
        return Left(self.error)

    def bind(self, fn: Callable[[T], Either[E, U]]) -> Either[E, U]:
        return Left(self.error)
        
    def get_or_else(self, default: U) -> T | U:
        return default

class Right(Either[E, T]):
    def __init__(self, value: T):
        self.value = value

    def map(self, fn: Callable[[T], U]) -> 'Right[E, U]':
        return Right(fn(self.value))

    def bind(self, fn: Callable[[T], Either[E, U]]) -> Either[E, U]:
        return fn(self.value)
        
    def get_or_else(self, default: U) -> T | U:
        return self.value

# Lab 4 wrapping risky operations

def safe_find_patient(pats: tuple[Patient, ...], pid: str) -> Maybe[Patient]:
    for p in pats:
        if p.id == pid:
            return Just(p)
    return Nothing()

def validate_invoice(inv: Invoice) -> Either[str, Invoice]:
    if not inv.items:
        return Left("Invoice has no items")
    if inv.amount <= 0:
        return Left("Invoice amount must be greater than zero")
    return Right(inv)
