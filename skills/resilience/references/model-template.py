# Resilience model for <project>: availability, RPO, RTO. Edit ASSUMPTIONS, compute(), LIMITS; run check_resilience.py to see results.
# Plain arithmetic, stdlib only. best = most favourable for the limits, worst = least favourable.

ASSUMPTIONS = {
    "RA-1": {"label": "node failures per year", "unit": "1/year", "best": 0.5, "expected": 1.0, "worst": 2.0},
    "RA-2": {"label": "detection time", "unit": "h", "best": 0.1, "expected": 0.5, "worst": 4.0},
    "RA-3": {"label": "restore from backup", "unit": "h", "best": 2, "expected": 6, "worst": 12},
    "RA-4": {"label": "replacement hardware lead time", "unit": "h", "best": 0, "expected": 24, "worst": 72},
    "RA-5": {"label": "backup interval", "unit": "h", "best": 1, "expected": 4, "worst": 24},
}
UNITS = {"downtime_h_month": "h/month", "availability_pct": "%", "rpo_h": "h", "rto_h": "h"}

def compute(a):
    rto = a["RA-2"] + a["RA-4"] + a["RA-3"]                       # time to recover one node failure
    downtime_month = a["RA-1"] / 12.0 * rto                        # expected downtime per month
    availability = 100.0 * (1 - downtime_month / 730.0)
    return {"rto_h": rto, "rpo_h": a["RA-5"], "downtime_h_month": downtime_month, "availability_pct": availability}

LIMITS = [
    {"id": "RL-1", "metric": "availability_pct", "op": ">=", "limit": 99.0, "req": "NFR-11", "label": "availability"},
    {"id": "RL-2", "metric": "rpo_h", "op": "<=", "limit": 24, "req": "NFR-11", "label": "data loss window"},
]
