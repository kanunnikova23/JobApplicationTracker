from app.api.deps import get_db


# Testing for dependency logic.
def test_get_db(db):
    gen = get_db()  # call your generator dependency
    db = next(gen)  # get the yielded session

    assert db is not None
    from app.db.database import SessionLocal
    assert isinstance(db, SessionLocal().__class__)

    try:
        next(gen)  # run cleanup
    except StopIteration:
        pass