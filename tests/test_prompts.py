from src.prompts import build_country_prompt


def test_build_country_prompt_contains_country_and_transcript() -> None:
    prompt = build_country_prompt(country="Indonesia", transcript="这是一个护肤产品演示")
    assert "Indonesia" in prompt
    assert "这是一个护肤产品演示" in prompt
    assert "JSON" in prompt


def test_build_country_prompt_includes_brand_context() -> None:
    prompt = build_country_prompt(
        country="Brazil",
        transcript="视频展示了跑鞋的缓震效果",
        brand_context="主打轻量与通勤",
    )
    assert "主打轻量与通勤" in prompt
