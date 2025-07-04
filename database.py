import aiosqlite

class Database:
    def __init__(self, db_path="messages.db"):
        self.db_path = db_path
        self.conn: aiosqlite.Connection = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS message_counts (
                guild_id TEXT,
                user_id TEXT,
                message_count INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            );
        """)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS snipes (
                channel_id TEXT PRIMARY KEY,
                message_id TEXT,
                author_id TEXT,
                author_name TEXT,
                content TEXT,
                created_at REAL,
                attachments TEXT,
                reply_author TEXT,
                reply_content TEXT,
                reply_channel_id TEXT,
                reply_message_id TEXT
            );
        """)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS edit_snipes (
                channel_id TEXT PRIMARY KEY,
                message_id TEXT,
                author_id TEXT,
                author_name TEXT,
                before_content TEXT,
                after_content TEXT,
                created_at REAL,
                edited_at REAL,
                attachments TEXT,
                reply_author TEXT,
                reply_content TEXT,
                reply_channel_id TEXT,
                reply_message_id TEXT
            );
        """)
        await self.conn.commit()

        # Attempt to add new columns for reply jump information if they don't exist
        for table in ("snipes", "edit_snipes"):
            try:
                await self.conn.execute(f"ALTER TABLE {table} ADD COLUMN reply_channel_id TEXT")
            except aiosqlite.OperationalError:
                pass
            try:
                await self.conn.execute(f"ALTER TABLE {table} ADD COLUMN reply_message_id TEXT")
            except aiosqlite.OperationalError:
                pass
        await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def increment_message_count(self, guild_id, user_id):
        await self.conn.execute("""
            INSERT INTO message_counts (guild_id, user_id, message_count)
            VALUES (?, ?, 1)
            ON CONFLICT(guild_id, user_id)
            DO UPDATE SET message_count = message_count + 1;
        """, (guild_id, user_id))
        await self.conn.commit()

    async def get_leaderboard(self, guild_id, limit=10):
        cursor = await self.conn.execute("""
            SELECT user_id, message_count
            FROM message_counts
            WHERE guild_id = ?
            ORDER BY message_count DESC
            LIMIT ?;
        """, (guild_id, limit))
        rows = await cursor.fetchall()
        await cursor.close()
        return rows

    async def store_snipe(
        self,
        channel_id: str,
        message_id: str,
        author_id: str,
        author_name: str,
        content: str,
        created_at: float,
        attachments: str,
        reply_author: str | None,
        reply_content: str | None,
        reply_channel_id: str | None,
        reply_message_id: str | None,
    ):
        await self.conn.execute(
            """
            INSERT INTO snipes (
                channel_id, message_id, author_id, author_name,
                content, created_at, attachments, reply_author,
                reply_content, reply_channel_id, reply_message_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(channel_id) DO UPDATE SET
                message_id=excluded.message_id,
                author_id=excluded.author_id,
                author_name=excluded.author_name,
                content=excluded.content,
                created_at=excluded.created_at,
                attachments=excluded.attachments,
                reply_author=excluded.reply_author,
                reply_content=excluded.reply_content,
                reply_channel_id=excluded.reply_channel_id,
                reply_message_id=excluded.reply_message_id;
            """,
            (
                channel_id,
                message_id,
                author_id,
                author_name,
                content,
                created_at,
                attachments,
                reply_author,
                reply_content,
                reply_channel_id,
                reply_message_id,
            ),
        )
        await self.conn.commit()

    async def get_snipe(self, channel_id: str):
        cursor = await self.conn.execute(
            """
            SELECT message_id, author_id, author_name, content,
                   created_at, attachments, reply_author, reply_content,
                   reply_channel_id, reply_message_id
            FROM snipes WHERE channel_id = ?;
            """,
            (channel_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        return row

    async def store_edit_snipe(
        self,
        channel_id: str,
        message_id: str,
        author_id: str,
        author_name: str,
        before_content: str,
        after_content: str,
        created_at: float,
        edited_at: float,
        attachments: str,
        reply_author: str | None,
        reply_content: str | None,
        reply_channel_id: str | None,
        reply_message_id: str | None,
    ):
        await self.conn.execute(
            """
            INSERT INTO edit_snipes (
                channel_id, message_id, author_id, author_name,
                before_content, after_content, created_at, edited_at,
                attachments, reply_author, reply_content,
                reply_channel_id, reply_message_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(channel_id) DO UPDATE SET
                message_id=excluded.message_id,
                author_id=excluded.author_id,
                author_name=excluded.author_name,
                before_content=excluded.before_content,
                after_content=excluded.after_content,
                created_at=excluded.created_at,
                edited_at=excluded.edited_at,
                attachments=excluded.attachments,
                reply_author=excluded.reply_author,
                reply_content=excluded.reply_content,
                reply_channel_id=excluded.reply_channel_id,
                reply_message_id=excluded.reply_message_id;
            """,
            (
                channel_id,
                message_id,
                author_id,
                author_name,
                before_content,
                after_content,
                created_at,
                edited_at,
                attachments,
                reply_author,
                reply_content,
                reply_channel_id,
                reply_message_id,
            ),
        )
        await self.conn.commit()

    async def get_edit_snipe(self, channel_id: str):
        cursor = await self.conn.execute(
            """
            SELECT message_id, author_id, author_name, before_content,
                   after_content, created_at, edited_at, attachments,
                   reply_author, reply_content, reply_channel_id,
                   reply_message_id
            FROM edit_snipes WHERE channel_id = ?;
            """,
            (channel_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        return row
