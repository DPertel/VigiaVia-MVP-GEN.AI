import re
import unicodedata


PROBLEM_TYPES = {
    "buraco": ["buraco", "cratera"],
    "pavimento danificado": [
        "pavimento", "asfalto", "rachadura", "afundamento",
        "via quebrada", "via danificada"
    ],
    "sinalização danificada": [
        "sinalizacao", "placa", "semaforo", "faixa apagada"
    ],
    "obstrução da via": [
        "obstrucao", "entulho", "arvore caída", "bloqueio"
    ],
}


def normalize(text):
    text = unicodedata.normalize("NFD", str(text).lower())
    text = "".join(
        c for c in text if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", text).strip()


def detect_problem(text):
    normalized = normalize(text)
    for problem, terms in PROBLEM_TYPES.items():
        if any(normalize(term) in normalized for term in terms):
            return problem
    return None


def next_question(report):
    if not report.get("problem"):
        return (
            "Qual problema você encontrou? Por exemplo: buraco, "
            "rachadura, asfalto danificado ou sinalização quebrada."
        )
    if not report.get("location") or not re.search(
        r"\b(?:rua|avenida|av\.|travessa|rodovia|estrada)\b",
        report.get("location", ""),
        flags=re.IGNORECASE
    ):
        return "Onde fica o problema? Informe rua, número, bairro e cidade, se souber."
    if not report.get("description"):
        return (
            "Pode descrever melhor o problema? Informe tamanho, "
            "profundidade ou condição da via, se souber."
        )
    if not report.get("risk"):
        return (
            "O problema oferece algum risco para motoristas, "
            "motociclistas, ciclistas ou pedestres?"
        )
    return None


def create_report_message(report):
    fields = [
        ("Problema", report.get("problem")),
        ("Localização", report.get("location")),
        ("Descrição", report.get("description")),
        ("Risco informado", report.get("risk")),
    ]

    lines = ["RELATO DE PROBLEMA VIÁRIO", ""]
    for label, value in fields:
        lines.append(f"{label}: {value or 'Não informado'}")

    lines.extend([
        "",
        "Este relato foi organizado pelo VigiaIA com base nas informações fornecidas.",
        "Revise os dados antes de encaminhá-lo ao órgão responsável.",
        "O VigiaIA não realizou o envio à prefeitura."
    ])
    return "\n".join(lines)


def process_report(message, report=None):
    allowed_fields = {"problem", "location", "description", "risk"}
    report = {
        key: str(value).strip()
        for key, value in (report or {}).items()
        if key in allowed_fields and isinstance(value, str) and value.strip()
    }

    message = str(message).strip()
    normalized = normalize(message)
    previous_question = next_question(report)

    # Identifica o problema, inclusive expressões como "via quebrada".
    if previous_question and previous_question.startswith("Qual problema"):
        detected = detect_problem(message)
        if detected:
            report["problem"] = detected

    # Coleta a localização. Permite informar cidade e rua em mensagens separadas.
    if previous_question and previous_question.startswith("Onde fica"):
        if not report.get("location"):
            report["location"] = message
        elif normalize(message) not in normalize(report["location"]):
            report["location"] += " - " + message

    # Também identifica uma rua mencionada espontaneamente na mensagem.
    street_match = re.search(
        r"(?:rua|avenida|av\.|travessa|rodovia|estrada)\s+[^,.;]+",
        message,
        flags=re.IGNORECASE
    )
    if street_match:
        street = street_match.group(0).strip()
        if not report.get("location"):
            report["location"] = street
        elif normalize(street) not in normalize(report["location"]):
            report["location"] += " - " + street

    # Coleta a descrição quando essa foi a pergunta anterior.
    if previous_question and previous_question.startswith("Pode descrever"):
        report["description"] = message

    # Interpreta respostas afirmativas, negativas ou descritivas sobre risco.
    if previous_question and previous_question.startswith("O problema oferece"):
        negative_answers = {
            "nao", "não", "nao oferece risco", "não oferece risco",
            "sem risco", "nenhum risco", "nao tem risco", "não tem risco"
        }
        positive_answers = {
            "sim", "sim oferece risco", "sim, oferece risco",
            "sim ha risco", "sim, há risco"
        }

        if normalized in {normalize(item) for item in negative_answers}:
            report["risk"] = "Nenhum risco identificado pelo cidadão."
        elif normalized in {normalize(item) for item in positive_answers}:
            report["risk"] = "O cidadão informou que há risco."
        else:
            report["risk"] = message

    question = next_question(report)

    if question:
        return {
            "answer": question,
            "completed": False,
            "report": report
        }

    return {
        "answer": (
            "Consegui organizar as informações. Confira o relato abaixo:\n\n"
            + create_report_message(report)
        ),
        "completed": True,
        "report": report
    }
