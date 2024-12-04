import { useState, useEffect } from "react";

function OutputBox() {
    const [output, setOutput] = useState("");

    useEffect(() => {
        const eventSource = new EventSource("http://192.168.1.10:40100");
        eventSource.onmessage = event => {
            setOutput(prevOutput => prevOutput + "\n" + event.data);
        };

        return () => {
            eventSource.close();
        };
    }, []);

    return (
        <div style={{ border: "1px solid black", padding: "10px", height: "200px", overflowY: "scroll" }}>
            <pre>{output}</pre>
        </div>
    );
}

export default OutputBox;
