from app import schemas


def generate_summary(turns: list[schemas.ConversationTurnResponse]) -> schemas.LearningSummary:
    server_turns = [t for t in turns if t.speaker == "server"]

    key_expressions: list[schemas.KeyExpression] = []
    seen = set()

    for turn in server_turns:
        if not turn.translated_text or turn.original_text in seen:
            continue
        seen.add(turn.original_text)
        key_expressions.append(
            schemas.KeyExpression(
                original=turn.original_text,
                translation=turn.translated_text,
                intent=turn.intent or "other",
                suggested_responses=turn.suggested_responses or [],
            )
        )

    return schemas.LearningSummary(
        total_turns=len(turns),
        server_turns=len(server_turns),
        key_expressions=key_expressions,
    )
