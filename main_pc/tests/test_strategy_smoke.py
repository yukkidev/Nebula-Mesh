import asyncio


def test_basic_heuristic_strategy_smoke():
    from main_pc.strategy import BasicHeuristicStrategy

    strat = BasicHeuristicStrategy()
    text = "URGENT: finish this\n- buy milk\n* call mom"

    categories = asyncio.run(strat.classify(text))
    todos = asyncio.run(strat.extract_todos(text))
    importance = asyncio.run(strat.rate_importance(text))

    assert categories and categories[0]["category"] in {"tasks", "notes"}
    assert {t["task"] for t in todos} == {"buy milk", "call mom"}
    assert importance == 10
