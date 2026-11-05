def problem_payload(**changes):
    payload = {
        "title": "Created Problem",
        "difficulty": "Easy",
        "statement": "Add two values.",
        "constraints": "Small integers.",
        "sample_input": "2 3",
        "sample_output": "5",
        "editorial_notes": "Add the values.",
        "reference_solution": "int main() {}",
        "hidden_test_cases": [{"input": "2 3", "output": "5"}],
        "tags": ["Math"],
    }
    payload.update(changes)
    return payload


def test_public_problem_browsing_and_private_fields(client, make_problem):
    published = make_problem(title="Published Sum", tags=["Math"])
    make_problem(title="Draft Secret", published=False, tags=["Math"])

    page = client.get("/api/v1/problems?limit=1")
    assert page.status_code == 200
    assert page.json()["total"] == 1
    assert page.json()["items"][0]["title"] == "Published Sum"
    assert "hidden_test_cases" not in page.json()["items"][0]
    assert "editorial_notes" not in page.json()["items"][0]

    filtered = client.get("/api/v1/problems?q=sum&difficulty=Easy&tag=Math")
    assert filtered.json()["total"] == 1
    assert client.get(f"/api/v1/problems/{published.problem_id}").status_code == 200
    assert client.get("/api/v1/problems/99999").status_code == 404
    assert [item["name"] for item in client.get("/api/v1/tags").json()] == ["Math"]
    assert client.get("/api/v1/problems?offset=-1").status_code == 422


def test_status_filter_requires_learner_and_filters_user_problems(client, make_user, make_problem, auth_headers, db_session):
    from app.models.user_problem_status import UserProblemStatus

    first = make_problem(title="First")
    make_problem(title="Second")
    learner = make_user()
    assert client.get("/api/v1/problems?status=solved").status_code == 401
    admin = make_user(role="admin")
    assert client.get(
        "/api/v1/problems?status=solved", headers=auth_headers(admin)
    ).status_code == 403
    db_session.add(UserProblemStatus(user_id=learner.user_id, problem_id=first.problem_id, status="solved"))
    db_session.commit()
    result = client.get("/api/v1/problems?status=solved", headers=auth_headers(learner))
    assert [item["problem_id"] for item in result.json()["items"]] == [first.problem_id]
    assert client.get("/api/v1/problems?status=unknown", headers=auth_headers(learner)).status_code == 422


def test_admin_problem_lifecycle_and_access_control(
    client, make_user, make_problem, auth_headers, db_session
):
    from app.models.ai_interaction_metadata import AIInteractionMetadata

    learner = make_user()
    admin = make_user(role="admin")
    assert client.get("/api/v1/admin/problems").status_code == 401
    assert client.get("/api/v1/admin/problems", headers=auth_headers(learner)).status_code == 403
    headers = auth_headers(admin)

    created = client.post("/api/v1/admin/problems", json=problem_payload(), headers=headers)
    assert created.status_code == 201
    data = created.json()
    problem_id = data["problem_id"]
    assert data["is_published"] is False
    assert data["hidden_test_cases"] == [{"input": "2 3", "output": "5"}]
    assert client.get(f"/api/v1/problems/{problem_id}").status_code == 404

    listed = client.get("/api/v1/admin/problems?limit=1", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert client.get(f"/api/v1/admin/problems/{problem_id}", headers=headers).status_code == 200
    assert client.get("/api/v1/admin/problems/99999", headers=headers).status_code == 404

    updated = client.patch(
        f"/api/v1/admin/problems/{problem_id}",
        json={"title": "  Renamed Problem  ", "tags": ["Math", "Arrays"]},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Renamed Problem"
    assert {tag["name"] for tag in updated.json()["tags"]} == {"Math", "Arrays"}
    assert client.patch(f"/api/v1/admin/problems/{problem_id}", json={}, headers=headers).status_code == 422

    published = client.put(
        f"/api/v1/admin/problems/{problem_id}/publication",
        json={"is_published": True},
        headers=headers,
    )
    assert published.status_code == 200
    assert client.get(f"/api/v1/problems/{problem_id}").status_code == 200
    db_session.add(
        AIInteractionMetadata(
            user_id=admin.user_id,
            problem_id=problem_id,
            feature="hint",
            model="test",
            input_tokens=0,
            output_tokens=0,
            request_status="test",
            latency_ms=0,
        )
    )
    db_session.commit()
    assert client.delete(f"/api/v1/admin/problems/{problem_id}", headers=headers).status_code == 204
    assert db_session.query(AIInteractionMetadata).count() == 0

    draft = make_problem(title="Delete Draft", published=False)
    assert client.delete(f"/api/v1/admin/problems/{draft.problem_id}", headers=headers).status_code == 204
    assert client.delete(f"/api/v1/admin/problems/{draft.problem_id}", headers=headers).status_code == 404


def test_problem_delete_is_blocked_by_learner_history(client, make_user, make_problem, auth_headers, db_session):
    from app.models.practice_attempt import PracticeAttempt

    admin = make_user(role="admin")
    learner = make_user()
    problem = make_problem()
    db_session.add(PracticeAttempt(user_id=learner.user_id, problem_id=problem.problem_id, language="cpp", verdict="attempted"))
    db_session.commit()
    response = client.delete(
        f"/api/v1/admin/problems/{problem.problem_id}", headers=auth_headers(admin)
    )
    assert response.status_code == 409
    assert response.json()["detail"].startswith("Problem has learner history")
