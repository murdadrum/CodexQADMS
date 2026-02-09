from __future__ import annotations

from typing import Any

from packages.contracts import CanonicalTokenModel


# Example deterministic rule summary used by tests.
def evaluate_token_coverage(canonical: CanonicalTokenModel) -> dict[str, Any]:
    return {
        "source": canonical.source,
        "token_counts": canonical.token_counts(),
        "total_tokens": len(canonical.tokens),
    }
