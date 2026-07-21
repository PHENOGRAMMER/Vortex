export class SSEClient {
    constructor(url, token = null) {
        this.url = url;
        this.token = token;
        this.controller = null;
    }

    async connect(body, handlers) {
        this.controller = new AbortController();

        const response = await fetch(this.url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...(this.token && {
                    Authorization: `Bearer ${this.token}`
                })
            },
            body: JSON.stringify(body),
            signal: this.controller.signal
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            const events = buffer.split("\n\n");

            buffer = events.pop();

            for (const event of events) {

                if (!event.trim()) continue;

                const lines = event.split("\n");

                let payload = "";

                for (const line of lines) {
                    if (line.startsWith("data:")) {
                        payload += line.slice(5).trim();
                    }
                }

                if (!payload) continue;

                const message = JSON.parse(payload);

                handlers?.onEvent?.(message);

                switch (message.type) {

                    case "token":
                        handlers?.onToken?.(message.data.content);
                        break;

                    case "status":
                        handlers?.onStatus?.(message.data.message);
                        break;

                    case "done":
                        handlers?.onDone?.();
                        return;

                    case "error":
                        handlers?.onError?.(message.data.message);
                        throw new Error(message.data.message || "Stream error");
                }
            }
        }
    }

    disconnect() {
        this.controller?.abort();
    }
}