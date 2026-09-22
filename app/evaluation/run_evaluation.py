from app.db.database import SessionLocal
from app.evaluation.retrieval_evaluator import evaluate_retrieval


USER_ID = 5


def main():
    db = SessionLocal()

    try:
        evaluation_result = evaluate_retrieval(
            db=db,
            user_id=USER_ID,
            top_k=5,
        )

        print("\n" + "=" * 60)
        print("RETRIEVAL EVALUATION")
        print("=" * 60)

        print(
            f"\nTotal Questions: "
            f"{evaluation_result['total_questions']}"
        )

        print(
            f"Hit@5: "
            f"{evaluation_result['hit_at_k']:.2f}"
        )

        print(
            f"Recall@5: "
            f"{evaluation_result['recall_at_k']:.2f}"
        )

        print(
            f"MRR: "
            f"{evaluation_result['mrr']:.2f}"
        )

        print("\n" + "-" * 60)
        print("QUESTION RESULTS")
        print("-" * 60)

        for index, result in enumerate(
            evaluation_result["results"],
            start=1,
        ):
            print(f"\nQuestion {index}:")
            print(f"  {result['question']}")

            print(
                f"  Expected chunks: "
                f"{result['expected_chunk_ids']}"
            )

            print(
                f"  Retrieved chunks: "
                f"{result['retrieved_chunk_ids']}"
            )

            print(
                f"  Hit@5: "
                f"{result['hit_at_k']}"
            )

            print(
                f"  Recall@5: "
                f"{result['recall_at_k']:.2f}"
            )

            print(
                f"  Reciprocal Rank: "
                f"{result['reciprocal_rank']:.2f}"
            )

        print("\n" + "=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()