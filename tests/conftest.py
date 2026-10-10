# Loaded by pytest before any test module, so the Arcade PATH guard in the
# snake package runs before a test imports Arcade directly.
import snake  # noqa: F401
