import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Send, FileText, Loader2, Shield } from "lucide-react";
import { toast } from "sonner";
import { z } from "zod";
import { marked } from "marked";

interface Message {
    role: "user" | "assistant";
    content: string;
    sources?: any[];
}

// Input validation schema
const querySchema = z.object({
    query: z.string()
        .trim()
        .min(1, "Question cannot be empty")
        .max(1000, "Question must be less than 1000 characters"),
    k: z.number().int().min(1).max(20).optional()
});

// Backend configuration
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

// Configure marked options
marked.setOptions({
    breaks: true,
    gfm: true,
});

const LegalAssistant = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesContainerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (messagesContainerRef.current) {
            messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
        }
    }, [messages, isLoading]);

    const handleSend = async () => {
        if (!input.trim()) return;

        // Validate input
        try {
            querySchema.parse({ query: input, k: 8 });
        } catch (error) {
            if (error instanceof z.ZodError) {
                toast.error(error.errors[0].message);
                return;
            }
        }

        const userMessage: Message = { role: "user", content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const response = await fetch(`${BACKEND_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: input, k: 8 }),
            });

            if (!response.ok) {
                throw new Error(`Backend error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();

            const assistantMessage: Message = {
                role: "assistant",
                content: data.answer || data.response || "Sorry, I couldn't generate a response.",
                sources: data.sources || []
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error("Error:", error);
            toast.error("Backend connection failed. Ensure Python server is running.");

            setMessages(prev => prev.slice(0, -1));
            setInput(input);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <section id="legal-assistant" className="min-h-screen py-12 px-6 md:px-12 lg:px-16 bg-gradient-hero relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute inset-0 bg-gradient-to-b from-secondary/5 via-transparent to-accent/5"></div>
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl"></div>

            <div className="w-full relative z-10">
                <div className="text-center mb-12 space-y-4">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary/20 border border-secondary/30 backdrop-blur-sm mb-4">
                        <FileText className="w-4 h-4 text-secondary" />
                        <span className="text-sm font-medium text-primary-foreground">Legal AI Chat</span>
                    </div>
                    <h2 className="text-3xl md:text-4xl font-bold text-primary-foreground">
                        Ask Your Legal Questions
                    </h2>
                    <p className="text-sm text-primary-foreground/70 max-w-2xl mx-auto">
                        Get instant answers powered by AI trained on Nepali legal domain
                    </p>
                </div>

                <Card id="chat-input" className="w-full shadow-elevated bg-primary/30 backdrop-blur-2xl border-primary-foreground/10 overflow-hidden">
                    <CardHeader className="border-b border-primary-foreground/10 bg-primary/20 backdrop-blur-sm">
                        <CardTitle className="flex items-center gap-3 text-primary-foreground">
                            <div className="p-2 rounded-lg bg-secondary/30">
                                <FileText className="w-5 h-5 text-secondary" />
                            </div>
                            <div>
                                <div className="text-lg">AI Legal Assistant</div>
                                <div className="text-sm font-normal text-primary-foreground/70">Trained on Nepali Legal Domain</div>
                            </div>
                        </CardTitle>
                    </CardHeader>

                    <CardContent className="p-0">
                        <div ref={messagesContainerRef} className="h-[550px] overflow-y-auto p-8 space-y-6 bg-primary/20 backdrop-blur-sm">
                            {messages.map((message, index) => (
                                <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}>
                                    <div
                                        className={`max-w-[85%] rounded-2xl px-6 py-4 shadow-card ${message.role === "user"
                                            ? "bg-gradient-accent text-accent-foreground shadow-glow"
                                            : "bg-primary/40 border border-primary-foreground/20 text-primary-foreground backdrop-blur-md"
                                            }`}
                                    >
                                        {/* Assistant message */}
                                        {message.role === "assistant" ? (
                                            <div>
                                                <div
                                                    className="markdown-response prose prose-sm max-w-none prose-invert"
                                                    dangerouslySetInnerHTML={{
                                                        __html: marked.parse(message.content) as string
                                                    }}
                                                />

                                                {/* Retrieved Sources Section */}
                                                {message.sources && message.sources.length > 0 && (
                                                    <details className="group mt-6 bg-primary/40 backdrop-blur-md border border-primary-foreground/20 rounded-xl overflow-hidden shadow-card transition-all hover:shadow-elevated">
                                                        <summary className="cursor-pointer px-5 py-3.5 flex items-center gap-3 bg-primary/20 hover:bg-primary/30 transition-colors">
                                                            <FileText className="w-4 h-4 text-secondary shrink-0" />
                                                            <span className="font-semibold text-sm text-secondary">Retrieved Sources</span>
                                                            <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-secondary/20 text-secondary">
                                                                {message.sources.length}
                                                            </span>
                                                        </summary>

                                                        <div className="px-5 py-4 space-y-3 bg-primary/20">
                                                            {message.sources.map((src, i) => {
                                                                const part = src.part_number;
                                                                const article = src.article_number;

                                                                let locationParts = [];
                                                                if (part) locationParts.push(`Part ${part}` + (src.part_title ? ` – ${src.part_title}` : ""));
                                                                if (article) locationParts.push(`Article ${article}` + (src.article_title ? `: ${src.article_title}` : ""));
                                                                if (src.clause_index !== undefined) locationParts.push(`Clause ${src.clause_index}`);

                                                                return (
                                                                    <div
                                                                        key={i}
                                                                        className="bg-primary/30 backdrop-blur-sm border border-primary-foreground/10 rounded-lg p-4 hover:border-secondary/30 transition-all animate-fade-in"
                                                                        style={{ animationDelay: `${i * 50}ms` }}
                                                                    >
                                                                        <div className="flex items-start gap-2 mb-2">
                                                                            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-secondary/20 text-secondary text-xs font-bold shrink-0">
                                                                                {i + 1}
                                                                            </span>
                                                                            <div className="flex-1 min-w-0">
                                                                                <h4 className="font-semibold text-sm text-primary-foreground truncate">
                                                                                    {src.document_title || "Unnamed Document"}
                                                                                </h4>
                                                                                {locationParts.length > 0 && (
                                                                                    <p className="text-xs text-primary-foreground/60 mt-0.5">
                                                                                        {locationParts.join(" • ")}
                                                                                    </p>
                                                                                )}
                                                                            </div>
                                                                        </div>

                                                                        <blockquote className="mt-3 pl-3 border-l-2 border-secondary/40 text-sm text-primary-foreground/80 leading-relaxed">
                                                                            {src.text}
                                                                        </blockquote>
                                                                    </div>
                                                                );
                                                            })}
                                                        </div>
                                                    </details>
                                                )}
                                            </div>
                                        ) : (
                                            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                                        )}
                                    </div>
                                </div>
                            ))}

                            {isLoading && (
                                <div className="flex justify-start animate-fade-in">
                                    <div className="bg-primary/40 border border-primary-foreground/20 backdrop-blur-md rounded-2xl px-6 py-4 flex items-center gap-3 shadow-card">
                                        <Loader2 className="w-5 h-5 animate-spin text-secondary" />
                                        <p className="text-sm text-primary-foreground">Analyzing your question...</p>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="border-t border-primary-foreground/10 p-6 bg-primary/20 backdrop-blur-sm">
                            <div className="flex gap-3">
                                <Textarea
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === "Enter" && !e.shiftKey) {
                                            e.preventDefault();
                                            handleSend();
                                        }
                                    }}
                                    placeholder="Type your legal question here..."
                                    className="min-h-[70px] resize-none bg-primary-foreground/10 border-primary-foreground/20 text-primary-foreground placeholder:text-primary-foreground/50 focus:border-secondary/50 focus:ring-secondary/20 transition-all"
                                />
                                <Button
                                    onClick={handleSend}
                                    disabled={isLoading || !input.trim()}
                                    className="shrink-0 bg-gradient-accent hover:shadow-glow hover:scale-105 transition-all px-6 shadow-card"
                                >
                                    <Send className="w-5 h-5" />
                                </Button>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </section>
    );
};

export default LegalAssistant;
