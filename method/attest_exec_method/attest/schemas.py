"""Data contracts shared across the four pipeline stages.

These dataclasses are the *spine* of the system: Stage 1 produces a
:class:`Contract` (the policy — what to feed, how to call, what to observe);
Stages 2-4 obey it so that snippets A and B are always exercised and observed
identically. We keep them as plain dataclasses with explicit (de)serialization
so artifacts on disk are stable and reviewable.
"""

from __future__ import annotations

import enum
from dataclasses import asdict, dataclass, field
from typing import Any

# --------------------------------------------------------------------------- #
# Inputs to the pipeline
# --------------------------------------------------------------------------- #


@dataclass
class Snippet:
    """One code fragment under comparison."""

    id: str
    code: str
    language: str  # "java" | "cpp" | "c"

    def short(self, n: int = 4000) -> str:
        return self.code if len(self.code) <= n else self.code[:n] + "\n/* ...truncated... */"


@dataclass
class Pair:
    """A pair of snippets plus optional ground-truth label (for evaluation)."""

    pair_id: str
    a: Snippet
    b: Snippet
    label: int | None = None  # 1 = clone, 0 = non-clone, None = unknown
    meta: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Stage 1 output: the unified contract
# --------------------------------------------------------------------------- #


class ObserveMode(str, enum.Enum):
    RETURN = "return"        # observe the method's return value
    ARTIFACT = "artifact"    # observe an external effect (file bytes, stdout, ...)
    STATE = "state"          # observe a projected object/state via accessors
    COMPOSITE = "composite"  # observe several parts together


@dataclass
class ObserveSpec:
    """How to turn a snippet's execution into one comparable observation."""

    mode: ObserveMode = ObserveMode.RETURN
    # artifact mode:
    artifact_kind: str | None = None     # file_bytes | file_text | dir_listing | stdout
    path_role: str | None = None         # logical role, e.g. "dest"
    charset: str = "UTF-8"
    # state mode: whitelisted accessors to project an opaque return object
    accessors: list[str] = field(default_factory=list)
    # composite mode: named sub-observations
    parts: list[dict[str, Any]] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        d: dict[str, Any] = {"mode": self.mode.value}
        if self.mode == ObserveMode.ARTIFACT:
            d["artifact"] = {
                "kind": self.artifact_kind,
                "path_role": self.path_role,
                "charset": self.charset,
            }
        elif self.mode == ObserveMode.STATE:
            d["accessors"] = self.accessors
        elif self.mode == ObserveMode.COMPOSITE:
            d["parts"] = self.parts
        return d

    @staticmethod
    def from_json(d: dict[str, Any]) -> "ObserveSpec":
        mode = ObserveMode(d.get("mode", "return"))
        art = d.get("artifact", {}) or {}
        return ObserveSpec(
            mode=mode,
            artifact_kind=art.get("kind"),
            path_role=art.get("path_role"),
            charset=art.get("charset", "UTF-8"),
            accessors=list(d.get("accessors", []) or []),
            parts=list(d.get("parts", []) or []),
        )


@dataclass
class Contract:
    """Stage-1 result: functional labels + the unified test contract."""

    label_a: str
    label_b: str
    same_function: bool
    # A human/LLM-readable description of the unified input/output interface the
    # pair is exercised against, plus the machine-readable observe spec.
    unified_signature: str
    observe: ObserveSpec
    # How the unified input cases are shaped: a list of {name, type, desc} that
    # tells Stage 3 what fields each case's `args` must contain.
    input_fields: list[dict[str, Any]] = field(default_factory=list)
    # The VALID input domain / preconditions the snippets assume (value ranges,
    # size limits, format guarantees). Stage 3 keeps the bulk of its inputs
    # inside this domain so that out-of-domain edge cases (which the code was
    # never meant to handle) don't manufacture spurious behavioral divergences.
    input_domain: str = ""
    rationale: str = ""

    def to_json(self) -> dict[str, Any]:
        return {
            "label_a": self.label_a,
            "label_b": self.label_b,
            "same_function": self.same_function,
            "unified_signature": self.unified_signature,
            "observe": self.observe.to_json(),
            "input_fields": self.input_fields,
            "input_domain": self.input_domain,
            "rationale": self.rationale,
        }

    @staticmethod
    def from_json(d: dict[str, Any]) -> "Contract":
        return Contract(
            label_a=str(d.get("label_a", "")),
            label_b=str(d.get("label_b", "")),
            same_function=bool(d.get("same_function", False)),
            unified_signature=str(d.get("unified_signature", "")),
            observe=ObserveSpec.from_json(d.get("observe", {}) or {}),
            input_fields=list(d.get("input_fields", []) or []),
            input_domain=str(d.get("input_domain", "")),
            rationale=str(d.get("rationale", "")),
        )


# --------------------------------------------------------------------------- #
# Stage 2 output: a runnable harness for one side
# --------------------------------------------------------------------------- #


@dataclass
class HarnessHoles:
    """The LLM-filled template holes for one snippet (language-specific keys)."""

    holes: dict[str, str]
    notes: str = ""


@dataclass
class BuiltHarness:
    """A compiled (or failed) harness for one side, with provenance."""

    side: str                 # "a" | "b"
    source: str               # full filled harness source
    compiled: bool
    workdir: str
    repair_attempts: int = 0
    diagnostics: str = ""     # last compiler/runtime diagnostics


# --------------------------------------------------------------------------- #
# Stage 3 output: the shared input batch
# --------------------------------------------------------------------------- #


@dataclass
class InputCase:
    id: str
    kind: str                 # normal | empty | large | nonascii | boundary | ...
    args: dict[str, Any]


@dataclass
class InputBatch:
    cases: list[InputCase]

    def to_inputs_json(self, observe: ObserveSpec) -> dict[str, Any]:
        return {
            "protocol": 1,
            "observe": observe.to_json(),
            "cases": [{"id": c.id, "kind": c.kind, "args": c.args} for c in self.cases],
        }


# --------------------------------------------------------------------------- #
# Stage 4 / final outcome
# --------------------------------------------------------------------------- #


class Verdict(str, enum.Enum):
    CLONE = "clone"
    NON_CLONE = "non_clone"
    UNDECIDED_EXEC = "undecided_exec"   # could not construct runnable evidence
    ERROR = "error"                     # pipeline-internal failure


class SideState(str, enum.Enum):
    OK = "ok"                 # compiled, ran, produced output
    EXEC_FAIL = "exec_fail"   # could not be made to run after repair budget


@dataclass
class CaseComparison:
    """Per-input comparison of A vs B observations."""

    id: str
    match: bool
    reason: str = ""          # rule that matched/mismatched, or LLM explanation
    a_repr: Any = None
    b_repr: Any = None


@dataclass
class PairOutcome:
    """The full result for one pair, including all evidence for the paper."""

    pair_id: str
    verdict: Verdict
    pass_rate: float = 0.0
    n_cases: int = 0
    n_match: int = 0
    side_a_state: SideState = SideState.OK
    side_b_state: SideState = SideState.OK
    reason: str = ""
    contract: dict[str, Any] | None = None
    comparisons: list[CaseComparison] = field(default_factory=list)
    repair_attempts_a: int = 0
    repair_attempts_b: int = 0
    stage_reached: int = 0
    extra: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        d = asdict(self)
        d["verdict"] = self.verdict.value
        d["side_a_state"] = self.side_a_state.value
        d["side_b_state"] = self.side_b_state.value
        return d

    @property
    def is_clone(self) -> bool:
        return self.verdict == Verdict.CLONE
