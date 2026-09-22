from sqlalchemy.orm import Session

from app.services.retrieval_service import retrieve_relevant_chunks


evaluation_dataset = [
    {
        "question": "What is AI Recommendation Logic?",
        "document_id": 5,
        "expected_chunk_ids": [80],
    },
    {
        "question": "What is the purpose of AI Recommendation Logic?",
        "document_id": 5,
        "expected_chunk_ids": [80, 82],
    },
    {
        "question": "How does the recommendation system match users with items?",
        "document_id": 5,
        "expected_chunk_ids": [80, 82],
    },
    {
        "question": "What approach is used to generate recommendations?",
        "document_id": 5,
        "expected_chunk_ids": [80, 82],
    },
    {
        "question": "What is the main goal of the recommendation system?",
        "document_id": 5,
        "expected_chunk_ids": [82],
    },
]


def calculate_hit_at_k(
    retrieved_chunk_ids: list[int],
    expected_chunk_ids: list[int],
    k: int = 5,
) -> int:
    """
    Returns 1 if at least one expected chunk
    appears in the top K retrieved results.
    Otherwise returns 0.
    """

    top_k_ids = retrieved_chunk_ids[:k]

    for chunk_id in expected_chunk_ids:
        if chunk_id in top_k_ids:
            return 1

    return 0


def calculate_recall_at_k(
    retrieved_chunk_ids: list[int],
    expected_chunk_ids: list[int],
    k: int = 5,
) -> float:
    """
    Measures how many expected relevant chunks
    were retrieved in the top K results.
    """

    top_k_ids = retrieved_chunk_ids[:k]

    if not expected_chunk_ids:
        return 0.0

    relevant_retrieved = sum(
        1
        for chunk_id in expected_chunk_ids
        if chunk_id in top_k_ids
    )

    return relevant_retrieved / len(expected_chunk_ids)


def calculate_reciprocal_rank(
    retrieved_chunk_ids: list[int],
    expected_chunk_ids: list[int],
) -> float:
    """
    Returns the reciprocal rank of the first
    relevant retrieved chunk.

    Example:
    First relevant result at position 1 -> 1.0
    First relevant result at position 2 -> 0.5
    First relevant result at position 3 -> 0.333
    """

    for rank, chunk_id in enumerate(
        retrieved_chunk_ids,
        start=1,
    ):
        if chunk_id in expected_chunk_ids:
            return 1 / rank

    return 0.0


def evaluate_retrieval(
    db: Session,
    user_id: int,
    top_k: int = 5,
) -> dict:
    """
    Runs the evaluation dataset against
    the current retrieval pipeline.
    """

    results = []

    total_hit_at_k = 0
    total_recall_at_k = 0.0
    total_reciprocal_rank = 0.0

    for item in evaluation_dataset:

        retrieved_chunks = retrieve_relevant_chunks(
            db=db,
            question=item["question"],
            document_id=item["document_id"],
            user_id=user_id,
            top_k=top_k,
        )

        retrieved_chunk_ids = [
            chunk["chunk_id"]
            for chunk in retrieved_chunks
        ]

        hit_at_k = calculate_hit_at_k(
            retrieved_chunk_ids=retrieved_chunk_ids,
            expected_chunk_ids=item["expected_chunk_ids"],
            k=top_k,
        )

        recall_at_k = calculate_recall_at_k(
            retrieved_chunk_ids=retrieved_chunk_ids,
            expected_chunk_ids=item["expected_chunk_ids"],
            k=top_k,
        )

        reciprocal_rank = calculate_reciprocal_rank(
            retrieved_chunk_ids=retrieved_chunk_ids,
            expected_chunk_ids=item["expected_chunk_ids"],
        )

        total_hit_at_k += hit_at_k
        total_recall_at_k += recall_at_k
        total_reciprocal_rank += reciprocal_rank

        results.append(
            {
                "question": item["question"],
                "expected_chunk_ids": item["expected_chunk_ids"],
                "retrieved_chunk_ids": retrieved_chunk_ids,
                "hit_at_k": hit_at_k,
                "recall_at_k": recall_at_k,
                "reciprocal_rank": reciprocal_rank,
            }
        )

    total_questions = len(evaluation_dataset)

    if total_questions == 0:
        return {
            "total_questions": 0,
            "hit_at_k": 0.0,
            "recall_at_k": 0.0,
            "mrr": 0.0,
            "results": [],
        }

    return {
        "total_questions": total_questions,
        "hit_at_k": total_hit_at_k / total_questions,
        "recall_at_k": total_recall_at_k / total_questions,
        "mrr": total_reciprocal_rank / total_questions,
        "results": results,
    }