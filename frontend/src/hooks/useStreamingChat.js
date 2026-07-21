import { useEffect, useRef, useState } from "react";
import API_BASE from "../config/api";
import { SSEClient } from "../lib/sseClient";

export function useStreamingChat(token) {
    const client = useRef(null);
    const [status, setStatus] = useState("");
    const [streaming, setStreaming] = useState(false);

    /**
     * @param {string} prompt - The user's message
     * @param {function} onToken - Called with each streamed token string
     * @param {Array} history - Prior conversation messages [{role, content}]
     */
    async function stream(prompt, onToken, history = []) {
        setStreaming(true);
        setStatus("Connecting...");

        client.current = new SSEClient(`${API_BASE}/api/chat/stream`, token);

        try {
            await client.current.connect(
                { prompt, history },
                {
                    onStatus: setStatus,
                    onToken,
                    onDone() {
                        setStreaming(false);
                        setStatus("");
                    },
                    onError(msg) {
                        setStreaming(false);
                        setStatus("");
                        throw new Error(msg || "Stream error");
                    },
                }
            );
        } catch (err) {
            setStreaming(false);
            setStatus("");
            throw err;
        }
    }

    function cancel() {
        client.current?.disconnect();
        setStreaming(false);
        setStatus("");
    }

    useEffect(() => {
        return () => {
            client.current?.disconnect();
        };
    }, []);

    return { stream, cancel, status, streaming };
}
