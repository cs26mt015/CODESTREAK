from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: EmailStr
    role: str
    timezone: str
    consent_status: str
    created_at: datetime
    updated_at: datetime


class RegisterRequest(InputModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    timezone: str = Field(default="UTC", min_length=1, max_length=100)
    consent_status: Literal["accepted"]

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value


class LoginRequest(InputModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserUpdate(InputModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    timezone: str | None = Field(default=None, min_length=1, max_length=100)

    @model_validator(mode="after")
    def require_at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Profile fields cannot be null")
        return self

    @field_validator("name")
    @classmethod
    def trim_updated_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value


class AuthResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserRead


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tag_id: int
    name: str


class ProblemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    problem_id: int
    title: str
    difficulty: str
    statement: str
    constraints: str | None
    sample_input: str | None
    sample_output: str | None
    is_published: bool
    tags: list[TagRead]
    created_at: datetime
    updated_at: datetime


class ProblemAdmin(ProblemPublic):
    editorial_notes: str | None
    reference_solution: str | None


class ProblemWrite(InputModel):
    title: str = Field(min_length=1, max_length=255)
    difficulty: str = Field(min_length=1, max_length=100)
    statement: str = Field(min_length=1, max_length=50000)
    constraints: str | None = Field(default=None, max_length=30000)
    sample_input: str | None = Field(default=None, max_length=30000)
    sample_output: str | None = Field(default=None, max_length=30000)
    editorial_notes: str | None = Field(default=None, max_length=30000)
    reference_solution: str | None = Field(default=None, max_length=50000)
    tags: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("title", "difficulty")
    @classmethod
    def trim_problem_labels(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be blank")
        return value

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        cleaned = [tag.strip() for tag in tags]
        if any(not tag or len(tag) > 255 for tag in cleaned):
            raise ValueError("Tags must be non-empty and at most 255 characters")
        return list(dict.fromkeys(cleaned))


class ProblemPatch(InputModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    difficulty: str | None = Field(default=None, min_length=1, max_length=100)
    statement: str | None = Field(default=None, min_length=1, max_length=50000)
    constraints: str | None = Field(default=None, max_length=30000)
    sample_input: str | None = Field(default=None, max_length=30000)
    sample_output: str | None = Field(default=None, max_length=30000)
    editorial_notes: str | None = Field(default=None, max_length=30000)
    reference_solution: str | None = Field(default=None, max_length=50000)
    tags: list[str] | None = Field(default=None, max_length=50)

    @field_validator("title", "difficulty")
    @classmethod
    def trim_patch_labels(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be blank")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")
        for required_field in ("title", "difficulty", "statement"):
            if required_field in self.model_fields_set and getattr(self, required_field) is None:
                raise ValueError(f"{required_field} cannot be null")
        return self

    @field_validator("tags")
    @classmethod
    def normalize_patch_tags(cls, tags: list[str] | None) -> list[str] | None:
        if tags is None:
            return None
        cleaned = [tag.strip() for tag in tags]
        if any(not tag or len(tag) > 255 for tag in cleaned):
            raise ValueError("Tags must be non-empty and at most 255 characters")
        return list(dict.fromkeys(cleaned))


class ProblemPage(BaseModel):
    items: list[ProblemPublic]
    total: int
    offset: int
    limit: int


class AdminProblemPage(BaseModel):
    items: list[ProblemAdmin]
    total: int
    offset: int
    limit: int


class AttemptCreate(InputModel):
    problem_id: int = Field(gt=0)
    outcome: Literal["attempted", "solved"]
    language: str = Field(default="self_reported", min_length=1, max_length=100)


class AttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempt_id: int
    user_id: int
    problem_id: int
    language: str
    verdict: str
    attempted_at: datetime
    execution_time: float | None
    memory_used: int | None


class AttemptPage(BaseModel):
    items: list[AttemptRead]
    total: int
    offset: int
    limit: int


class ProblemStatusUpdate(InputModel):
    status: Literal["not_started", "attempted", "solved"]


class ProblemStatusRead(BaseModel):
    problem_id: int
    status: str
    first_attempt_at: datetime | None
    solved_at: datetime | None
    updated_at: datetime


class PracticePlanUpdate(InputModel):
    daily_goal: int = Field(ge=1, le=1000)


class PracticePlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan_id: int
    plan_date: date
    daily_goal: int
    completed_count: int


class DailyActivityRead(BaseModel):
    local_date: date
    problems_attempted: int
    problems_solved: int


class StreakSummary(BaseModel):
    current_streak: int
    longest_streak: int
    timezone: str


class BreakdownItem(BaseModel):
    name: str
    solved: int


class ProgressSummary(BaseModel):
    total_solved: int
    current_streak: int
    longest_streak: int
    daily_goal: int
    completed_today: int
    by_topic: list[BreakdownItem]
    by_difficulty: list[BreakdownItem]


class Recommendation(BaseModel):
    problem: ProblemPublic | None
    message: str


class HintRequest(InputModel):
    level: int = Field(ge=1, le=3)
    question: str | None = Field(default=None, max_length=1000)


class HintResponse(BaseModel):
    problem_id: int
    level: int
    hint: str
    generated_by_ai: Literal[True] = True
    disclaimer: str


class PublicationUpdate(InputModel):
    is_published: bool
