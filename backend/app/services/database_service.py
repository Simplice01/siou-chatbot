from typing import Any
from uuid import UUID

from psycopg import sql
from psycopg.types.json import Jsonb

from app.core.database import Database
from app.schemas.chat import ChatResponse
from app.schemas.database import (
    ConversationCreate,
    FeedbackCreate,
    OrganizationCreate,
    OrganizationUpdate,
    UserCreate,
    UserUpdate,
)
from app.models.document import DocumentChunk, PageText


class DatabaseService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def list_rows(self, table: str, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        allowed = {
            "users",
            "documents",
            "document_chunks",
            "source_files",
            "organizations",
            "service_cards",
            "conversations",
            "messages",
            "feedback_reports",
        }
        if table not in allowed:
            raise ValueError(f"Table non autorisee: {table}")
        order_columns = {
            "source_files": "collected_at",
            "document_chunks": "chunk_index",
        }
        order_column = order_columns.get(table, "created_at")
        direction = "ASC" if table == "document_chunks" else "DESC"
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("SELECT * FROM {} ORDER BY {} {} LIMIT %s OFFSET %s").format(
                        sql.Identifier(table),
                        sql.Identifier(order_column),
                        sql.SQL(direction),
                    ),
                    (limit, offset),
                )
                return list(cur.fetchall())

    def get_row(self, table: str, row_id: UUID) -> dict[str, Any] | None:
        allowed = {"users", "documents", "source_files", "organizations", "service_cards", "conversations", "feedback_reports"}
        if table not in allowed:
            raise ValueError(f"Table non autorisee: {table}")
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("SELECT * FROM {} WHERE id = %s").format(sql.Identifier(table)), (row_id,))
                return cur.fetchone()

    def list_document_chunks(self, document_id: UUID, limit: int = 100) -> list[dict[str, Any]]:
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, document_id, chunk_index, page_start, page_end, content, char_count
                    FROM document_chunks
                    WHERE document_id = %s
                    ORDER BY chunk_index
                    LIMIT %s
                    """,
                    (document_id, limit),
                )
                return list(cur.fetchall())

    def create_user(self, payload: UserCreate) -> dict[str, Any]:
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (organization_id, email, full_name, role)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                    """,
                    (payload.organization_id, payload.email, payload.full_name, payload.role),
                )
                return cur.fetchone()

    def update_user(self, user_id: UUID, payload: UserUpdate) -> dict[str, Any] | None:
        fields = payload.model_dump(exclude_unset=True)
        return self._update_row("users", user_id, fields)

    def deactivate_user(self, user_id: UUID) -> dict[str, Any] | None:
        return self._update_row("users", user_id, {"is_active": False})

    def create_conversation(self, payload: ConversationCreate) -> dict[str, Any]:
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO conversations (user_id, title, channel)
                    VALUES (%s, %s, %s)
                    RETURNING *
                    """,
                    (payload.user_id, payload.title, payload.channel),
                )
                return cur.fetchone()

    def delete_conversation(self, conversation_id: UUID) -> bool:
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))
                return cur.rowcount > 0

    def list_messages(self, conversation_id: UUID) -> list[dict[str, Any]]:
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, conversation_id, role, content, confidence_score, created_at
                    FROM messages
                    WHERE conversation_id = %s
                    ORDER BY created_at ASC
                    """,
                    (conversation_id,),
                )
                return list(cur.fetchall())

    def update_organization(self, organization_id: UUID, payload: OrganizationUpdate) -> dict[str, Any] | None:
        fields = payload.model_dump(exclude_unset=True)
        return self._update_row("organizations", organization_id, fields)

    def create_organization(self, payload: OrganizationCreate) -> dict[str, Any]:
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO organizations (name, acronym, type, description, email, phone, website)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (payload.name, payload.acronym, payload.type, payload.description, payload.email, payload.phone, payload.website),
                )
                return cur.fetchone()

    def create_feedback(self, payload: FeedbackCreate) -> dict[str, Any]:
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO feedback_reports (
                      message_id, conversation_id, reporter_user_id, organization_id, description, expected_answer
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        payload.message_id,
                        payload.conversation_id,
                        payload.reporter_user_id,
                        payload.organization_id,
                        payload.description,
                        payload.expected_answer,
                    ),
                )
                return cur.fetchone()

    def save_chat_exchange(
        self,
        question: str,
        response: ChatResponse,
        conversation_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> tuple[UUID, UUID]:
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                if conversation_id:
                    cur.execute("SELECT id FROM conversations WHERE id = %s", (conversation_id,))
                    conversation = cur.fetchone()
                else:
                    conversation = None
                if not conversation:
                    title = question.strip()[:120]
                    cur.execute(
                        """
                        INSERT INTO conversations (user_id, channel, title)
                        VALUES (%s, 'web', %s)
                        RETURNING id
                        """,
                        (user_id, title),
                    )
                    conversation_id = cur.fetchone()["id"]

                cur.execute(
                    """
                    INSERT INTO messages (conversation_id, role, content, metadata)
                    VALUES (%s, 'user', %s, %s)
                    RETURNING id
                    """,
                    (conversation_id, question, Jsonb({})),
                )
                cur.fetchone()

                cur.execute(
                    """
                    INSERT INTO messages (conversation_id, role, content, confidence_score, metadata)
                    VALUES (%s, 'assistant', %s, %s, %s)
                    RETURNING id
                    """,
                    (conversation_id, response.answer, response.confidence, Jsonb({"pages": response.pages})),
                )
                message_id = cur.fetchone()["id"]

                for source in response.sources:
                    document_id, chunk_id = self._resolve_source_ids(cur, source.document, source.chunk_id)
                    cur.execute(
                        """
                        INSERT INTO message_sources (message_id, document_id, chunk_id, page, score, citation)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (message_id, document_id, chunk_id, source.page, source.score, source.citation),
                    )
                return conversation_id, message_id

    def stats(self) -> dict[str, int]:
        tables = ["users", "documents", "document_chunks", "organizations", "service_cards", "conversations", "messages"]
        data: dict[str, int] = {}
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                for table in tables:
                    cur.execute(sql.SQL("SELECT count(*) AS total FROM {}").format(sql.Identifier(table)))
                    data[table] = cur.fetchone()["total"]
        return data

    def sync_indexed_document(
        self,
        filename: str,
        digest: str,
        size_bytes: int,
        pages: list[PageText],
        chunks: list[DocumentChunk],
    ) -> None:
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO source_files (kind, original_filename, mime_type, sha256, file_size_bytes, page_count, metadata)
                    VALUES ('pdf_officiel', %s, 'application/pdf', %s, %s, %s, %s)
                    ON CONFLICT (sha256) DO UPDATE SET
                      original_filename = EXCLUDED.original_filename,
                      file_size_bytes = EXCLUDED.file_size_bytes,
                      page_count = EXCLUDED.page_count,
                      last_seen_at = now(),
                      metadata = EXCLUDED.metadata
                    RETURNING id
                    """,
                    (
                        filename,
                        digest,
                        size_bytes,
                        len(pages),
                        Jsonb({"source": "documents_folder"}),
                    ),
                )
                source_file_id = cur.fetchone()["id"]

                raw_text = "\n\n".join(page.text for page in pages if page.text.strip())
                summary = raw_text[:600].strip() if raw_text else None
                cur.execute(
                    "DELETE FROM documents WHERE title = %s OR source_file_id = %s",
                    (filename, source_file_id),
                )
                cur.execute(
                    """
                    INSERT INTO documents (
                      source_file_id, title, type, status, summary, raw_text, normalized_text, metadata
                    )
                    VALUES (%s, %s, 'procedure', 'publie', %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        source_file_id,
                        filename,
                        summary,
                        raw_text,
                        raw_text,
                        Jsonb({"origin": "local_pdf_indexing"}),
                    ),
                )
                document_id = cur.fetchone()["id"]

                for index, chunk in enumerate(chunks):
                    cur.execute(
                        """
                        INSERT INTO document_chunks (
                          document_id, chunk_index, page_start, page_end, content, token_count, metadata
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            document_id,
                            index,
                            chunk.page_start,
                            chunk.page_end,
                            chunk.text,
                            max(1, len(chunk.text.split())),
                            Jsonb({"external_chunk_id": chunk.id, "document_slug": chunk.document_id}),
                        ),
                    )

    def _update_row(self, table: str, row_id: UUID, fields: dict[str, Any]) -> dict[str, Any] | None:
        if not fields:
            return self.get_row(table, row_id)
        allowed_tables = {"users", "organizations"}
        if table not in allowed_tables:
            raise ValueError(f"Table non modifiable: {table}")
        assignments = [sql.SQL("{} = %s").format(sql.Identifier(key)) for key in fields]
        values = list(fields.values()) + [row_id]
        query = sql.SQL("UPDATE {} SET {} WHERE id = %s RETURNING *").format(
            sql.Identifier(table),
            sql.SQL(", ").join(assignments),
        )
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
                return cur.fetchone()

    def _resolve_source_ids(self, cur: Any, filename: str, chunk_external_id: str) -> tuple[UUID | None, UUID | None]:
        cur.execute(
            """
            SELECT d.id
            FROM documents d
            LEFT JOIN source_files sf ON sf.id = d.source_file_id
            WHERE sf.original_filename = %s OR d.title = %s
            ORDER BY d.created_at DESC
            LIMIT 1
            """,
            (filename, filename),
        )
        document = cur.fetchone()
        document_id = document["id"] if document else None
        chunk_id = None
        if document_id:
            cur.execute(
                """
                SELECT id
                FROM document_chunks
                WHERE document_id = %s AND metadata->>'external_chunk_id' = %s
                LIMIT 1
                """,
                (document_id, chunk_external_id),
            )
            chunk = cur.fetchone()
            chunk_id = chunk["id"] if chunk else None
        return document_id, chunk_id
