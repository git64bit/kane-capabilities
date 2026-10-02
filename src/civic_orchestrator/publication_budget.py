from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PublicationBudgetPolicy:
    max_publications: int
    max_publication_bytes: int

    def __post_init__(self) -> None:
        for name, value in (
            ("max_publications", self.max_publications),
            ("max_publication_bytes", self.max_publication_bytes),
        ):
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                raise ValueError(f"{name} must be a non-negative integer")


@dataclass(frozen=True)
class PublicationBudgetUsage:
    completed_publications: int
    completed_bytes: int
    held_publications: int
    held_bytes: int

    @property
    def charged_publications(self) -> int:
        return self.completed_publications + self.held_publications

    @property
    def charged_bytes(self) -> int:
        return self.completed_bytes + self.held_bytes


class PublicationBudgetExceeded(ValueError):
    def __init__(
        self,
        *,
        usage: PublicationBudgetUsage,
        policy: PublicationBudgetPolicy,
        requested_bytes: int,
        reason: str,
    ) -> None:
        super().__init__(reason)
        self.usage = usage
        self.policy = policy
        self.requested_bytes = requested_bytes
