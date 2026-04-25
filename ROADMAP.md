# FleetOS – ROADMAP

---

## Architecture Decisions (Locked)

### Assignments
- All assignment types are handled in a single `assignments.py` file across models, schemas, services, and routers.
- There is no separate `student_placement` file or model. Student placement is part of `assignments.py`.
- Assignment types covered:
  - Route ↔ School
  - Route → Operator
  - Yard ↔ Route
  - Route ↔ Driver
  - Route ↔ Bus
  - Student → Route / Run / Stop

### Driver & Bus Assignment
- Drivers and buses are assigned at the **route level only** — not at the run level.
- One driver per route. One bus per route.
- All runs under a route inherit the same driver and bus.

### Run Readiness
- Readiness is determined at the **route level**.
  - **Not Ready** = route has no driver assigned, or no bus assigned, or neither.
  - **Ready** = route has both a driver and a bus assigned.

### Conflict Detection
- Conflicts are detected at the **route level**.
- A conflict occurs when the same driver or the same bus is assigned to two routes whose run times overlap.

---

## Missing Files (Placeholders To Be Created)

The following files do not exist yet and need to be created:

- `backend/models/user.py`
- `backend/models/membership.py`
- `backend/models/pretrip.py`
- `backend/models/posttrip.py`
- `backend/models/incident.py`
- `backend/models/alert.py`
- `backend/models/event.py`
- `backend/models/audit.py`
- `backend/models/school_confirmation.py`
- `backend/models/absence.py`
- `backend/routers/auth.py`
- `backend/routers/system.py`
- `backend/core/permissions.py`
