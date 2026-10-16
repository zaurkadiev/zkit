# Resource model for <project>. Edit ASSUMPTIONS, compute(), LIMITS; run check_resource_math.py to see results.
# Plain arithmetic, stdlib only. One formula per line, comment names the resource. Keep it small.

ASSUMPTIONS = {   # best = most favourable for the limits, worst = least favourable
    "A-1": {"label": "active share of environments at peak", "unit": "ratio", "best": 0.10, "expected": 0.20, "worst": 0.40},
    "A-2": {"label": "memory per active environment", "unit": "MB", "best": 400, "expected": 600, "worst": 900},
    "A-3": {"label": "server memory", "unit": "MB", "best": 16384, "expected": 16384, "worst": 16384},
    "A-4": {"label": "server price", "unit": "EUR/month", "best": 30, "expected": 40, "worst": 55},
}

UNITS = {"envs_per_server": "envs", "cost_per_env": "EUR/month"}

def compute(a):
    envs_per_server = a["A-3"] / (a["A-2"] * a["A-1"])   # memory: how many environments one server holds
    cost_per_env = a["A-4"] / envs_per_server            # money: price of one environment
    return {"envs_per_server": envs_per_server, "cost_per_env": cost_per_env}

LIMITS = [   # every numeric requirement / budget the math can test
    {"id": "L-1", "metric": "cost_per_env", "op": "<=", "limit": 2.0, "req": "NFR-3", "label": "environment cost within the per-organization target"},
]
