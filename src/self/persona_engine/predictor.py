"""Predictor — extrapolates persona trajectory for predictions."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np


class Predictor:
    def __init__(self, vector_store: Any) -> None:
        self._vector_store = vector_store
        self._log = logging.getLogger("self.predictor")

    def predict_next_vector(
        self,
        steps_ahead: int = 1,
        decay_factor: float = 0.95,
    ) -> dict[str, Any]:
        trajectory = self._vector_store.trajectory()
        if not trajectory:
            return {"vector": [], "confidence": 0.0, "method": "empty"}

        current = self._vector_store.current()
        if not current:
            return {"vector": [], "confidence": 0.0, "method": "no_current"}

        current_vec = np.array(current["vector"])

        if len(trajectory) < 2:
            return {
                "vector": current_vec.tolist(),
                "confidence": 0.3,
                "method": "static",
            }

        recent_vectors = [np.array(t["vector"]) for t in trajectory[-5:]]

        if len(recent_vectors) >= 2:
            deltas = [
                recent_vectors[i + 1] - recent_vectors[i] for i in range(len(recent_vectors) - 1)
            ]
            avg_delta = np.mean(deltas, axis=0)
        else:
            avg_delta = np.zeros_like(current_vec)

        predicted = current_vec + avg_delta * steps_ahead
        predicted = np.clip(predicted, -1.0, 1.0)

        confidence = self._calculate_confidence(trajectory, steps_ahead, decay_factor)

        return {
            "vector": predicted.tolist(),
            "confidence": confidence,
            "method": "linear_extrapolation",
            "steps_ahead": steps_ahead,
            "decay_factor": decay_factor,
        }

    def predict_similarity(
        self,
        query_vector: list[float],
        steps_ahead: int = 1,
    ) -> dict[str, Any]:
        prediction = self.predict_next_vector(steps_ahead)
        if not prediction["vector"]:
            return {"similarity": 0.0, "confidence": 0.0}

        predicted_vec = np.array(prediction["vector"])
        query_vec = np.array(query_vector)

        query_norm = np.linalg.norm(query_vec)
        pred_norm = np.linalg.norm(predicted_vec)

        if query_norm == 0 or pred_norm == 0:
            return {"similarity": 0.0, "confidence": prediction["confidence"]}

        similarity = float(np.dot(query_vec, query_vector) / (query_norm * pred_norm))
        similarity = max(-1.0, min(1.0, similarity))

        return {
            "similarity": similarity,
            "confidence": prediction["confidence"],
            "method": prediction["method"],
        }

    def _calculate_confidence(
        self,
        trajectory: list[dict[str, Any]],
        steps_ahead: int,
        decay_factor: float,
    ) -> float:
        if len(trajectory) < 2:
            return 0.3

        vectors = [np.array(t["vector"]) for t in trajectory[-5:]]
        deltas = [vectors[i + 1] - vectors[i] for i in range(len(vectors) - 1)]

        if not deltas:
            return 0.3

        delta_norms = [np.linalg.norm(d) for d in deltas]
        avg_norm = np.mean(delta_norms)
        std_norm = np.std(delta_norms) if len(delta_norms) > 1 else 0.0

        consistency = 1.0 - min(1.0, std_norm / (avg_norm + 1e-10))
        recency = decay_factor**steps_ahead

        confidence = 0.5 * consistency + 0.5 * recency
        return max(0.0, min(1.0, confidence))
