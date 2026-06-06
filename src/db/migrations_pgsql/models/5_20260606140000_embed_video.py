# RSSFunBot
# https://github.com/mathewskdaniel/RSSFunBot

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "embed_video" SMALLINT NOT NULL  DEFAULT 1;
        ALTER TABLE "sub" ADD "embed_video" SMALLINT NOT NULL  DEFAULT -100;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "sub" DROP COLUMN "embed_video";
        ALTER TABLE "user" DROP COLUMN "embed_video";"""
