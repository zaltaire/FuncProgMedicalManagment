from functools import lru_cache
from core.domain import Appointment

# Lab 3
@lru_cache(maxsize=128)
def predict_load(
    day_str: str,
    appts_index: tuple[Appointment, ...]
) -> tuple[tuple[str, int], ...]:
    # day_str formatted as "YYYY-MM-DD"
    # we return a tuple of tuples: (doctor_id, load)
    counts: dict[str, int] = {}
    for appt in appts_index:
        appt_day = appt.when.strftime("%Y-%m-%d")
        if appt_day == day_str:
            counts[appt.doctor_id] = counts.get(appt.doctor_id, 0) + 1
            
    # Simulate an expensive computation by doing something slow
    # (In a real scenario, this would be an ML model or complex logic)
    import time
    time.sleep(0.5) 
    
    return tuple(sorted(counts.items()))

