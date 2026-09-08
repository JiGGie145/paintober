"""Smoke test for the standalone maturin extension."""

import paintober_native


assert paintober_native.module_name() == "paintober_native"
