def check_readiness(
    testing_completed,
    approval_obtained,
    implementation_plan,
    rollback_plan,
    documentation_ready
):
    checks = {
        "Testing Completed": testing_completed,
        "Approval Obtained": approval_obtained,
        "Implementation Plan": bool(implementation_plan.strip()),
        "Rollback Plan": bool(rollback_plan.strip()),
        "Documentation Ready": documentation_ready
    }

    ready = all(checks.values())

    return ready, checks