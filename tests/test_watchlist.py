"""
tests/test_watchlist.py — CineLog

Tests for the watchlist feature.
"""

from services.collection_service import FilmNotFoundError
import pytest
from app import create_app, db
from models import User, Film, WatchlistEntry
from services.watchlist_service import add_to_watchlist, remove_from_watchlist, NotInWatchlistError

@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def sample_user(app):
    """A user to use in tests."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id

@pytest.fixture
def sample_film(app):
    """A film to use in tests."""
    with app.app_context():
        film = Film(title="Paddington 2", year=2017, genre="Comedy")
        db.session.add(film)
        db.session.commit()
        return film.id

# ── Nonexistent film ───────────────────────────────────────────────────────────────

def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """
    Adding a film_id that doesn't exist in the database should raise
    FilmNotFoundError, not a database integrity error.
    """
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(user_id=sample_user, film_id=fake_film_id)


# ── Remove from watchlist ──────────────────────────────────────────────────────────

def test_remove_from_watchlist_not_found_raises(app, sample_user, sample_film):
    """
    Attempting to remove a film that is not in the user's watchlist
    should raise NotInWatchlistError.
    """
    with app.app_context():
        # The film exists, but the user hasn't added it to their watchlist
        with pytest.raises(NotInWatchlistError):
            remove_from_watchlist(user_id=sample_user, film_id=sample_film)

