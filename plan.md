# ⧈ Plan — Restore Local Chat History & Export to *ai-prompt-genius* ⧉

> Version V0.1 · 2025-05-31

Bring back the missing **auto-save every ChatGPT conversation + exporter** capability (last seen in early 2023).

## Prerequisites

* **Node 18+** – [download](https://nodejs.org/)
* **npm**
* **Edge / Chrome (Chromium)** – [Edge](https://www.microsoft.com/edge) for quickest testing
* **Python 3.10+** – only if you already use `main.py` launcher

## 1 Install Project Deps

```bash
npm install
npm install dexie lodash-es      # IndexedDB wrapper + debounce util
```

*Docs:* [Dexie](https://dexie.org/docs)  |  [lodash-es on npm](https://www.npmjs.com/package/lodash-es)

## 2 IndexedDB Schema

**src/lib/historyDb.ts**

```typescript
import Dexie, { Table } from 'dexie';

export interface Chat {
  conversation_id: string;
  title: string;
  updated: number;
}
export interface Msg {
  id?: number;
  conversation_id: string;
  author_role: 'user' | 'assistant';
  text: string;
  create_time: number;
}

class HistoryDB extends Dexie {
  chats!: Table<Chat, string>;
  messages!: Table<Msg, number>;
  constructor() {
    super('chatgpt');
    this.version(1).stores({
      chats: 'conversation_id, updated',
      messages: '++id, conversation_id, create_time',
    });
  }
}
export const db = new HistoryDB();
```

*Legacy reference:* [`db.ts` (2023 fork)](https://github.com/davgit/ChatGPT-Prompt-Genius/blob/master/src/lib/db.ts)

> **Codex hint:** “Generate Vitest tests for `HistoryDB` insert & lookup.”

## 3 Recorder Content Script

**src/contentScripts/historyRecorder.ts** (modernised from 2023 code)

```typescript
import { db } from '../lib/historyDb';
import debounce from 'lodash-es/debounce';

const persist = debounce(async (el: HTMLElement) => {
  const role   = el.dataset.messageAuthorRole as 'user' | 'assistant';
  const convId = window.location.pathname.split('/').pop()!;
  await db.messages.add({
    conversation_id: convId,
    author_role: role,
    text: el.innerText.trim(),
    create_time: Date.now(),
  });
  await db.chats.put({
    conversation_id: convId,
    title: document.title.replace('ChatGPT – ', ''),
    updated: Date.now(),
  });
}, 500);

new MutationObserver(m =>
  m.forEach(mut => persist(mut.target as HTMLElement)),
).observe(document.body, { childList: true, subtree: true });
```

*Original inspiration:* [`chatRecorder.ts`](https://raw.githubusercontent.com/davgit/ChatGPT-Prompt-Genius/master/src/contentScript/chatRecorder.ts)

## 4 Patch `manifest.json`

```jsonc
"content_scripts": [
  {
    "matches": ["https://chat.openai.com/*"],
    "js": ["contentScripts/historyRecorder.js"],
    "run_at": "document_idle"
  }
],
"permissions": ["storage"]
```

## 5 History UI & Export

1. Copy view:
   *`src/pages/History/ThreadView.tsx`* ← [`ThreadView.tsx` raw](https://raw.githubusercontent.com/davgit/ChatGPT-Prompt-Genius/master/src/pages/thread/ThreadView.tsx)
2. Add a **History** route in `App.tsx` sidebar.

3. Install **JSZip** (`npm install jszip`) for an **Export All (.zip)** button.
   *Docs:* [JSZip site](https://stuk.github.io/jszip/)

## 6 Build & Lint

```bash
npm run lint
npm run build        # emits historyRecorder.js into dist/
```

## 7 Local Verification

1. `npm run build`
2. `python main.py` – launches Edge with unpacked extension (`dist/`).
3. Open [chat.openai.com](https://chat.openai.com), send a message.
4. In the browser, visit `chrome://indexeddb-internals` and check **chatgpt** DB rows.
5. Go to **History** page → list threads → click **Export** → verify Markdown / PDF / ZIP.

## 8 Optional CI

Add to `.github/workflows/ci.yml`

```yaml
- run: npm run vitest         # unit tests
- run: npm run build          # ensure recorder compiles
```

## 9 Docs Update

**README.md**

```
### Local Chat History (Revived)
• Auto-saves every ChatGPT message to IndexedDB
• History view with per-thread export (Markdown, PDF)
• Bulk “Export All (.zip)” powered by JSZip
```

*(Also add bullet in CHANGELOG.md under “Unreleased”.)*

### Quick Resources

* Legacy fork with full history logic – <https://github.com/davgit/ChatGPT-Prompt-Genius>
* Chrome IndexedDB viewer – type **chrome://indexeddb-internals** in address bar
* Dexie React guide – <https://dexie.org/docs/Tutorial/React>

**Done.** Build + launch and your extension once again records every ChatGPT conversation for easy archival.
