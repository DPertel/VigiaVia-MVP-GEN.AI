import json
import time
import re
import unicodedata
import statistics

from .retriever import Retriever
from .rag import VigiaIA
from .config import ROOT

EVAL = ROOT / "avaliacao"
OUT = EVAL / "resultados"
OUT.mkdir(parents=True, exist_ok=True)


def normalize(text):
    text = str(text).lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )
    return re.sub(r"\s+", " ", text).strip()


def retrieval_metrics(retriever, cases, gold):
    eligible = 0
    hits1 = 0
    hits3 = 0
    details = []

    gold_by_id = {item["id"]: item for item in gold}

    for case in cases:
        expected = set(
            gold_by_id[case["id"]]["expected_sources"]
        )

        found = retriever.search(case["question"], 3)
        ids = [item["source_id"] for item in found]

        if expected:
            eligible += 1
            hit1 = bool(set(ids[:1]) & expected)
            hit3 = bool(set(ids[:3]) & expected)
            hits1 += hit1
            hits3 += hit3
        else:
            hit1 = None
            hit3 = None

        details.append({
            "id": case["id"],
            "expected_sources": sorted(expected),
            "top3_sources": ids,
            "hit_at_1": hit1,
            "hit_at_3": hit3,
            "retrieved_scores": [
                round(item["score"], 4) for item in found
            ]
        })

    denominator = eligible or 1

    return {
        "eligible_cases": eligible,
        "excluded_abstention_cases": len(cases) - eligible,
        "recall_at_1": hits1 / denominator,
        "recall_at_3": hits3 / denominator,
        "details": details
    }


def is_valid_schema(response):
    if not isinstance(response, dict):
        return False

    required = {
        "answer", "citations", "abstained", "rationale"
    }

    return (
        required.issubset(response)
        and isinstance(response["answer"], str)
        and isinstance(response["citations"], list)
        and isinstance(response["abstained"], bool)
        and isinstance(response["rationale"], str)
    )


def response_metrics(runs, gold):
    gold_by_id = {item["id"]: item for item in gold}
    summary = {}

    for mode in ("base", "rag", "agent_rag"):
        selected = [
            item for item in runs if item["mode"] == mode
        ]

        successful = [
            item for item in selected
            if isinstance(item.get("response"), dict)
        ]

        schema_valid = 0
        correct_abstentions = 0
        term_matches = 0
        eligible_terms = 0

        citation_applicable = 0
        citation_covered = 0
        citation_checked = 0
        citation_references_valid = 0

        for run in selected:
            response = run.get("response")

            if not isinstance(response, dict):
                continue

            if is_valid_schema(response):
                schema_valid += 1

            expected = gold_by_id[run["case_id"]]
            abstained = response.get("abstained")

            if abstained == expected["must_abstain"]:
                correct_abstentions += 1

            if not expected["must_abstain"] and abstained is False:
                terms = expected.get("expected_terms", [])
                terms_any = expected.get("expected_terms_any", [])
                answer = normalize(response.get("answer", ""))

                has_term_criteria = bool(terms or terms_any)

                if has_term_criteria:
                    eligible_terms += 1

                    all_required_match = all(
                        normalize(term) in answer
                        for term in terms
                    )

                    any_alternative_match = (
                        not terms_any
                        or any(
                            normalize(term) in answer
                            for term in terms_any
                        )
                    )

                    if all_required_match and any_alternative_match:
                        term_matches += 1

            if mode != "base":
                citation_applicable += 1
                citations = response.get("citations", [])
                retrieved = response.get("retrieved", [])

                if citations:
                    citation_covered += 1
                    citation_checked += 1

                    allowed = {
                        (item.get("source_id"), item.get("chunk_id"))
                        for item in retrieved
                        if isinstance(item, dict)
                    }

                    all_valid = all(
                        isinstance(citation, dict)
                        and (
                            citation.get("source_id"),
                            citation.get("chunk_id")
                        ) in allowed
                        for citation in citations
                    )

                    if all_valid:
                        citation_references_valid += 1

        successful_count = len(successful)
        denominator = successful_count or 1

        latencies = [
            item["latency_seconds"]
            for item in selected
            if isinstance(item.get("latency_seconds"), (int, float))
        ]

        latency_stats = {
            "average_seconds": (
                round(statistics.mean(latencies), 3)
                if latencies else None
            ),
            "median_seconds": (
                round(statistics.median(latencies), 3)
                if latencies else None
            ),
            "min_seconds": round(min(latencies), 3) if latencies else None,
            "max_seconds": round(max(latencies), 3) if latencies else None
        }

        if mode == "base":
            citation_metrics = {
                "applicable": False,
                "coverage_rate": None,
                "reference_valid_rate": None,
                "cases_with_citations": 0
            }
        else:
            citation_metrics = {
                "applicable": True,
                "coverage_rate": (
                    citation_covered / (citation_applicable or 1)
                ),
                "reference_valid_rate": (
                    citation_references_valid / (citation_checked or 1)
                    if citation_checked else None
                ),
                "cases_with_citations": citation_covered,
                "cases_checked_for_reference": citation_checked
            }

        summary[mode] = {
            "total_cases": len(selected),
            "successful_cases": successful_count,
            "execution_errors": len(selected) - successful_count,
            "schema_valid_rate": schema_valid / denominator,
            "citation_metrics": citation_metrics,
            "correct_abstention_rate": (
                correct_abstentions / denominator
            ),
            "expected_terms_complete_rate": (
                term_matches / eligible_terms if eligible_terms else None
            ),
            "cases_with_expected_terms": eligible_terms,
            "latency": latency_stats
        }

    return summary


def main():
    cases = json.loads(
        (EVAL / "conjunto_teste.json").read_text(encoding="utf-8")
    )

    gold = json.loads(
        (EVAL / "gabarito.json").read_text(encoding="utf-8")
    )

    retriever = Retriever()
    engine = VigiaIA()

    results = {
        "retrieval": retrieval_metrics(retriever, cases, gold),
        "runs": []
    }

    for case in cases:
        for mode in ("base", "rag", "agent_rag"):
            start = time.perf_counter()

            try:
                response = engine.ask(case["question"], mode)
                error = None
            except Exception as exc:
                response = None
                error = str(exc)

            results["runs"].append({
                "case_id": case["id"],
                "mode": mode,
                "latency_seconds": round(
                    time.perf_counter() - start, 3
                ),
                "response": response,
                "error": error
            })

    results["response_metrics"] = response_metrics(
        results["runs"], gold
    )

    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = OUT / f"avaliacao-{stamp}.json"

    path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\nResults: {path}")

    print("\nRETRIEVAL")
    print("Recall@1:", round(
        results["retrieval"]["recall_at_1"], 3
    ))
    print("Recall@3:", round(
        results["retrieval"]["recall_at_3"], 3
    ))
    print(
        "Eligible cases:",
        results["retrieval"]["eligible_cases"]
    )

    print("\nMETRICS BY CONFIGURATION")

    for mode, metrics in results["response_metrics"].items():
        print(f"\n{mode}:")
        for name, value in metrics.items():
            print(f"  {name}: {value}")


if __name__ == "__main__":
    main()
