import Dexie, { Table } from "dexie"

export interface Chat {
    conversation_id: string
    title: string
    updated: number
}

export interface Msg {
    id?: number
    conversation_id: string
    author_role: "user" | "assistant"
    text: string
    create_time: number
}

class HistoryDB extends Dexie {
    chats!: Table<Chat, string>
    messages!: Table<Msg, number>
    constructor() {
        super("chatgpt")
        this.version(1).stores({
            chats: "conversation_id, updated",
            messages: "++id, conversation_id, create_time",
        })
    }
}

export const db = new HistoryDB()
