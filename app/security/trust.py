import math

# phi_e — CogTrust's per-element weights (severity)
ELEMENT_WEIGHTS = {
    "role_consistency": 1.0,   # Role Cognition
    "grounding":        1.5,   # Generated Content — worst failure
    "task_adherence":   1.2,   # did it do its assigned job
    "evidence_use":     1.0,   # Actions Trajectory
}

LAMBDA_POS = 0.3   # weight on positive evidence
TAU_NEG    = 0.7   # weight on negative evidence  (lambda < tau)
PRIOR_C    = 2.0   # uncertainty prior
BASE_RATE  = 0.5   # a — where a brand-new agent starts
DECAY      = 0.3   # in m_i = e^(-DECAY * i)
WINDOW     = 10


def round_opinion(positive, negative):
    """One round's reputation, CogTrust Eq. 5 and 7."""
    alpha = sum(ELEMENT_WEIGHTS.get(e, 1.0) for e in positive)
    beta  = sum(ELEMENT_WEIGHTS.get(e, 1.0) for e in negative)

    denom = LAMBDA_POS * alpha + TAU_NEG * beta + PRIOR_C
    belief      = (LAMBDA_POS * alpha) / denom
    uncertainty = PRIOR_C / denom

    return belief + BASE_RATE * uncertainty


def reputation(rounds):
    """Time-decayed average over recent rounds, CogTrust Eq. 8.
       rounds[0] is the newest."""
    if not rounds:
        return BASE_RATE

    numerator = 0.0
    denominator = 0.0

    for i, r in enumerate(rounds[:WINDOW]):
        m = math.exp(-DECAY * i)
        numerator += m * round_opinion(r["positive"], r["negative"])
        denominator += m

    return round(numerator / denominator, 3)