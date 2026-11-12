from sqlalchemy import select
from sqlalchemy.orm import Session

from .model_db import Invoice, Transfer, Proposal
from .algorithm import two_sum

def get_open_invoice(invoice_id: str, db: Session) -> dict:
    invoice = db.get(Invoice, invoice_id)

    if invoice is None:
        return {"error": "invoice_not_found", "invoice_id": invoice_id}

    return {
        "customer_id": invoice.customer_id,
        "currency": invoice.currency,
        "missing_amount": invoice.missing_amount,
        "status": "PAID" if invoice.missing_amount==0 else "OPEN",
    }

def list_unmatched_transfers(customer_id: str, currency: str, db: Session) -> list:
    query = (
        select(Transfer.id)
        .where(
            Transfer.customer_id == customer_id,
            Transfer.currency == currency,
            Transfer.status.is_(False),
        )
        .order_by(Transfer.received_at, Transfer.id)
    )
    return db.scalars(query).all()

def find_two_transfer_match(invoice_id, db: Session) -> tuple:
    invoice = get_open_invoice(invoice_id, db)

    if invoice.get("error"):
        return None

    query = select(Transfer.id, Transfer.amount).where(
        Transfer.customer_id == invoice["customer_id"], 
        Transfer.currency == invoice["currency"],
        Transfer.status.is_(False))
    transfers = db.execute(query).all()

    t1, t2 = two_sum(invoice["total_amount"], [t.right for t in transfers])

    if t1 == None:
        return (None, None)

    return transfers[t1], transfers[t2]

def propose_invoice_match(invoice_id: str, transfer_ids: tuple, db: Session):
    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        return {"error": "invoice_not_found", "invoice_id": invoice_id}

    if invoice.missing_amount <= 0:
        return {"error": "invoice_fullfilled", "invoice_id": invoice_id}

    if transfer_ids[0] == transfer_ids[1]:
        return {"error": "same_transfer", "transfer_ids": transfer_ids}

    t1 = db.get(Transfer, transfer_ids[0])

    if t1 is None:
        return {"error": "transfer_not_found", "transfer_id": transfer_ids[0]}

    if t1.status == True:
        return {"error": "transfer_is_matched", "transfer_id": transfer_ids[0]} 

    t2 = db.get(Transfer, transfer_ids[1])

    if t2 is None:
        return {"error": "transfer_not_found", "transfer_id": transfer_ids[1]}

    if t2.status == True:
        return {"error": "transfer_is_matched", "transfer_id": transfer_ids[1]} 

    db.add(Proposal(invoice_id=invoice_id, transfer_id1=t1.id, transfer_id2=t2.id))
    db.commit()

    return