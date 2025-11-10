// src/components/Bot.jsx
import { useState } from "react";
import axios from "axios";

export default function Bot() {
    const [prompt, setPrompt] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState("");

    const handleSubmit = async () => {
        if (!prompt.trim()) return;
        setLoading(true);
        setResult("");
        try {
            const res = await axios.post("http://localhost:8000/create-note", { prompt });
            setResult(res.data.result || "Note created successfully!");
        } catch (err) {
            setResult("❌ Error: " + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white shadow-lg rounded-2xl p-6 w-[600px]">
            <h1 className="text-2xl font-semibold text-gray-800 mb-4">
                🧠 Notion Note Agent
            </h1>
            <textarea
                className="w-full border border-gray-300 rounded-md p-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={6}
                placeholder="e.g. Create a note summarizing today's design review..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
            />
            <button
                onClick={handleSubmit}
                disabled={loading}
                className="mt-4 w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
            >
                {loading ? "Creating Note..." : "Create Note in Notion"}
            </button>
            {result && (
                <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-md text-gray-700">
                    {result}
                </div>
            )}
        </div>
    );
}
