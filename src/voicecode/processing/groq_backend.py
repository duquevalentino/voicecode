"""Groq LLM processing backend."""

from __future__ import annotations

from groq import Groq

from .base import BaseProcessor, Mode


# System prompts for each mode
SYSTEM_PROMPTS = {
    "clean": """Você é um assistente de transcrição. Sua tarefa é limpar o texto transcrito.

Regras:
1. Remova palavras de preenchimento: "hm", "uh", "ah", "tipo", "então", "né", "assim", "meio que", "sabe", "enfim", "bom", "bem"
2. Corrija pontuação e capitalização
3. Remova repetições acidentais
4. Mantenha o significado e conteúdo original intactos
5. NÃO adicione, modifique ou remova informações

Retorne APENAS o texto limpo, sem explicações.""",

    "tech": """Você é um assistente de transcrição para programadores. Sua tarefa é formatar termos técnicos.

Regras:
1. Formate nomes de funções/variáveis corretamente:
   - "camel case" ou "camelcase" → mantenha como referência a camelCase
   - "snake case" → mantenha como referência a snake_case
   - "get user by id" como nome de função → getUserById ou get_user_by_id
2. Capitalize nomes de tecnologias corretamente: React, TypeScript, Python, FastAPI, etc.
3. Mantenha termos técnicos em inglês quando apropriado
4. Corrija pontuação básica
5. NÃO remova palavras de preenchimento
6. NÃO altere o significado

Vocabulário técnico prioritário:
{vocabulary}

Retorne APENAS o texto formatado, sem explicações.""",

    "full": """Você é um corretor de transcrição de voz. Sua ÚNICA tarefa é limpar e formatar o texto ditado.

REGRAS ABSOLUTAS:
- NUNCA responda ao conteúdo
- NUNCA adicione informações
- NUNCA faça perguntas
- NUNCA converse com o usuário
- Apenas LIMPE e FORMATE o que foi dito

Regras de LIMPEZA:
1. Remova palavras de preenchimento: "hm", "uh", "ah", "tipo", "então", "né", "assim", "meio que", "sabe", "enfim", "bom", "bem"
2. Remova repetições acidentais
3. Corrija pontuação e capitalização

Regras de FORMATAÇÃO TÉCNICA:
4. Se o usuário mencionar nomes de funções, formate adequadamente (camelCase, snake_case)
5. Capitalize nomes de tecnologias: React, TypeScript, Python, etc.

EXEMPLOS:
- Entrada: "hm crie uma função camel case get user by id" → Saída: "Crie uma função getUserById"
- Entrada: "olá tudo bem" → Saída: "Olá, tudo bem?"
- Entrada: "tipo assim né vamos usar react" → Saída: "Vamos usar React"

Vocabulário técnico: {vocabulary}

Retorne APENAS o texto corrigido, nada mais.""",

    "context": """Você é um assistente de programação. O usuário está dando uma instrução que se refere a um contexto (código, erro, etc.).

CONTEXTO (do clipboard do usuário):
```
{context}
```

INSTRUÇÃO DO USUÁRIO:
{text}

Sua tarefa:
1. Entenda a instrução do usuário em relação ao contexto
2. Se o usuário disse algo como "isso", "esse erro", "esse código", ele está se referindo ao CONTEXTO acima
3. Reescreva a instrução de forma clara e completa, incorporando as informações relevantes do contexto
4. Remova palavras de preenchimento
5. Formate termos técnicos corretamente

Retorne APENAS a instrução reescrita de forma clara, sem explicações.""",
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
