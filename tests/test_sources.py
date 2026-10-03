from harness_model_sync.sources import parse_llamacpp, parse_openrouter

OPENROUTER_PAYLOAD = {
    "data": [
        {"id": "z-ai/glm-5.3-flash", "context_length": 1048576,
         "top_provider": {"max_completion_tokens": 131072}},
        {"id": "deepseek/deepseek-v4-flash", "context_length": 1048576,
         "top_provider": {"max_completion_tokens": 131072}},
    ]
}

LLAMACPP_PAYLOAD = {
    "data": [
        {"id": "nex-n25-mini-uncensored-q8",
         "status": {"args": ["llama-server", "--ctx-size", "262144", "--port", "0"]}},
        {"id": "qwen-3.8-flash-next-iq3",
         "status": {"args": ["llama-server", "--ctx-size=131072"]}},
    ]
}


def test_parse_openrouter_maps_context_and_max_output():
    models = parse_openrouter(OPENROUTER_PAYLOAD)
    assert (models[0].provider, models[0].id) == ("openrouter", "z-ai/glm-5.3-flash")
    assert models[0].context_window == 1048576
    assert models[0].max_output == 131072


def test_parse_llamacpp_reads_ctx_size_from_args():
    models = parse_llamacpp(LLAMACPP_PAYLOAD, provider="llama-dgx")
    assert models[0].context_window == 262144
    assert models[1].context_window == 131072
    assert models[0].provider == "llama-dgx"
