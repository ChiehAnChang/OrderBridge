from app import schemas
from app.services.classifier import INTENT_ICONS


def generate_summary(turns: list[schemas.ConversationTurnResponse]) -> schemas.LearningSummary:
    server_turns = [t for t in turns if t.speaker == "server"]

    key_expressions: list[schemas.KeyExpression] = []
    seen = set()

    for turn in server_turns:
        if not turn.translated_text or turn.original_text in seen:
            continue
        seen.add(turn.original_text)
        intent = turn.intent or "other"
        key_expressions.append(
            schemas.KeyExpression(
                original=turn.original_text,
                translation=turn.translated_text,
                intent=intent,
                icon=INTENT_ICONS.get(intent, "❓"),
                suggested_responses=turn.suggested_responses or [],
            )
        )

    return schemas.LearningSummary(
        total_turns=len(turns),
        server_turns=len(server_turns),
        key_expressions=key_expressions,
    )
