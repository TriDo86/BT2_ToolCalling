from datetime import datetime

from app.config import get_setting
from app.database import Base, make_session_factory
from app.model_db import Customer, Invoice, Transfer
from app.tools import find_two_transfer_match, list_unmatched_transfers


def add_sample(db, model, **fields):
    existing = db.get(model, fields["id"])
    if existing is None:
        db.add(model(**fields))
    elif any(getattr(existing, name) != value for name, value in fields.items()):
        raise ValueError(f"{model.__name__} {fields['id']} already has different data")


def seed_demo(database_url: str) -> list[str]:
    engine, session_factory = make_session_factory(database_url)
    try:
        Base.metadata.create_all(engine)

        with session_factory.begin() as db:
            add_sample(db, Customer, id="C-12", name="Khách mẫu C-12")
            add_sample(db, Customer, id="C-99", name="Khách mẫu C-99")
            db.flush()

            add_sample(
                db,
                Invoice,
                id="I-77",
                customer_id="C-12",
                currency="VND",
                total_amount=1_500_000,
                missing_amount=1_500_000,
            )

            for transfer_id, minute, customer_id, currency, amount in [
                ("P1", 0, "C-12", "VND", 900_000),
                ("P4", 2, "C-99", "VND", 600_000),
                ("P5", 3, "C-12", "USD", 600_000),
                ("P2", 5, "C-12", "VND", 600_000),
                ("P3", 10, "C-12", "VND", 600_000),
            ]:
                add_sample(
                    db,
                    Transfer,
                    id=transfer_id,
                    received_at=datetime(2026, 11, 3, 9, minute),
                    customer_id=customer_id,
                    currency=currency,
                    amount=amount,
                    status=False,
                )

            db.flush()
            eligible_ids = list_unmatched_transfers("C-12", "VND", db)
            matched_ids = find_two_transfer_match("I-77", db)
            if eligible_ids != ["P1", "P2", "P3"] or matched_ids != ["P1", "P2"]:
                raise ValueError(f"Unexpected I-77 result: {eligible_ids=}, {matched_ids=}")

        return matched_ids
    finally:
        engine.dispose()


if __name__ == "__main__":
    pair = seed_demo(get_setting().database_url)
    print(f"I-77: {' + '.join(pair)}")
