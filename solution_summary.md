# Solution Summary

## Issue
The application was failing to start with the error:
```
sqlalchemy.exc.UnboundExecutionError: Could not locate a bind configured on mapper Mapper[User(users)], SQL expression or this Session.
```

## Root Cause
In `app/db.py`, the `async_session` is created but not bound to the engine until `initialize_db()` is called. The application was trying to use the session in `main.py` before initializing the database connection.

## Solution
Added a call to `initialize_db()` in the `on_startup` function in `main.py` before using the session:

```python
@app.on_event("startup")
async def on_startup():
    # Run alembic upgrade head
    subprocess.run(["alembic", "upgrade", "head"])
    
    # Initialize database connection
    await initialize_db()

    # Ensure at least one admin user exists
    async with async_session() as session:
        # ...
```

This ensures the database connection is properly established and the session is bound to the engine before any database operations are performed.