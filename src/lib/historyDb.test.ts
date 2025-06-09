import { describe, expect, it, beforeEach } from "vitest"
import { db } from "./historyDb"

beforeEach(async () => {
    await db.delete()
})

describe("HistoryDB", () => {
    it("inserts and retrieves messages", async () => {
        await db.messages.add({
            conversation_id: "1",
            author_role: "user",
            text: "hi",
            create_time: Date.now(),
        })
        const msgs = await db.messages.where("conversation_id").equals("1").toArray()
        expect(msgs.length).toBe(1)
        expect(msgs[0].text).toBe("hi")
    })

    it("stores chat metadata", async () => {
        await db.chats.put({
            conversation_id: "c1",
            title: "Test",
            updated: Date.now(),
        })
        const chat = await db.chats.get("c1")
        expect(chat?.title).toBe("Test")
    })
})
