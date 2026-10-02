"""sizing.py — the arithmetic for running a model on your own machine: will it fit,
how long will it take, and does the prompt fit the context window."""

# Average bits stored per weight for common GGUF quantisations (they mix precisions internally).
BITS_PER_WEIGHT = {"Q8_0": 8.5, "Q6_K": 6.6, "Q5_K_M": 5.7, "Q4_K_M": 4.8, "Q3_K_M": 3.9}


def weights_gb(billions_of_params: float, quant: str) -> float:
    """Memory for the weights alone: parameters × bits per weight ÷ 8 bits per byte."""
    return round(billions_of_params * BITS_PER_WEIGHT[quant] / 8, 1)


def fits(model_gb: float, free_ram_gb: float, headroom_gb: float = 1.5) -> bool:
    """Leave headroom for the context cache and the runtime, or the system starts swapping."""
    return model_gb + headroom_gb <= free_ram_gb


def generation_seconds(output_tokens: int, tokens_per_second: float) -> float:
    """Output is produced one token at a time, so time is tokens ÷ rate."""
    return round(output_tokens / tokens_per_second, 1)


def prompt_budget(context_window: int, reserve_for_reply: int) -> int:
    """What's left for the prompt once the reply's space is set aside."""
    return context_window - reserve_for_reply


def fits_context(fixed_overhead: int, lesson_tokens: int, chat_tokens: int,
                 context_window: int, reserve_for_reply: int) -> bool:
    return fixed_overhead + lesson_tokens + chat_tokens <= prompt_budget(context_window, reserve_for_reply)


def words_to_tokens(words: int) -> int:
    """English averages roughly 1.3 tokens per word; code and markdown run higher."""
    return round(words * 1.3)
