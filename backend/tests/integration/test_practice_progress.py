from datetime import date


def test_attempt_status_daily_activity_and_progress_summary(
    client, make_user, make_problem, auth_headers
):
    learner = make_user(timezone="Asia/Kolkata")
    problem = make_problem(tags=["Arrays"])
    next_problem = make_problem(title="Next Challenge", tags=["Arrays"])
    headers = auth_headers(learner)

    initial_status = client.get(
        f"/api/v1/problems/{problem.problem_id}/status", headers=headers
    )
    assert initial_status.json()["status"] == "not_started"
    response = client.post(
        "/api/v1/attempts",
        json={"problem_id": problem.problem_id, "outcome": "attempted", "language": "Python"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["verdict"] == "attempted"

    solved_attempt = client.post(
        "/api/v1/attempts",
        json={"problem_id": problem.problem_id, "outcome": "solved", "language": "Python"},
        headers=headers,
    )
    assert solved_attempt.status_code == 201
    assert client.get(
        f"/api/v1/problems/{problem.problem_id}/status", headers=headers
    ).json()["status"] == "solved"

    solved = client.put(
        f"/api/v1/problems/{problem.problem_id}/status",
        json={"status": "solved"},
        headers=headers,
    )
    assert solved.status_code == 200
    assert solved.json()["solved_at"] is not None
    summary = client.get("/api/v1/progress/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["total_solved"] == 1
    assert summary.json()["completed_today"] == 1
    assert summary.json()["by_topic"] == [{"name": "Arrays", "solved": 1}]
    assert summary.json()["by_difficulty"] == [{"name": "Easy", "solved": 1}]

    from app.services.activity import user_local_date

    local_today = user_local_date(learner).isoformat()
    activity = client.get(
        "/api/v1/progress/activity",
        params={"start_date": local_today, "end_date": local_today},
        headers=headers,
    )
    assert activity.status_code == 200
    assert activity.json()[0]["problems_solved"] == 1
    assert client.get("/api/v1/progress/streaks", headers=headers).json()["current_streak"] == 1
    recommendation = client.get("/api/v1/recommendations/next", headers=headers).json()
    assert recommendation["problem"]["problem_id"] == next_problem.problem_id


def test_activity_ranges_recommendation_empty_and_role_checks(
    client, make_user, make_problem, auth_headers
):
    learner = make_user()
    admin = make_user(role="admin")
    problem = make_problem()
    headers = auth_headers(learner)

    assert client.get("/api/v1/progress/activity").status_code == 401
    assert client.get("/api/v1/progress/summary", headers=auth_headers(admin)).status_code == 403
    assert client.get(
        "/api/v1/progress/activity",
        params={"start_date": "2026-01-02", "end_date": "2026-01-01"},
        headers=headers,
    ).status_code == 422
    assert client.get(
        "/api/v1/progress/activity",
        params={"start_date": "2024-01-01", "end_date": "2025-02-02"},
        headers=headers,
    ).status_code == 422

    recommendation = client.get("/api/v1/recommendations/next", headers=headers).json()
    assert recommendation["problem"]["problem_id"] == problem.problem_id
    assert client.put(
        f"/api/v1/problems/{problem.problem_id}/status",
        json={"status": "not_started"},
        headers=headers,
    ).status_code == 200


def test_plan_create_update_filter_and_delete(client, make_user, auth_headers):
    learner = make_user()
    headers = auth_headers(learner)
    plan_date = date.today().isoformat()

    created = client.put(
        f"/api/v1/plans/{plan_date}", json={"daily_goal": 3}, headers=headers
    )
    assert created.status_code == 200
    assert created.json()["daily_goal"] == 3
    updated = client.put(
        f"/api/v1/plans/{plan_date}", json={"daily_goal": 5}, headers=headers
    )
    assert updated.json()["daily_goal"] == 5
    assert client.put(
        f"/api/v1/plans/{plan_date}", json={"daily_goal": 0}, headers=headers
    ).status_code == 422
    assert len(client.get("/api/v1/plans", headers=headers).json()) == 1
    assert client.get(
        "/api/v1/plans?start_date=2026-01-02&end_date=2026-01-01", headers=headers
    ).status_code == 422
    assert client.delete(f"/api/v1/plans/{plan_date}", headers=headers).status_code == 204
    assert client.delete(f"/api/v1/plans/{plan_date}", headers=headers).status_code == 404


def test_attempt_history_is_private_and_invalid_problem_is_not_found(
    client, make_user, make_problem, auth_headers
):
    first = make_user(email="first@example.com")
    second = make_user(email="second@example.com")
    problem = make_problem()
    first_headers = auth_headers(first)
    second_headers = auth_headers(second)

    assert client.post(
        "/api/v1/attempts",
        json={"problem_id": problem.problem_id, "outcome": "solved"},
        headers=first_headers,
    ).status_code == 201
    assert client.get("/api/v1/attempts", headers=first_headers).json()["total"] == 1
    assert client.get("/api/v1/attempts", headers=second_headers).json()["total"] == 0
    assert client.get(
        "/api/v1/attempts?problem_id=-1", headers=first_headers
    ).status_code == 422
    assert client.post(
        "/api/v1/attempts",
        json={"problem_id": 98765, "outcome": "solved"},
        headers=first_headers,
    ).status_code == 404

