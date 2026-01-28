"""Groq LLM processing backend."""

from __future__ import annotations

from groq import Groq

from .base import BaseProcessor, Mode


# System prompts for each mode
SYSTEM_PROMPTS = {
    "clean": """Limpe o texto removendo palavras de preenchimento.

Remova: "hm", "uh", "ah", "tipo", "então", "né", "assim", "meio que", "sabe", "enfim", "bom", "bem"
Corrija pontuação. Mantenha o significado.

PROIBIDO: NÃO escreva introduções como "Aqui está" ou "O texto limpo é". Responda SOMENTE com o texto limpo.

Texto:""",

    "tech": """Formate termos técnicos no texto.

Regras:
- Nomes de funções: getUserById, get_user_by_id
- Tecnologias: React, TypeScript, Python, FastAPI
- Vocabulário: {vocabulary}

PROIBIDO: NÃO escreva introduções. Responda SOMENTE com o texto formatado.

Texto:""",

    "full": """Corrija o texto mantendo o MESMO IDIOMA do original.

REGRAS:
1. Remova: "hm", "uh", "ah", "tipo", "então", "né", "assim", "sabe", "enfim"
2. Corrija pontuação
3. Formate termos técnicos: React, TypeScript, Python, camelCase
4. MANTENHA O IDIOMA ORIGINAL (português fica português, inglês fica inglês)

PROIBIDO:
- NÃO traduza
- NÃO adicione introduções
- NÃO explique
- Retorne SOMENTE o texto corrigido

Texto:""",

    "context": """Reescreva a instrução incorporando o contexto.

CONTEXTO:
```
{context}
```

INSTRUÇÃO: {text}

Reescreva a instrução de forma clara, substituindo "isso/esse erro/esse código" pelo conteúdo relevante do contexto.

PROIBIDO: NÃO escreva introduções. Responda SOMENTE com a instrução reescrita.""",
}


class GroqProcessor(BaseProcessor):
    """
    Text processing using Groq LLM API.

    Processes transcribed text according to the selected mode:
    - raw: No processing (passthrough)
    - clean: Remove filler words, fix punctuation
    - tech: Format technical terms
    - full: Clean + Tech combined
    """

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-8b-instant",
    ):
        """
        Initialize the Groq processor.

        Args:
            api_key: Groq API key
            model: LLM model to use
        """
        self.api_key = api_key
        self.model = model
        self._client: Groq | None = None

    def _get_client(self) -> Groq:
        """Get or create Groq client."""
        if self._client is None:
            self._client = Groq(api_key=self.api_key)
        return self._client

    def process(
        self,
        text: str,
        mode: Mode,
        vocabulary: list[str] | None = None,
        context: str | None = None,
    ) -> str:
        """
        Process text according to mode.

        Args:
            text: Raw transcribed text
            mode: Processing mode
            vocabulary: Custom vocabulary terms
            context: Optional context from clipboard

        Returns:
            Processed text
        """
        if not text:
            return ""

        # Raw mode - no processing
        if mode == "raw":
            return text

        # If context is provided, use context mode
        if context:
            return self._process_with_context(text, context, vocabulary)

        # Get appropriate system prompt
        system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["full"])

        # Format vocabulary into prompt
        vocab_str = ", ".join(vocabulary) if vocabulary else "N/A"
        system_prompt = system_prompt.format(vocabulary=vocab_str)

        return self._call_llm(system_prompt, text)

    def _process_with_context(
        self,
        text: str,
        context: str,
        vocabulary: list[str] | None = None,
    ) -> str:
        """Process text with context injection."""
        system_prompt = SYSTEM_PROMPTS["context"].format(
            context=context[:2000],  # Limit context size
            text=text,
        )

        # For context mode, the instruction is already in the system prompt
        return self._call_llm(system_prompt, "Reescreva a instrução de forma clara.")

    def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """Call Groq LLM API."""
        client = self._get_client()

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,  # Low temperature for consistent output
                max_tokens=1024,
            )

            result = response.choices[0].message.content
            return result.strip() if result else ""

        except Exception as e:
            raise ProcessingError(f"Groq processing failed: {e}") from e

    def is_available(self) -> bool:
        """Check if Groq API is available."""
        return bool(self.api_key)


class ProcessingError(Exception):
    """Error during text processing."""
    pass
