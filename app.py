"""
app.py
------
FleetOS application entry point.

Creates and configures the FastAPI application instance. Responsible for:
  - Lifespan context (startup and shutdown hooks)
  - Middleware registration
  - Router registration (grouped by domain — added as each domain is implemented)
  - Root health check endpoint

Run with:
    uvicorn app:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings

# database.py is imported so that Base and engine exist in the process.
# create_all is intentionally NOT called here — schema migrations are managed
# exclusively by Alembic. Importing the module is sufficient to ensure the
# metadata object is populated when Alembic's env.py references it.
from database import Base, engine  # noqa: F401


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown.

    Startup  — runs before the server begins accepting requests.
    Shutdown — runs after the server stops accepting requests and all
               in-flight requests have completed.

    Use this context to open/close external connections (message brokers,
    background task queues, etc.) as the application grows. Database
    connections are managed per-request via get_db() and do not need
    explicit startup/shutdown here.
    """
    # -- Startup -----------------------------------------------------------
    # Nothing to initialise yet. Add connection setup here as needed.
    yield
    # -- Shutdown ----------------------------------------------------------
    # Nothing to tear down yet. Add cleanup logic here as needed.


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "FleetOS — school bus transportation management system. "
        "Manages districts, operators, drivers, buses, routes, runs, "
        "students, assignments, inspections, incidents, and alerts."
    ),
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

# CORS — all origins permitted during development.
# TODO: restrict allow_origins to explicit frontend domain(s) in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
# Routers are registered below as each domain layer is implemented.
# Import pattern for each:
#   from backend.routers.<module> import router as <name>_router
#   app.include_router(<name>_router, prefix="/api/<name>", tags=["<Name>"])
#
# -- Auth & system (identity, access control) ------------------------------
#   auth_router        → backend/routers/auth.py
#   system_router      → backend/routers/system.py
#
# -- Planning (static configuration) --------------------------------------
#   districts_router   → backend/routers/districts.py
#   operators_router   → backend/routers/operators.py
#   yards_router       → backend/routers/yards.py
#   schools_router     → backend/routers/schools.py
#   routes_router      → backend/routers/routes.py
#   stops_router       → backend/routers/stops.py
#   students_router    → backend/routers/students.py
#   drivers_router     → backend/routers/drivers.py
#   buses_router       → backend/routers/buses.py
#
# -- Assignments (linking planning entities) -------------------------------
#   assignments_router → backend/routers/assignments.py
#
# -- Execution (operational day) ------------------------------------------
#   runs_router        → backend/routers/runs.py
#   dispatchers_router → backend/routers/dispatchers.py
#
# -- Execution workflow (per-run forms) ------------------------------------
#   pretrip_router     → backend/routers/pretrip.py      (not yet created)
#   posttrip_router    → backend/routers/posttrip.py     (not yet created)
#   incidents_router   → backend/routers/incidents.py    (not yet created)
#   absences_router    → backend/routers/absences.py     (not yet created)
#   confirmations_router → backend/routers/school_confirmation.py (not yet created)
#
# -- Alerts ----------------------------------------------------------------
#   alerts_router      → backend/routers/alerts.py       (not yet created)
#
# -- Reports & audit -------------------------------------------------------
#   reports_router     → backend/routers/reports.py
#   payroll_router     → backend/routers/payroll.py
#   shop_router        → backend/routers/shop.py
#
# -- WebSocket (real-time updates) ----------------------------------------
#   websocket_router   → (not yet designed)

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/", tags=["Health"])
def health_check():
    """
    Root health check endpoint.

    Returns the project name, version, and a static "ok" status string.
    Used by load balancers, container orchestrators, and uptime monitors to
    confirm the application process is running and reachable.

    Returns:
        dict: {
            "project": str   — value of settings.PROJECT_NAME,
            "version": str   — value of settings.VERSION,
            "status":  str   — always "ok" if this response is reached,
        }
    """
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ok",
    }
