import pytest


def test_classification_engine_contract_smoke():
    from nebula_mesh.contracts import ClassificationEngine, ClassificationStrategy

    class DummyStrategy(ClassificationStrategy):
        async def classify(self, text: str):
            return [{"category": "test"}]

        async def extract_todos(self, text: str):
            return [{"task": "t"}]

        async def rate_importance(self, text: str) -> int:
            return 7

    engine = ClassificationEngine(strategy=DummyStrategy())

    import asyncio

    result = asyncio.run(engine.process("hello"))
    assert result.importance == 7
    assert result.categories[0]["category"] == "test"
    assert result.todos[0]["task"] == "t"
