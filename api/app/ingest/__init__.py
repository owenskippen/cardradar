"""Card show ingestion pipeline.

collect posts (sources/) -> keyword filter -> Claude extraction -> geocode
-> dedupe against existing events -> save as hidden events for admin review.

Run with:  python -m app.ingest --help
"""
