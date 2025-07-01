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
