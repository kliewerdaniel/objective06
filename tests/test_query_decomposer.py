"""Tests for query_decomposer module."""

from __future__ import annotations

from self.query_decomposer import QueryDecomposer


def test_decompose_empty_query() -> None:
    decomposer = QueryDecomposer()
    result = decomposer.decompose("")
    assert result == []


def test_decompose_simple_query() -> None:
    decomposer = QueryDecomposer()
    result = decomposer.decompose("What is my project status?")
    assert len(result) == 1
    assert result[0]["complexity"] == "simple"
    assert result[0]["intent"] == "factual"


def test_decompose_complex_query() -> None:
    decomposer = QueryDecomposer()
    result = decomposer.decompose("What is my project status and what tasks are due?")
    assert len(result) == 1
    assert result[0]["complexity"] == "complex"
    assert len(result[0]["sub_queries"]) >= 2


def test_decompose_entity_query() -> None:
    decomposer = QueryDecomposer()
    result = decomposer.decompose("Tell me about the project goals")
    assert result[0]["intent"] in ["entity", "factual"]


def test_decompose_reflection_query() -> None:
    decomposer = QueryDecomposer()
    result = decomposer.decompose("What do you think about my progress?")
    assert result[0]["intent"] in ["reflection", "factual"]


def test_decompose_conversation_query() -> None:
    decomposer = QueryDecomposer()
    result = decomposer.decompose("Hello there")
    assert result[0]["intent"] == "conversation"
