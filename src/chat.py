from .llm import generate


def answer_chat_question(question, mode, engine):
    result = engine.ask(question, mode)

    if not result.get("abstained"):
        return result

    prompt = f"""
Você é o assistente conversacional VigiaIA, especializado em mobilidade urbana.

A documentação consultada não contém evidências suficientes para responder
à pergunta do usuário.

Sua tarefa é oferecer uma explicação de conhecimento geral, quando possível.

REGRAS OBRIGATÓRIAS:
- Responda em português brasileiro.
- Seja claro, didático e objetivo.
- Não invente características, funcionalidades ou decisões internas do projeto VigiaVia ou VigiaIA.
- Se a pergunta pedir detalhes específicos desses projetos, informe que eles não foram confirmados na documentação.
- Você pode explicar conceitos gerais de mobilidade urbana, inteligência artificial,
  visão computacional, zeladoria urbana e tecnologias relacionadas.
- Diferencie explicitamente conhecimento geral de informações documentadas.
- Se não souber responder com segurança, admita a limitação.
- Não invente fontes, citações, números ou referências.
- Não afirme que consultou documentos que não foram encontrados.

PERGUNTA DO USUÁRIO:
{question}

Responda somente com o texto da explicação.
"""

    try:
        fallback = generate(prompt, temperature=0.2)
    except Exception:
        fallback = ""

    if not fallback.strip():
        return {
            **result,
            "fallback_available": False,
            "rationale": (
                "A documentação não contém informação suficiente e "
                "não foi possível obter uma resposta alternativa do modelo local."
            )
        }

    return {
        **result,
        "answer": (
            "Não encontrei confirmação dessa informação na documentação "
            "do VigiaVia. A seguir, apresento uma explicação de conhecimento "
            "geral, que não deve ser interpretada como uma descrição "
            "confirmada da implementação do projeto:\n\n"
            + fallback.strip()
        ),
        "citations": [],
        "abstained": False,
        "fallback": True,
        "verified_by_kb": False,
        "rationale": (
            "Resposta elaborada pelo modelo local com conhecimento geral; "
            "não confirmada pela base documental."
        )
    }
