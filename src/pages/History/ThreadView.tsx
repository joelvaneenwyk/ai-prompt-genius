import React, { useEffect, useState } from "react"
import { db, Msg, Chat } from "../../lib/historyDb"
import JSZip from "jszip"

export default function ThreadView() {
    const [threads, setThreads] = useState<Chat[]>([])

    useEffect(() => {
        db.chats.toArray().then(setThreads)
    }, [])

    const exportAll = async () => {
        const zip = new JSZip()
        for (const chat of await db.chats.toArray()) {
            const msgs = await db.messages
                .where("conversation_id")
                .equals(chat.conversation_id)
                .toArray()
            const md = msgs.map(m => `${m.author_role}: ${m.text}`).join("\n\n")
            zip.file(`${chat.title || chat.conversation_id}.md`, md)
        }
        const blob = await zip.generateAsync({ type: "blob" })
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = "chats.zip"
        a.click()
        URL.revokeObjectURL(url)
    }

    return (
        <div>
            <h2>History</h2>
            <button onClick={exportAll}>Export All (.zip)</button>
            <ul>
                {threads.map(t => (
                    <li key={t.conversation_id}>{t.title}</li>
                ))}
            </ul>
        </div>
    )
}
