"""Seed local demo accounts and starter problems after database migrations."""

import os

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Problem, Tag, User
from app.seed_catalog import ADDITIONAL_PROBLEMS


STARTER_PROBLEMS = (
    {
        "title": "Sum Two Integers",
        "difficulty": "Easy",
        "statement": (
            "Read two integers from standard input and print their sum. "
            "The integers are separated by whitespace."
        ),
        "constraints": "-1,000,000,000 <= each integer <= 1,000,000,000",
        "sample_input": "7 5",
        "sample_output": "12",
        "editorial_notes": "Read both values as integers and print their sum.",
        "reference_solution": "#include <iostream>\nint main() { long long a, b; std::cin >> a >> b; std::cout << a + b << std::endl; }",
        "hidden_test_cases": [
            {"input": "7 5\n", "output": "12\n"},
            {"input": "-8 3\n", "output": "-5\n"},
            {"input": "1000000000 1000000000\n", "output": "2000000000\n"},
        ],
        "tags": ["Math", "Input and Output"],
    },
    {
        "title": "Count Vowels",
        "difficulty": "Easy",
        "statement": (
            "Read one line of text and print the number of English vowels "
            "(a, e, i, o, u) it contains, ignoring letter case."
        ),
        "constraints": "The line contains at most 10,000 printable characters.",
        "sample_input": "CodeStreak",
        "sample_output": "3",
        "editorial_notes": "Convert each character to lowercase and count vowels.",
        "reference_solution": "#include <iostream>\n#include <string>\n#include <cctype>\nint main() { std::string s; std::getline(std::cin, s); int n = 0; for (char c : s) { c = std::tolower(static_cast<unsigned char>(c)); if (c=='a'||c=='e'||c=='i'||c=='o'||c=='u') ++n; } std::cout << n << std::endl; }",
        "hidden_test_cases": [
            {"input": "CodeStreak\n", "output": "3\n"},
            {"input": "rhythm\n", "output": "0\n"},
            {"input": "AEIOU\n", "output": "5\n"},
        ],
        "tags": ["Strings", "Counting"],
    },
    {
        "title": "Find the Largest Number",
        "difficulty": "Easy",
        "statement": (
            "Read an integer n followed by n integers. Print the largest value. "
            "The input values are separated by whitespace."
        ),
        "constraints": "1 <= n <= 100,000; -1,000,000,000 <= each value <= 1,000,000,000",
        "sample_input": "5\n-3 8 2 8 1",
        "sample_output": "8",
        "editorial_notes": "Track the maximum while reading the values.",
        "reference_solution": "#include <iostream>\n#include <algorithm>\nint main() { int n; std::cin >> n; long long x, best; std::cin >> best; for (int i=1; i<n; ++i) { std::cin >> x; best = std::max(best, x); } std::cout << best << std::endl; }",
        "hidden_test_cases": [
            {"input": "5\n-3 8 2 8 1\n", "output": "8\n"},
            {"input": "1\n-42\n", "output": "-42\n"},
            {"input": "4\n-9 -2 -17 -4\n", "output": "-2\n"},
        ],
        "tags": ["Arrays", "Iteration"],
    },
)


def _environment_value(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    if not value:
        raise ValueError(f"{name} cannot be empty when demo seeding is enabled")
    return value


def _ensure_user(db, *, name: str, email: str, password: str, role: str) -> None:
    email = email.lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        legacy_emails = {
            "learner@example.com": "learner@codestreak.local",
            "admin@example.com": "admin@codestreak.local",
        }
        legacy_email = legacy_emails.get(email)
        if legacy_email:
            user = db.scalar(select(User).where(User.email == legacy_email))
            if user is not None and user.role == role:
                user.email = email
    if user is not None:
        if user.role != role:
            raise ValueError(
                f"Seed account {email} already exists with role {user.role!r}; "
                f"use another configured email or correct that account's role."
            )
        return

    if len(password) < 12 or len(password) > 128:
        raise ValueError(f"The configured {role} demo password must be 12 to 128 characters")
    db.add(
        User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=role,
            timezone="Asia/Kolkata",
            consent_status="accepted",
        )
    )
    db.flush()


def _ensure_problem(db, values: dict) -> None:
    problem = db.scalar(select(Problem).where(Problem.title == values["title"]))
    if problem is not None:
        return

    tags = []
    for name in values["tags"]:
        tag = db.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)

    problem = Problem(
        title=values["title"],
        difficulty=values["difficulty"],
        statement=values["statement"],
        constraints=values["constraints"],
        sample_input=values["sample_input"],
        sample_output=values["sample_output"],
        editorial_notes=values["editorial_notes"],
        reference_solution=values["reference_solution"],
        hidden_test_cases=values["hidden_test_cases"],
        is_published=True,
        tags=tags,
    )
    db.add(problem)


def seed_demo_data() -> None:
    if os.getenv("SEED_DEMO_DATA", "true").strip().lower() not in {"1", "true", "yes", "on"}:
        print("Demo data seeding is disabled.", flush=True)
        return
    if settings.app_env.lower() in {"prod", "production"}:
        raise ValueError("Set SEED_DEMO_DATA=false in production to disable demo account seeding")

    accounts = (
        {
            "name": _environment_value("SEED_LEARNER_NAME", "Demo Learner"),
            "email": _environment_value("SEED_LEARNER_EMAIL", "learner@example.com"),
            "password": _environment_value("SEED_LEARNER_PASSWORD", "LearnCode!2026Demo"),
            "role": "learner",
        },
        {
            "name": _environment_value("SEED_ADMIN_NAME", "Demo Admin"),
            "email": _environment_value("SEED_ADMIN_EMAIL", "admin@example.com"),
            "password": _environment_value("SEED_ADMIN_PASSWORD", "AdminCode!2026Demo"),
            "role": "admin",
        },
    )

    with SessionLocal.begin() as db:
        for account in accounts:
            _ensure_user(db, **account)
        for problem in (*STARTER_PROBLEMS, *ADDITIONAL_PROBLEMS):
            _ensure_problem(db, problem)

    print("Demo learner, admin, and starter problems are ready.", flush=True)


if __name__ == "__main__":
    seed_demo_data()
