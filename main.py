"""Temporal Rare-Disease Discovery Engine (TRDDE).

Version 1.1.0 — GitHub development edition

TRDDE is an educational research-pattern prototype. Its built-in dataset is
entirely synthetic. It is not a diagnostic tool and makes no clinical claims.

Runtime dependencies: Python standard library only.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PROJECT_NAME = "Temporal Rare-Disease Discovery Engine"
PROJECT_SHORT_NAME = "TRDDE"
VERSION = "1.1.0"


@dataclass(frozen=True, slots=True)
class Feature:
    """A fictional demonstration feature and its broad system label."""

    feature_id: str
    name: str
    system: str


@dataclass(frozen=True, slots=True)
class Observation:
    """An illustrative feature observation with an onset-age interval."""

    feature_id: str
    onset_start_years: float
    onset_end_years: float


@dataclass(frozen=True, slots=True)
class Profile:
    """A fictional profile containing a collection of observations."""

    profile_id: str
    name: str
    observations: tuple[Observation, ...]


@dataclass(frozen=True, slots=True)
class IntervalComparison:
    feature_id: str
    interval_a: tuple[float, float]
    interval_b: tuple[float, float]
    relation: str


@dataclass(frozen=True, slots=True)
class ProfileComparison:
    profile_a: Profile
    profile_b: Profile
    shared_feature_ids: tuple[str, ...]
    shared_systems: tuple[str, ...]
    phenotype_similarity: float
    temporal_compatibility: float
    combined_score: float
    interval_details: tuple[IntervalComparison, ...]


@dataclass(frozen=True, slots=True)
class Hypothesis:
    hypothesis_id: str
    profile_names: tuple[str, str]
    shared_features: tuple[str, ...]
    shared_systems: tuple[str, ...]
    phenotype_similarity: float
    temporal_compatibility: float
    ranking_score: float
    research_question: str
    suggested_next_step: str
    status: str = "Unvalidated research question"


# These identifiers are local demonstration IDs, not HPO identifiers.
FEATURES: dict[str, Feature] = {
    "SYN-001": Feature("SYN-001", "Motor coordination differences", "Neurological"),
    "SYN-002": Feature("SYN-002", "Feeding difficulties", "Gastrointestinal"),
    "SYN-003": Feature("SYN-003", "Muscle weakness", "Musculoskeletal"),
    "SYN-004": Feature("SYN-004", "Recurrent respiratory infections", "Respiratory"),
    "SYN-005": Feature("SYN-005", "Vision changes", "Ophthalmological"),
    "SYN-006": Feature("SYN-006", "Developmental differences", "Neurological"),
    "SYN-007": Feature("SYN-007", "Recurrent vomiting", "Gastrointestinal"),
    "SYN-008": Feature("SYN-008", "Poor growth", "Growth and nutrition"),
    "SYN-009": Feature("SYN-009", "Breathing difficulties", "Respiratory"),
    "SYN-010": Feature("SYN-010", "Exercise intolerance", "Cardiovascular"),
    "SYN-011": Feature("SYN-011", "Cardiac rhythm differences", "Cardiovascular"),
    "SYN-012": Feature("SYN-012", "Skin fragility", "Dermatological"),
    "SYN-013": Feature("SYN-013", "Recurrent infections", "Immunological"),
    "SYN-014": Feature("SYN-014", "Persistent fatigue", "General"),
    "SYN-015": Feature("SYN-015", "Hearing changes", "Auditory"),
    "SYN-016": Feature("SYN-016", "Joint stiffness", "Musculoskeletal"),
    "SYN-017": Feature("SYN-017", "Seizure-like episodes", "Neurological"),
    "SYN-018": Feature("SYN-018", "Digestive discomfort", "Gastrointestinal"),
    "SYN-019": Feature("SYN-019", "Unusual bruising", "Hematological"),
    "SYN-020": Feature("SYN-020", "Temperature regulation differences", "Autonomic"),
}


def _profile(profile_id: str, name: str, rows: tuple[tuple[str, float, float], ...]) -> Profile:
    return Profile(
        profile_id=profile_id,
        name=name,
        observations=tuple(Observation(*row) for row in rows),
    )


# Ten fictional profiles; all five observations per profile are synthetic.
PROFILES: tuple[Profile, ...] = (
    _profile("SYN-D01", "Synthetic Profile A", (
        ("SYN-001", 1, 3), ("SYN-002", 1, 2), ("SYN-003", 2, 5),
        ("SYN-004", 4, 7), ("SYN-016", 5, 8),
    )),
    _profile("SYN-D02", "Synthetic Profile B", (
        ("SYN-001", 2, 4), ("SYN-002", 1, 3), ("SYN-003", 3, 6),
        ("SYN-005", 5, 8), ("SYN-015", 6, 9),
    )),
    _profile("SYN-D03", "Synthetic Profile C", (
        ("SYN-006", 2, 5), ("SYN-007", 1, 3), ("SYN-008", 1, 4),
        ("SYN-002", 1, 2), ("SYN-018", 3, 5),
    )),
    _profile("SYN-D04", "Synthetic Profile D", (
        ("SYN-001", 1, 4), ("SYN-003", 2, 5), ("SYN-009", 4, 7),
        ("SYN-010", 5, 8), ("SYN-017", 3, 6),
    )),
    _profile("SYN-D05", "Synthetic Profile E", (
        ("SYN-002", 1, 3), ("SYN-007", 2, 4), ("SYN-012", 4, 7),
        ("SYN-013", 3, 6), ("SYN-019", 5, 8),
    )),
    _profile("SYN-D06", "Synthetic Profile F", (
        ("SYN-003", 2, 4), ("SYN-010", 3, 6), ("SYN-011", 5, 9),
        ("SYN-014", 1, 3), ("SYN-020", 4, 7),
    )),
    _profile("SYN-D07", "Synthetic Profile G", (
        ("SYN-006", 2, 4), ("SYN-005", 3, 6), ("SYN-001", 1, 3),
        ("SYN-008", 1, 4), ("SYN-015", 5, 8),
    )),
    _profile("SYN-D08", "Synthetic Profile H", (
        ("SYN-002", 1, 2), ("SYN-009", 2, 5), ("SYN-013", 2, 4),
        ("SYN-003", 4, 7), ("SYN-018", 3, 6),
    )),
    _profile("SYN-D09", "Synthetic Profile I", (
        ("SYN-004", 2, 5), ("SYN-013", 1, 4), ("SYN-019", 3, 6),
        ("SYN-014", 2, 5), ("SYN-020", 4, 8),
    )),
    _profile("SYN-D10", "Synthetic Profile J", (
        ("SYN-005", 2, 5), ("SYN-015", 1, 4), ("SYN-017", 3, 6),
        ("SYN-006", 2, 5), ("SYN-016", 5, 9),
    )),
)


SUGGESTED_NEXT_STEP = (
    "Verify phenotype definitions and chronology in independent datasets; "
    "assess missingness, ascertainment bias, confounding, and alternative explanations."
)


def observations_by_feature(profile: Profile) -> dict[str, Observation]:
    """Return a profile's observations indexed by feature ID."""
    return {observation.feature_id: observation for observation in profile.observations}


def validate_dataset(
    profiles: Iterable[Profile] = PROFILES,
    features: dict[str, Feature] = FEATURES,
) -> list[str]:
    """Return data-integrity errors; an empty list means the demo data pass checks."""
    profile_list = list(profiles)
    errors: list[str] = []
    profile_ids: set[str] = set()
    profile_names: set[str] = set()

    if not profile_list:
        errors.append("The dataset contains no profiles.")

    for profile in profile_list:
        if profile.profile_id in profile_ids:
            errors.append(f"Duplicate profile ID: {profile.profile_id}")
        profile_ids.add(profile.profile_id)

        if profile.name in profile_names:
            errors.append(f"Duplicate profile name: {profile.name}")
        profile_names.add(profile.name)

        if not profile.observations:
            errors.append(f"Profile has no observations: {profile.profile_id}")

        seen_features: set[str] = set()
        for observation in profile.observations:
            feature_id = observation.feature_id
            if feature_id not in features:
                errors.append(f"Unknown feature {feature_id} in {profile.profile_id}")
            if feature_id in seen_features:
                errors.append(f"Duplicate feature {feature_id} in {profile.profile_id}")
            seen_features.add(feature_id)

            start = observation.onset_start_years
            end = observation.onset_end_years
            if not (math.isfinite(start) and math.isfinite(end)):
                errors.append(f"Non-finite onset interval in {profile.profile_id}: {feature_id}")
            elif start < 0 or end < start:
                errors.append(f"Invalid onset interval in {profile.profile_id}: {feature_id}")

    return errors


def feature_weights(profiles: Iterable[Profile] = PROFILES) -> dict[str, float]:
    """Compute inverse-frequency weights from the supplied cohort.

    A feature appearing in fewer profiles receives a larger weight. This is
    a cohort-relative weighting rule, not a clinical measure of importance.
    """
    profile_list = list(profiles)
    counts: dict[str, int] = {}
    for profile in profile_list:
        for feature_id in observations_by_feature(profile):
            counts[feature_id] = counts.get(feature_id, 0) + 1

    total_profiles = len(profile_list)
    return {
        feature_id: 1.0 + math.log((total_profiles + 1) / (count + 1))
        for feature_id, count in counts.items()
    }


def weighted_jaccard(
    feature_ids_a: Iterable[str],
    feature_ids_b: Iterable[str],
    weights: dict[str, float],
) -> float:
    """Return weighted Jaccard similarity for two sets of feature IDs."""
    set_a, set_b = set(feature_ids_a), set(feature_ids_b)
    union = set_a | set_b
    if not union:
        return 0.0

    shared_weight = sum(weights.get(feature_id, 1.0) for feature_id in set_a & set_b)
    union_weight = sum(weights.get(feature_id, 1.0) for feature_id in union)
    return shared_weight / union_weight if union_weight else 0.0


def intervals_overlap(interval_a: tuple[float, float], interval_b: tuple[float, float]) -> bool:
    """Return whether two closed onset-age intervals share any values."""
    return not (interval_a[1] < interval_b[0] or interval_b[1] < interval_a[0])


def compare_profiles(
    profile_a: Profile,
    profile_b: Profile,
    weights: dict[str, float] | None = None,
) -> ProfileComparison:
    """Compare feature overlap and onset-interval compatibility for two profiles."""
    if weights is None:
        weights = feature_weights()

    map_a = observations_by_feature(profile_a)
    map_b = observations_by_feature(profile_b)
    shared_ids = tuple(sorted(set(map_a) & set(map_b)))
    shared_systems = tuple(sorted({FEATURES[item].system for item in shared_ids if item in FEATURES}))

    similarity = weighted_jaccard(map_a, map_b, weights)
    interval_details: list[IntervalComparison] = []
    compatible_count = 0

    for feature_id in shared_ids:
        observation_a = map_a[feature_id]
        observation_b = map_b[feature_id]
        interval_a = (observation_a.onset_start_years, observation_a.onset_end_years)
        interval_b = (observation_b.onset_start_years, observation_b.onset_end_years)
        overlaps = intervals_overlap(interval_a, interval_b)
        if overlaps:
            relation = "Intervals overlap"
            compatible_count += 1
        elif interval_a[1] < interval_b[0]:
            relation = "A interval is earlier"
        else:
            relation = "B interval is earlier"

        interval_details.append(
            IntervalComparison(feature_id, interval_a, interval_b, relation)
        )

    temporal = compatible_count / len(shared_ids) if shared_ids else 0.0
    combined = (0.70 * similarity) + (0.30 * temporal)

    return ProfileComparison(
        profile_a=profile_a,
        profile_b=profile_b,
        shared_feature_ids=shared_ids,
        shared_systems=shared_systems,
        phenotype_similarity=similarity,
        temporal_compatibility=temporal,
        combined_score=combined,
        interval_details=tuple(interval_details),
    )


def all_comparisons(profiles: Iterable[Profile] = PROFILES) -> list[ProfileComparison]:
    """Compare every unique pair in a cohort, ranked deterministically."""
    profile_list = list(profiles)
    weights = feature_weights(profile_list)
    results: list[ProfileComparison] = []

    for index, profile_a in enumerate(profile_list):
        for profile_b in profile_list[index + 1:]:
            results.append(compare_profiles(profile_a, profile_b, weights))

    return sorted(
        results,
        key=lambda item: (
            -item.combined_score,
            item.profile_a.profile_id,
            item.profile_b.profile_id,
        ),
    )


def discover_candidates(profiles: Iterable[Profile] = PROFILES) -> list[ProfileComparison]:
    """Keep pairs sharing at least two features across at least two systems."""
    return [
        comparison
        for comparison in all_comparisons(profiles)
        if len(comparison.shared_feature_ids) >= 2
        and len(comparison.shared_systems) >= 2
    ]


def build_research_question(comparison: ProfileComparison) -> str:
    """Convert a candidate overlap into a cautious, testable research question."""
    feature_names = [FEATURES[item].name for item in comparison.shared_feature_ids]
    joined_features = ", ".join(feature_names)
    return (
        "In independent real-world datasets, do "
        f"{joined_features} across {comparison.profile_a.name} and "
        f"{comparison.profile_b.name} form a reproducible multisystem pattern?"
    )


def generate_hypotheses(profiles: Iterable[Profile] = PROFILES) -> list[Hypothesis]:
    """Generate structured research-question dossiers from candidate pairs."""
    hypotheses: list[Hypothesis] = []
    for index, comparison in enumerate(discover_candidates(profiles), start=1):
        feature_names = tuple(FEATURES[item].name for item in comparison.shared_feature_ids)
        hypotheses.append(
            Hypothesis(
                hypothesis_id=f"TRDDE-H{index:03d}",
                profile_names=(comparison.profile_a.name, comparison.profile_b.name),
                shared_features=feature_names,
                shared_systems=comparison.shared_systems,
                phenotype_similarity=comparison.phenotype_similarity,
                temporal_compatibility=comparison.temporal_compatibility,
                ranking_score=comparison.combined_score,
                research_question=build_research_question(comparison),
                suggested_next_step=SUGGESTED_NEXT_STEP,
            )
        )
    return hypotheses


def build_research_report(profiles: Iterable[Profile] = PROFILES) -> dict:
    """Build a JSON-serializable report with methods, data, and limitations."""
    profile_list = list(profiles)
    weights = feature_weights(profile_list)
    candidates = discover_candidates(profile_list)
    hypothesis_list = generate_hypotheses(profile_list)
    observations = [observation for profile in profile_list for observation in profile.observations]

    return {
        "project": PROJECT_NAME,
        "short_name": PROJECT_SHORT_NAME,
        "version": VERSION,
        "dataset": {
            "status": "Synthetic demonstration data only",
            "profile_count": len(profile_list),
            "observation_count": len(observations),
            "feature_count": len({item.feature_id for item in observations}),
            "all_onset_intervals_present": all(
                item.onset_start_years is not None and item.onset_end_years is not None
                for item in observations
            ),
        },
        "methods": {
            "phenotype_similarity": (
                "Inverse-frequency weighted Jaccard similarity. Feature weights "
                "are calculated relative to the supplied synthetic cohort."
            ),
            "temporal_compatibility": (
                "Fraction of shared features whose illustrative onset-age intervals overlap."
            ),
            "combined_exploratory_score": "0.70 * phenotype_similarity + 0.30 * temporal_compatibility",
            "candidate_rule": "At least two shared features represented by at least two system labels.",
            "feature_weights": weights,
        },
        "profiles": [
            {
                "profile_id": profile.profile_id,
                "name": profile.name,
                "observations": [
                    {
                        "feature_id": item.feature_id,
                        "feature_name": FEATURES[item.feature_id].name,
                        "system": FEATURES[item.feature_id].system,
                        "onset_interval_years": [item.onset_start_years, item.onset_end_years],
                    }
                    for item in profile.observations
                ],
            }
            for profile in profile_list
        ],
        "candidate_pairs": [
            {
                "profile_a": item.profile_a.name,
                "profile_b": item.profile_b.name,
                "shared_features": [FEATURES[key].name for key in item.shared_feature_ids],
                "shared_systems": list(item.shared_systems),
                "phenotype_similarity": round(item.phenotype_similarity, 6),
                "temporal_compatibility": round(item.temporal_compatibility, 6),
                "combined_exploratory_score": round(item.combined_score, 6),
            }
            for item in candidates
        ],
        "hypotheses": [
            {
                "id": item.hypothesis_id,
                "research_question": item.research_question,
                "suggested_next_step": item.suggested_next_step,
                "status": item.status,
            }
            for item in hypothesis_list
        ],
        "limitations": [
            "Every profile and observation in this version is fictional and synthetic.",
            "Feature IDs beginning with SYN- are local demonstration identifiers, not HPO IDs.",
            "No real patient records, disease annotations, or biomedical database queries are included.",
            "A shared feature or overlapping interval does not establish causation, disease identity, or clinical significance.",
            "The ranking score is an exploratory ordering aid, not a probability or validated statistic.",
            "Independent biomedical validation and expert review would be required before research conclusions.",
        ],
        "safety_notice": (
            "TRDDE is not a diagnostic tool and is not intended for treatment, screening, "
            "or clinical decision-making."
        ),
    }


def export_report(destination: str | Path = "trdde_research_report.json") -> Path:
    """Write the current synthetic-cohort report as formatted JSON."""
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(build_research_report(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def print_heading(title: str) -> None:
    print("\n" + "=" * 68)
    print(title)
    print("=" * 68)


def pause() -> None:
    try:
        input("\nPress Enter to return to the menu...")
    except EOFError:
        print()


def ask_integer(prompt: str, minimum: int, maximum: int) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            if minimum <= value <= maximum:
                return value
        except (ValueError, EOFError):
            pass
        print(f"Enter a whole number from {minimum} to {maximum}.")


def show_discovery() -> None:
    print_heading("COHORT-LEVEL PATTERN DISCOVERY")
    candidates = discover_candidates()
    print(f"Synthetic profiles analysed: {len(PROFILES)}")
    print(f"Multisystem candidate pairs: {len(candidates)}")

    for rank, item in enumerate(candidates[:10], start=1):
        names = [FEATURES[key].name for key in item.shared_feature_ids]
        print(f"\n{rank}. {item.profile_a.name} <-> {item.profile_b.name}")
        print("   Shared features:", ", ".join(names))
        print("   Organ systems:", ", ".join(item.shared_systems))
        print(f"   Phenotype similarity: {item.phenotype_similarity:.3f}")
        print(f"   Temporal compatibility: {item.temporal_compatibility:.3f}")
        print(f"   Combined ranking: {item.combined_score:.3f}")

    print("\nThese are candidate patterns in fictional data, not discoveries.")


def show_profile(profile: Profile) -> None:
    print_heading(f"TEMPORAL PROFILE: {profile.name}")
    print("Profile ID:", profile.profile_id)
    print("Evidence status: Synthetic demonstration only\n")
    ordered = sorted(
        profile.observations,
        key=lambda item: (item.onset_start_years + item.onset_end_years) / 2,
    )
    for index, observation in enumerate(ordered, start=1):
        feature = FEATURES[observation.feature_id]
        print(f"{index}. {feature.name} [{feature.system}]")
        print(
            "   Illustrative onset interval: "
            f"{observation.onset_start_years:g} to {observation.onset_end_years:g} years"
        )
    print("\nIntervals are ranges, not exact patient-level event dates.")
    print("Overlapping intervals cannot establish which feature came first.")


def show_comparison() -> None:
    print_heading("COMPARE TWO PROFILES")
    for index, profile in enumerate(PROFILES, start=1):
        print(f"{index}. {profile.name}")

    first = ask_integer("\nChoose profile A: ", 1, len(PROFILES))
    second = ask_integer("Choose profile B: ", 1, len(PROFILES))
    if first == second:
        print("Choose two different profiles.")
        return

    result = compare_profiles(PROFILES[first - 1], PROFILES[second - 1])
    print_heading("COMPARISON RESULTS")
    print("A:", result.profile_a.name)
    print("B:", result.profile_b.name)
    print(f"Weighted phenotype similarity: {result.phenotype_similarity:.3f}")
    print(f"Temporal interval compatibility: {result.temporal_compatibility:.3f}")
    print(f"Combined exploratory ranking: {result.combined_score:.3f}")
    print("Shared organ systems:", ", ".join(result.shared_systems) or "None")
    print("\nShared-feature interval comparisons:")
    for detail in result.interval_details:
        feature_name = FEATURES[detail.feature_id].name
        print(f"- {feature_name}")
        print(f"  A: {detail.interval_a} | B: {detail.interval_b} | {detail.relation}")
    print("\nScores are ranking aids, not probabilities or diagnoses.")


def show_hypotheses() -> None:
    print_heading("RESEARCH HYPOTHESIS DOSSIERS")
    items = generate_hypotheses()
    if not items:
        print("No candidate met the current criteria.")
        return

    for item in items:
        print(f"\n{item.hypothesis_id}")
        print("Research question:", item.research_question)
        print("Shared systems:", ", ".join(item.shared_systems))
        print(f"Phenotype similarity: {item.phenotype_similarity:.3f}")
        print(f"Temporal compatibility: {item.temporal_compatibility:.3f}")
        print("Suggested next step:", item.suggested_next_step)
        print("Status:", item.status)


def show_quality() -> None:
    print_heading("DATA QUALITY AND COVERAGE")
    observations = [item for profile in PROFILES for item in profile.observations]
    unique_features = {item.feature_id for item in observations}
    systems = {FEATURES[item.feature_id].system for item in observations}
    known_intervals = sum(
        item.onset_start_years is not None and item.onset_end_years is not None
        for item in observations
    )
    missing_intervals = len(observations) - known_intervals
    coverage = (known_intervals / len(observations) * 100) if observations else 0.0

    print("Profiles:", len(PROFILES))
    print("Feature observations:", len(observations))
    print("Unique demonstration features:", len(unique_features))
    print("Organ-system labels:", len(systems))
    print("Known onset intervals:", known_intervals)
    print("Missing onset intervals:", missing_intervals)
    print(f"Onset coverage: {coverage:.0f}%")
    print("\nIMPORTANT: coverage describes only this constructed demo.")
    print("It says nothing about real-world biomedical datasets.")
    print("No patient records or real disease annotations are included.")


def question_builder() -> None:
    print_heading("RESEARCH QUESTION BUILDER")
    feature_ids = sorted(FEATURES)
    for index, feature_id in enumerate(feature_ids, start=1):
        feature = FEATURES[feature_id]
        print(f"{index}. {feature.name} [{feature.system}]")

    first = ask_integer("\nChoose feature one: ", 1, len(feature_ids))
    second = ask_integer("Choose feature two: ", 1, len(feature_ids))
    if first == second:
        print("Choose two different features.")
        return

    feature_a = FEATURES[feature_ids[first - 1]]
    feature_b = FEATURES[feature_ids[second - 1]]
    print("\nExploratory research question:")
    print(
        "Across independently curated datasets, does the co-occurrence "
        f"of {feature_a.name} and {feature_b.name} represent a reproducible pattern?"
    )
    print("\nSuggested method: define both features, identify suitable datasets,")
    print("measure co-occurrence, examine chronology and missing data, and seek")
    print("independent replication.")
    print("\nThis builder creates questions, not evidence.")


def about() -> None:
    print_heading("ABOUT THE PROJECT")
    print(f"{PROJECT_NAME} ({PROJECT_SHORT_NAME})")
    print("Version:", VERSION)
    print("\nTRDDE explores multisystem feature overlap and illustrative onset")
    print("intervals to formulate research questions for further study.")
    print("\nWorkflow: represent features -> compare profiles -> examine")
    print("temporal compatibility -> rank candidate patterns -> formulate")
    print("hypotheses -> export a structured JSON report.")
    print("\nCurrent limitation: all built-in profiles are fictional and synthetic.")
    print("No live biomedical datasets or literature searches are connected.")
    print("\nTRDDE is not a diagnostic or clinical decision-support tool.")


def run_menu() -> None:
    while True:
        print_heading(PROJECT_NAME.upper())
        print(f"Version {VERSION} | GitHub development edition")
        print(f"Profiles: {len(PROFILES)} | Dataset: Synthetic demonstration")
        print("\n1. Run cohort-level pattern discovery")
        print("2. Explore a temporal profile")
        print("3. Compare two profiles")
        print("4. View research hypothesis dossiers")
        print("5. View data quality and coverage")
        print("6. Build a research question")
        print("7. Export a JSON research report")
        print("8. About this project")
        print("0. Exit")

        try:
            choice = input("\nChoose an option: ").strip()
        except EOFError:
            print("\nInput ended. Goodbye.")
            return

        actions = {
            "1": show_discovery,
            "3": show_comparison,
            "4": show_hypotheses,
            "5": show_quality,
            "6": question_builder,
            "8": about,
        }

        if choice == "0":
            print("\nThank you for exploring TRDDE.")
            print("Patterns are questions. Evidence moves science forward.")
            return
        if choice == "2":
            for index, profile in enumerate(PROFILES, start=1):
                print(f"{index}. {profile.name}")
            selected = ask_integer("Choose a profile: ", 1, len(PROFILES))
            show_profile(PROFILES[selected - 1])
        elif choice == "7":
            try:
                path = export_report()
                print(f"Report exported to: {path}")
            except OSError as error:
                print(f"Could not write report: {error}")
        elif choice in actions:
            actions[choice]()
        else:
            print("Invalid choice. Select one of the listed options.")
            continue

        if choice in {"1", "2", "3", "4", "5", "6", "7", "8"}:
            pause()


def main(argv: list[str] | None = None) -> int:
    """Program entry point. Returns an exit status suitable for command lines."""
    parser = argparse.ArgumentParser(
        description="Explore synthetic multisystem feature patterns and onset intervals."
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="validate the built-in synthetic dataset and exit",
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="print the cohort-level candidate summary and exit",
    )
    parser.add_argument(
        "--export", nargs="?", const="trdde_research_report.json", metavar="PATH",
        help="export a JSON report (default: trdde_research_report.json)",
    )
    args = parser.parse_args(argv)

    errors = validate_dataset()
    if errors:
        print_heading("DATA VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    if args.validate:
        print("Dataset validation passed.")
        print(f"Profiles: {len(PROFILES)} | Features: {len(FEATURES)}")
        print(f"Observations: {sum(len(profile.observations) for profile in PROFILES)}")
        return 0

    if args.summary:
        show_discovery()
        return 0

    if args.export is not None:
        try:
            path = export_report(args.export)
            print(f"Research report exported to: {path}")
            return 0
        except OSError as error:
            print(f"Could not export report: {error}", file=sys.stderr)
            return 1

    run_menu()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
