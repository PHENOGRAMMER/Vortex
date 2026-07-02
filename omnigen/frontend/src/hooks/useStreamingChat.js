import { useEffect, useRef, useState } from "react";
import API_BASE from "../config/api";
import { SSEClient } from "../lib/sseClient";

export function useStreamingChat(token) {
    const client = useRef(null);
    const [status, setStatus] = useState("");
    const [streaming, setStreaming] = useState(false);

    async function stream(prompt, onToken) {
        setStreaming(true);
        setStatus("Connecting...");

        client.current = new SSEClient(`${API_BASE}/api/chat/stream`, token);

        try {
            await client.current.connect(
                {
                    prompt
                },
                {
                    onStatus: setStatus,

                    onToken,

                    onDone() {
                        setStreaming(false);
                        setStatus("");
                    },

                    onError() {
                        setStreaming(false);
                        setStatus("");
                    }
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

    return {

        stream,

        cancel,

        status,

        streaming
    };
}