from typing import Protocol


class Synthesizer(Protocol):
    def __call__(self, prompt_text: str) -> str: ...


def passthrough_synth(prompt_text: str) -> str:
    # Deterministic baseline: echo the last few lines to keep tests stable
    lines = [l for l in prompt_text.splitlines() if l.strip()]
    return "\n".join(lines[-6:])
