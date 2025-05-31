import { db } from "../lib/historyDb"
import debounce from "lodash-es/debounce"

const persist = debounce(async (el: HTMLElement) => {
    const role = el.dataset.messageAuthorRole as "user" | "assistant"
    const convId = window.location.pathname.split("/").pop()!
    await db.messages.add({
        conversation_id: convId,
        author_role: role,
        text: el.innerText.trim(),
        create_time: Date.now(),
    })
    await db.chats.put({
        conversation_id: convId,
        title: document.title.replace("ChatGPT – ", ""),
        updated: Date.now(),
    })
}, 500)

new MutationObserver(m => m.forEach(mut => persist(mut.target as HTMLElement))).observe(
    document.body,
    { childList: true, subtree: true },
)
