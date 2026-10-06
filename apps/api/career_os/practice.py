"""Formative next actions, never a mastery score, prerequisite lock or hiring prediction."""

from typing import Any

from career_os.contracts import digest

POLICY = "formative-next-practice/1"


def next_practice(units: list[dict[str, Any]], latest: dict[str, dict[str, Any]]) -> dict[str, Any]:
    items = []
    for unit in sorted(units, key=lambda x: x["week"]):
        attempt = latest.get(unit["id"])
        if attempt is None:
            state = "not_started"
            reason = "Dersi oku, küçük örneği elle çöz ve ilk denemeni kaydet."
        elif attempt.get("content_fingerprint") != digest(unit):
            state = "refresh_lesson"
            reason = (
                "Ders içeriği değişti. "
                "Eski yanıtları yeni içerik için başarı saymadan yeniden çalış."
            )
        elif attempt.get("objective_correct", 0) < attempt.get("objective_total", 1):
            state = "revisit_concept"
            reason = (
                "Son denemede yanlış seçenek var. "
                "Açıklamayı oku, bir karşı örnek kur ve yeniden dene."
            )
        elif attempt.get("assistance") != "independent":
            state = "independent_practice"
            reason = (
                "Seçenekler doğru; bu deneme yardımlı. "
                "Referansı kapatıp farklı bir örneği kendin uygula."
            )
        else:
            state = "defend_and_review"
            reason = (
                "Bağımsızlık öz bildirimin. Kodunu, görünmeyen bir hatayı düzeltmeni "
                "ve İngilizce savunmanı birine incelet."
            )
        items.append(
            {
                "lesson_id": unit["id"],
                "week": unit["week"],
                "title": unit["title"],
                "state": state,
                "reason": reason,
                "attempt_id": attempt.get("id") if attempt else None,
            }
        )
    # Work through the earliest unfinished objective/practice step. A self-reported
    # successful attempt allows another study suggestion, not a mastery promotion.
    candidate = next(
        (x for x in items if x["state"] != "defend_and_review"), items[0] if items else None
    )
    return {
        "policy_version": POLICY,
        "items": items,
        "suggested_lesson_id": candidate["lesson_id"] if candidate else None,
        "scope": (
            "Son ders denemelerine dayalı çalışma önerisi; "
            "ustalık, CEFR veya işe hazır olma ölçümü değildir."
        ),
        "review_backlog": [x["lesson_id"] for x in items if x["state"] == "defend_and_review"],
    }
