from __future__ import annotations
from core.domain import Service

# Lab 2
def flatten_services(roots: tuple[Service, ...]) -> tuple[Service, ...]:
    def flatten_single(srv: Service) -> tuple[Service, ...]:
        result = (srv,)
        for child in srv.children:
            result = result + flatten_single(child)
        return result

    result: tuple[Service, ...] = ()
    for root in roots:
        result = result + flatten_single(root)
    return result

def find_service_by_code(roots: tuple[Service, ...], code: str) -> Service | None:
    for root in roots:
        if root.code == code:
            return root
        found_in_children = find_service_by_code(root.children, code)
        if found_in_children is not None:
            return found_in_children
    return None

def sum_prices_recursive(root: Service) -> float:
    return root.price + sum(sum_prices_recursive(child) for child in root.children)
