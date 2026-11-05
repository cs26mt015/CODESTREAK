import httpx


def test_language_catalog_is_proxied_and_cached(client, monkeypatch):
    from app.api import judge

    calls = []

    def fake_get(url, headers, timeout):
        calls.append((url, headers, timeout))
        return httpx.Response(
            200,
            json=[{"id": 71, "name": "Python"}],
            request=httpx.Request("GET", url),
        )

    judge._supported_languages.cache_clear()
    monkeypatch.setattr(judge.httpx, "get", fake_get)
    assert client.get("/api/v1/languages").json() == [{"id": 71, "name": "Python"}]
    assert client.get("/api/v1/languages").status_code == 200
    assert len(calls) == 1
    assert calls[0][1]["X-Auth-Token"]
    judge._supported_languages.cache_clear()

    monkeypatch.setattr(
        judge.httpx,
        "get",
        lambda *args, **kwargs: (_ for _ in ()).throw(httpx.ConnectError("offline")),
    )
    assert client.get("/api/v1/languages").status_code == 503
    judge._supported_languages.cache_clear()


def test_judge_run_auth_validation_and_upstream_errors(client, make_user, make_problem, auth_headers, monkeypatch):
    from app.api import judge

    execute = judge._execute
    learner = make_user()
    admin = make_user(role="admin")
    problem = make_problem()
    request = {"language_id": 71, "source_code": "print(1)", "stdin": ""}
    assert client.post(f"/api/v1/problems/{problem.problem_id}/run", json=request).status_code == 401
    assert client.post(
        f"/api/v1/problems/{problem.problem_id}/run", json=request, headers=auth_headers(admin)
    ).status_code == 403
    assert client.post(
        f"/api/v1/problems/{problem.problem_id}/run",
        json={**request, "language_id": 0},
        headers=auth_headers(learner),
    ).status_code == 422

    monkeypatch.setattr(judge, "_supported_languages", lambda: ({"id": 71, "name": "Python"},))
    monkeypatch.setattr(judge, "_execute", lambda source_code, language_id, stdin: {"stdout": "1\n"})
    ok = client.post(
        f"/api/v1/problems/{problem.problem_id}/run", json=request, headers=auth_headers(learner)
    )
    assert ok.status_code == 200
    assert ok.json()["stdout"] == "1\n"
    unsupported = client.post(
        f"/api/v1/problems/{problem.problem_id}/run",
        json={**request, "language_id": 72},
        headers=auth_headers(learner),
    )
    assert unsupported.status_code == 422
    assert client.post(
        "/api/v1/problems/99999/run", json=request, headers=auth_headers(learner)
    ).status_code == 404

    monkeypatch.setattr(judge, "_execute", execute)
    monkeypatch.setattr(
        judge.httpx,
        "post",
        lambda url, **kwargs: httpx.Response(
            200,
            json={"stdout": "5\n"},
            request=httpx.Request("POST", url),
        ),
    )
    proxied = client.post(
        f"/api/v1/problems/{problem.problem_id}/run", json=request, headers=auth_headers(learner)
    )
    assert proxied.status_code == 200
    assert proxied.json()["stdout"] == "5\n"

    monkeypatch.setattr(
        judge.httpx,
        "post",
        lambda *args, **kwargs: (_ for _ in ()).throw(httpx.ConnectError("offline")),
    )
    assert client.post(
        f"/api/v1/problems/{problem.problem_id}/run", json=request, headers=auth_headers(learner)
    ).status_code == 503


def test_judge_submission_acceptance_wrong_answer_and_empty_cases(
    client, make_user, make_problem, auth_headers, monkeypatch
):
    from app.api import judge

    learner = make_user()
    accepted_problem = make_problem(
        title="Accepted", hidden_test_cases=[{"input": "1", "output": "1"}, {"input": "2", "output": "2"}]
    )
    empty_problem = make_problem(title="No cases", hidden_test_cases=[])
    monkeypatch.setattr(judge, "_supported_languages", lambda: ({"id": 71},))
    monkeypatch.setattr(
        judge,
        "_execute",
        lambda source_code, language_id, stdin: {
            "status": {"description": "Accepted"},
            "stdout": f"{stdin}\n",
            "time": "0.01",
            "memory": 1024,
        },
    )
    request = {"language_id": 71, "source_code": "print(input())"}
    headers = auth_headers(learner)
    accepted = client.post(
        f"/api/v1/problems/{accepted_problem.problem_id}/submit", json=request, headers=headers
    )
    assert accepted.status_code == 200
    assert accepted.json()["verdict"] == "Accepted"
    assert accepted.json()["passed"] == accepted.json()["total"] == 2
    assert accepted.json()["attempt_id"]
    assert client.get(
        f"/api/v1/problems/{accepted_problem.problem_id}/status", headers=headers
    ).json()["status"] == "solved"

    empty = client.post(
        f"/api/v1/problems/{empty_problem.problem_id}/submit", json=request, headers=headers
    )
    assert empty.status_code == 409

    monkeypatch.setattr(
        judge,
        "_execute",
        lambda source_code, language_id, stdin: {"status": {"description": "Accepted"}, "stdout": "wrong"},
    )
    wrong = client.post(
        f"/api/v1/problems/{accepted_problem.problem_id}/submit", json=request, headers=headers
    )
    assert wrong.status_code == 200
    assert wrong.json()["verdict"] == "Wrong Answer"
    assert wrong.json()["failed_case"] == 1

    timed_out_problem = make_problem(title="Runner Error")
    monkeypatch.setattr(
        judge,
        "_execute",
        lambda source_code, language_id, stdin: {
            "status": {"description": "Compilation Error"},
            "stdout": None,
            "memory": None,
        },
    )
    failed = client.post(
        f"/api/v1/problems/{timed_out_problem.problem_id}/submit", json=request, headers=headers
    )
    assert failed.status_code == 200
    assert failed.json()["verdict"] == "Compilation Error"
    assert failed.json()["passed"] == 0


def test_hint_records_unconfigured_requests_and_enforces_rate_limit(
    client, db_session, make_user, make_problem, auth_headers, monkeypatch
):
    from datetime import UTC, datetime

    from app.api import hints
    from app.models.ai_interaction_metadata import AIInteractionMetadata

    learner = make_user()
    admin = make_user(role="admin")
    problem = make_problem()
    headers = auth_headers(learner)
    monkeypatch.setattr(hints.settings, "hint_provider", "disabled")
    payload = {"level": 2, "question": "What should I try?"}

    assert client.post(
        f"/api/v1/problems/{problem.problem_id}/hints", json=payload, headers=auth_headers(admin)
    ).status_code == 403
    assert client.post(
        f"/api/v1/problems/{problem.problem_id}/hints", json=payload
    ).status_code == 401
    unavailable = client.post(
        f"/api/v1/problems/{problem.problem_id}/hints", json=payload, headers=headers
    )
    assert unavailable.status_code == 503
    interaction = db_session.query(AIInteractionMetadata).one()
    assert interaction.request_status == "provider_unconfigured"
    assert interaction.feature == "hint_level_2"

    monkeypatch.setattr(hints.settings, "hint_provider", "configured-provider")
    configured = client.post(
        f"/api/v1/problems/{problem.problem_id}/hints", json=payload, headers=headers
    )
    assert configured.status_code == 503
    assert db_session.query(AIInteractionMetadata).count() == 2
    assert db_session.query(AIInteractionMetadata).order_by(AIInteractionMetadata.interaction_id.desc()).first().request_status == "provider_unavailable"

    now = datetime.now(UTC).replace(tzinfo=None)
    db_session.add_all(
        [
            AIInteractionMetadata(
                user_id=learner.user_id,
                problem_id=problem.problem_id,
                feature="hint_level_1",
                model="unconfigured",
                input_tokens=0,
                output_tokens=0,
                request_status="provider_unconfigured",
                latency_ms=0,
                created_at=now,
            )
            for _ in range(4)
        ]
    )
    db_session.commit()
    limited = client.post(
        f"/api/v1/problems/{problem.problem_id}/hints", json=payload, headers=headers
    )
    assert limited.status_code == 429
    assert client.post("/api/v1/problems/99999/hints", json=payload, headers=headers).status_code == 404
