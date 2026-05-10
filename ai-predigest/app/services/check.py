"""
Timing Integrity Debugger

Scans:
- All domains
- All evaluators
- All questions
- Validates TIMING questions

Checks:
1. sub_subdomain → TIMING_BY_SUB_SUBDOMAIN mapping
2. timing rule exists in TIMING_RULES
3. multiple timing questions per subtopic
"""

from collections import defaultdict

from app.domains.registry import DOMAIN_REGISTRY
from app.domains.base import QueryType
from app.services.timing_engine import TIMING_RULES
from app.services.astro_engine import TIMING_BY_SUB_SUBDOMAIN


def debug_timing_integrity():
    print("\n" + "=" * 80)
    print("🔍 TIMING INTEGRITY CHECK")
    print("=" * 80)

    timing_count_by_subtopic = defaultdict(int)
    errors = []

    for domain, subtopic_map in DOMAIN_REGISTRY.items():
        print(f"\n📘 DOMAIN: {domain}")

        for subtopic, evaluator_cls in subtopic_map.items():
            evaluator = evaluator_cls()
            questions = evaluator.get_questions()

            for q in questions:
                if q.meta.query_type != QueryType.TIMING:
                    continue

                timing_count_by_subtopic[(domain, subtopic)] += 1
                sub_sub = q.sub_subdomain
                qid = q.id

                print(f"\n  ⏱️ TIMING QUESTION FOUND")
                print(f"     Domain        : {domain}")
                print(f"     Subtopic      : {subtopic}")
                print(f"     Question ID   : {qid}")
                print(f"     Sub-subdomain : {sub_sub}")

                # ---- Mapping check
                timing_name = TIMING_BY_SUB_SUBDOMAIN.get(sub_sub)
                if not timing_name:
                    errors.append(
                        f"❌ Missing TIMING_BY_SUB_SUBDOMAIN mapping: '{sub_sub}'"
                    )
                    print("     ❌ No TIMING_BY_SUB_SUBDOMAIN mapping")
                    continue

                print(f"     ✔ Timing Rule : {timing_name}")

                # ---- TIMING_RULES existence check
                if timing_name not in TIMING_RULES:
                    errors.append(
                        f"❌ Missing TIMING_RULES entry: '{timing_name}'"
                    )
                    print("     ❌ Timing rule NOT found in TIMING_RULES")
                else:
                    print("     ✔ TIMING_RULES entry exists")

    # ---- Multiple timing question check
    print("\n" + "-" * 80)
    print("🔁 MULTIPLE TIMING QUESTIONS CHECK")
    print("-" * 80)

    for (domain, subtopic), count in timing_count_by_subtopic.items():
        if count > 1:
            print(
                f"⚠️ MULTIPLE TIMING QUESTIONS: "
                f"{domain} / {subtopic} → {count}"
            )

    # ---- Final summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)

    if not errors:
        print("✅ NO TIMING ISSUES FOUND — SYSTEM IS CONSISTENT")
    else:
        print("❌ ISSUES FOUND:")
        for e in errors:
            print(" ", e)


if __name__ == "__main__":
    debug_timing_integrity()
