from app.models.document import DocumentChunk


class PromptService:
    def build(self, question: str, contexts: list[tuple[DocumentChunk, float]]) -> list[dict[str, str]]:
        context_text = "\n\n".join(
            f"[Source {idx} | page {chunk.page_start} | score {score:.3f}]\n{chunk.text}"
            for idx, (chunk, score) in enumerate(contexts, start=1)
        )
        system = (
            "Tu es SIOU, un agent d'orientation institutionnelle pour aider un agent d'accueil ou une secretaire "
            "a orienter rapidement un usager vers la bonne direction, agence, procedure, adresse, contact ou evenement. "
            "Tu ne realises pas la demarche a la place de l'usager: tu l'orientes. "
            "Tu dois repondre uniquement a partir des extraits fournis. N'utilise jamais tes connaissances externes. "
            "Si l'information demandee n'est pas explicitement presente, reponds clairement que l'information est absente "
            "des documents disponibles. Reponds en francais, de facon courte, fiable et exploitable au guichet."
        )
        user = (
            f"Question:\n{question}\n\n"
            f"Extraits autorisés:\n{context_text}\n\n"
            "Produit une reponse structuree si les informations existent:\n"
            "- Orientation: que doit faire l'usager.\n"
            "- Structure competente: direction, agence ou service concerne.\n"
            "- Adresse / contact / horaires: uniquement si present dans les extraits.\n"
            "- Informations utiles: procedure, condition ou evenement pertinent.\n"
            "Ne donne que les informations directement utiles pour repondre a la question posee. "
            "Ne cite pas de source inexistante et n'invente aucune adresse, date ou contact."
        )
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]
