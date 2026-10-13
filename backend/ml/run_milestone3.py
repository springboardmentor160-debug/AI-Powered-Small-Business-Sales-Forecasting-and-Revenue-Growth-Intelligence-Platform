"""Run the whole Milestone 3 pipeline and write artifacts/milestone-3/.

Usage (from the project root, with the virtual environment active):

    python -m backend.ml.run_milestone3              # everything
    python -m backend.ml.run_milestone3 churn        # one part only
    python -m backend.ml.run_milestone3 recommendations anomaly
"""

import argparse
import logging
import time

from backend.ml import anomaly, churn, recommendations
from backend.ml.common import load_clean_sales

STEPS = {
    "recommendations": recommendations.run,
    "churn": churn.run,
    "anomaly": anomaly.run,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("steps", nargs="*", help=f"any of: {list(STEPS)}")
    args = parser.parse_args()
    selected = args.steps or list(STEPS)

    unknown = [name for name in selected if name not in STEPS]
    if unknown:
        parser.error(f"unknown step(s) {unknown}; choose from {list(STEPS)}")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("milestone3")

    started = time.time()
    sales = load_clean_sales()
    for name in selected:
        logger.info("=== %s ===", name)
        STEPS[name](sales)
    logger.info("Milestone 3 pipeline finished in %.0fs", time.time() - started)


if __name__ == "__main__":
    main()
