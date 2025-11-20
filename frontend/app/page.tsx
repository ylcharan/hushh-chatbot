"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import {
  MessageSquare,
  Database,
  Settings,
  Plus,
  Trash2,
  Send,
  Menu,
  X,
  FileText,
  Globe,
  Upload,
} from "lucide-react";

interface Message {
  id: string;
  user_message: string;
  bot_response: string;
  context_used?: any[];
  created_at: string;
}

interface KnowledgeEntry {
  id: string;
  title: string;
  content: string;
  category: string;
  source_type?: string;
  source_url?: string;
  metadata?: any;
  created_at: string;
  updated_at: string;
}

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>("Checking...");
  const [sessionId, setSessionId] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"chat" | "settings">("chat");
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

  // Knowledge base state
  const [knowledge, setKnowledge] = useState<KnowledgeEntry[]>([]);
  const [newKnowledgeTitle, setNewKnowledgeTitle] = useState<string>("");
  const [newKnowledgeContent, setNewKnowledgeContent] = useState<string>("");
  const [newKnowledgeCategory, setNewKnowledgeCategory] =
    useState<string>("general");
  const [knowledgeSheetOpen, setKnowledgeSheetOpen] = useState<boolean>(false);

  // Scraper state
  const [sourceType, setSourceType] = useState<"text" | "url" | "file">("text");
  const [urlInput, setUrlInput] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    // Check backend health
    fetch("http://localhost:5001/api/health")
      .then((res) => res.json())
      .then((data) => {
        setBackendStatus(`Connected - ${data.service}`);
      })
      .catch((err) => {
        setBackendStatus("Backend not running");
        toast({
          variant: "destructive",
          title: "Backend Connection Error",
          description: "Failed to connect to the backend server.",
        });
        console.error("Backend connection error:", err);
      });

    // Create a new session
    createSession();

    // Load knowledge base
    loadKnowledge();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const createSession = async () => {
    try {
      const response = await fetch("http://localhost:5001/api/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const result = await response.json();
      if (result.success) {
        setSessionId(result.session_id);
      }
    } catch (err) {
      console.error("Error creating session:", err);
      toast({
        variant: "destructive",
        title: "Session Error",
        description: "Failed to create a new session.",
      });
    }
  };

  const sendMessage = async () => {
    if (!userInput.trim() || isLoading) return;

    const currentMessage = userInput;
    setUserInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:5001/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: currentMessage,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No response body");
      }

      let streamedResponse = "";
      let contextUsed: any[] = [];
      let timestamp = new Date().toISOString();
      const tempMessageId = Date.now().toString();

      // Add a temporary message with empty response
      const tempMessage: Message = {
        id: tempMessageId,
        user_message: currentMessage,
        bot_response: "",
        context_used: [],
        created_at: timestamp,
      };
      setMessages((prev) => [...prev, tempMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === "init") {
                contextUsed = data.context || [];
                if (data.session_id) {
                  setSessionId(data.session_id);
                }
              } else if (data.type === "content") {
                streamedResponse += data.content;
                // Add a small delay for smoother streaming
                await new Promise((resolve) => setTimeout(resolve, 20));
                // Update the message in real-time
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === tempMessageId
                      ? {
                          ...msg,
                          bot_response: streamedResponse,
                          context_used: contextUsed,
                        }
                      : msg
                  )
                );
              } else if (data.type === "done") {
                timestamp = data.timestamp || timestamp;
              } else if (data.type === "error") {
                console.error("Streaming error:", data.error);
                streamedResponse =
                  "Sorry, an error occurred while generating the response.";
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === tempMessageId
                      ? { ...msg, bot_response: streamedResponse }
                      : msg
                  )
                );
                toast({
                  variant: "destructive",
                  title: "Streaming Error",
                  description: data.error,
                });
              }
            } catch (e) {
              console.error("Error parsing SSE data:", e);
            }
          }
        }
      }
    } catch (err) {
      console.error("Error sending message:", err);
      toast({
        variant: "destructive",
        title: "Message Error",
        description: "Failed to send your message. Please try again.",
      });
      // Add error message
      const errorMessage: Message = {
        id: Date.now().toString(),
        user_message: currentMessage,
        bot_response:
          "Sorry, an error occurred while sending your message. Please try again.",
        context_used: [],
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadKnowledge = async () => {
    try {
      const response = await fetch("http://localhost:5001/api/knowledge");
      const result = await response.json();
      if (result.success) {
        setKnowledge(result.knowledge);
      }
    } catch (err) {
      console.error("Error loading knowledge:", err);
      toast({
        variant: "destructive",
        title: "Knowledge Load Error",
        description: "Failed to load knowledge base entries.",
      });
    }
  };

  const addKnowledge = async () => {
    setIsProcessing(true);

    try {
      if (sourceType === "text") {
        // Text content
        if (!newKnowledgeContent.trim()) {
          toast({
            variant: "destructive",
            title: "Validation Error",
            description: "Please enter text content.",
          });
          setIsProcessing(false);
          return;
        }

        const response = await fetch("http://localhost:5001/api/scraper/text", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            content: newKnowledgeContent,
            title: newKnowledgeTitle || undefined,
            category: newKnowledgeCategory,
          }),
        });

        const result = await response.json();

        if (result.success) {
          toast({
            title: "Success",
            description: "Text content added successfully!",
          });
          resetForm();
          loadKnowledge();
        } else {
          throw new Error(result.error);
        }
      } else if (sourceType === "url") {
        // URL scraping
        if (!urlInput.trim()) {
          toast({
            variant: "destructive",
            title: "Validation Error",
            description: "Please enter a URL.",
          });
          setIsProcessing(false);
          return;
        }

        const response = await fetch("http://localhost:5001/api/scraper/url", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url: urlInput,
            category: newKnowledgeCategory,
            max_depth: 0,
            extract_links: false,
          }),
        });

        const result = await response.json();

        if (result.success) {
          toast({
            title: "Success",
            description: `Successfully scraped and added ${result.count} page(s)!`,
          });
          resetForm();
          loadKnowledge();
        } else {
          throw new Error(result.error);
        }
      } else if (sourceType === "file") {
        // File upload
        if (!selectedFile) {
          toast({
            variant: "destructive",
            title: "Validation Error",
            description: "Please select a file.",
          });
          setIsProcessing(false);
          return;
        }

        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("category", newKnowledgeCategory);
        if (newKnowledgeTitle) {
          formData.append("title", newKnowledgeTitle);
        }

        const response = await fetch("http://localhost:5001/api/scraper/file", {
          method: "POST",
          body: formData,
        });

        const result = await response.json();

        if (result.success) {
          toast({
            title: "Success",
            description: `File "${result.filename}" processed successfully!`,
          });
          resetForm();
          loadKnowledge();
        } else {
          throw new Error(result.error);
        }
      }
    } catch (err: any) {
      console.error("Error adding knowledge:", err);
      toast({
        variant: "destructive",
        title: "Error",
        description: err.message || "Failed to add knowledge entry.",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const resetForm = () => {
    setNewKnowledgeTitle("");
    setNewKnowledgeContent("");
    setNewKnowledgeCategory("general");
    setUrlInput("");
    setSelectedFile(null);
  };

  const deleteKnowledge = async (id: string) => {
    try {
      const response = await fetch(
        `http://localhost:5001/api/knowledge/${id}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (result.success) {
        toast({
          title: "Success",
          description: "Knowledge entry deleted successfully.",
        });
        loadKnowledge();
      }
    } catch (err) {
      console.error("Error deleting knowledge:", err);
      toast({
        variant: "destructive",
        title: "Delete Error",
        description: "Failed to delete knowledge entry.",
      });
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 text-white transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}
      >
        <div className="flex flex-col h-full">
          {/* Logo/Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-800">
            <h1 className="text-xl font-bold">Hushh AI</h1>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-gray-400 hover:text-white"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            <button
              onClick={() => setActiveTab("chat")}
              className={`flex items-center gap-3 w-full px-4 py-3 rounded-lg transition-colors ${
                activeTab === "chat"
                  ? "bg-gray-800 text-white"
                  : "text-gray-400 hover:bg-gray-800 hover:text-white"
              }`}
            >
              <MessageSquare className="h-5 w-5" />
              <span>Chat</span>
            </button>

            <button
              onClick={() => setActiveTab("settings")}
              className={`flex items-center gap-3 w-full px-4 py-3 rounded-lg transition-colors ${
                activeTab === "settings"
                  ? "bg-gray-800 text-white"
                  : "text-gray-400 hover:bg-gray-800 hover:text-white"
              }`}
            >
              <Settings className="h-5 w-5" />
              <span>Settings</span>
            </button>
          </nav>

          {/* Status Footer */}
          <div className="p-4 border-t border-gray-800">
            <div className="flex items-center gap-2">
              <div
                className={`h-2 w-2 rounded-full ${
                  backendStatus.includes("Connected")
                    ? "bg-green-500"
                    : "bg-red-500"
                }`}
              />
              <span className="text-xs text-gray-400">{backendStatus}</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-gray-600 hover:text-gray-900"
              >
                <Menu className="h-6 w-6" />
              </button>
              <h2 className="text-2xl font-bold text-gray-900">
                {activeTab === "chat" ? "Chat" : "Settings"}
              </h2>
            </div>
            <div>
              <Sheet
                open={knowledgeSheetOpen}
                onOpenChange={setKnowledgeSheetOpen}
              >
                <SheetTrigger asChild>
                  <Button variant="outline" className="flex items-center gap-2">
                    <Database className="h-4 w-4" />
                    <span>Knowledge Base</span>
                  </Button>
                </SheetTrigger>
                <SheetContent className="w-full sm:max-w-xl">
                  <SheetHeader>
                    <SheetTitle>Knowledge Base</SheetTitle>
                    <SheetDescription>
                      Manage your knowledge base entries
                    </SheetDescription>
                  </SheetHeader>

                  <div className="mt-6 space-y-6">
                    {/* Add Knowledge Form */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Add Knowledge</CardTitle>
                        <CardDescription>
                          Add new information from text, URL, or file
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        {/* Source Type Tabs */}
                        <div className="flex gap-2 mb-4">
                          <Button
                            variant={
                              sourceType === "text" ? "default" : "outline"
                            }
                            size="sm"
                            onClick={() => setSourceType("text")}
                            className="flex-1"
                          >
                            <FileText className="h-4 w-4 mr-2" />
                            Text
                          </Button>
                          <Button
                            variant={
                              sourceType === "url" ? "default" : "outline"
                            }
                            size="sm"
                            onClick={() => setSourceType("url")}
                            className="flex-1"
                          >
                            <Globe className="h-4 w-4 mr-2" />
                            URL
                          </Button>
                          <Button
                            variant={
                              sourceType === "file" ? "default" : "outline"
                            }
                            size="sm"
                            onClick={() => setSourceType("file")}
                            className="flex-1"
                          >
                            <Upload className="h-4 w-4 mr-2" />
                            File
                          </Button>
                        </div>

                        {/* Text Input */}
                        {sourceType === "text" && (
                          <>
                            <div>
                              <label className="text-sm font-medium mb-2 block">
                                Title (Optional)
                              </label>
                              <Input
                                placeholder="Enter title or leave blank for auto-generation..."
                                value={newKnowledgeTitle}
                                onChange={(e) =>
                                  setNewKnowledgeTitle(e.target.value)
                                }
                              />
                            </div>
                            <div>
                              <label className="text-sm font-medium mb-2 block">
                                Content
                              </label>
                              <Textarea
                                placeholder="Enter text content..."
                                value={newKnowledgeContent}
                                onChange={(e) =>
                                  setNewKnowledgeContent(e.target.value)
                                }
                                rows={6}
                              />
                            </div>
                          </>
                        )}

                        {/* URL Input */}
                        {sourceType === "url" && (
                          <div>
                            <label className="text-sm font-medium mb-2 block">
                              Website URL
                            </label>
                            <Input
                              placeholder="https://example.com/page"
                              value={urlInput}
                              onChange={(e) => setUrlInput(e.target.value)}
                              type="url"
                            />
                            <p className="text-xs text-gray-500 mt-1">
                              Enter a URL to scrape content from a website
                            </p>
                          </div>
                        )}

                        {/* File Upload */}
                        {sourceType === "file" && (
                          <>
                            <div>
                              <label className="text-sm font-medium mb-2 block">
                                Upload File
                              </label>
                              <Input
                                type="file"
                                onChange={(e) =>
                                  setSelectedFile(e.target.files?.[0] || null)
                                }
                                accept=".txt,.md,.pdf,.docx,.doc,.csv,.json,.py,.js,.java,.cpp,.c,.html,.css"
                              />
                              <p className="text-xs text-gray-500 mt-1">
                                Supported: PDF, DOCX, TXT, CSV, JSON, Code files
                              </p>
                              {selectedFile && (
                                <p className="text-sm text-gray-700 mt-2">
                                  Selected: {selectedFile.name}
                                </p>
                              )}
                            </div>
                            <div>
                              <label className="text-sm font-medium mb-2 block">
                                Title (Optional)
                              </label>
                              <Input
                                placeholder="Override filename as title..."
                                value={newKnowledgeTitle}
                                onChange={(e) =>
                                  setNewKnowledgeTitle(e.target.value)
                                }
                              />
                            </div>
                          </>
                        )}

                        {/* Category (common for all types) */}
                        <div>
                          <label className="text-sm font-medium mb-2 block">
                            Category
                          </label>
                          <Input
                            placeholder="e.g., general, technical, faq..."
                            value={newKnowledgeCategory}
                            onChange={(e) =>
                              setNewKnowledgeCategory(e.target.value)
                            }
                          />
                        </div>

                        {/* Submit Button */}
                        <Button
                          onClick={addKnowledge}
                          className="w-full"
                          disabled={isProcessing}
                        >
                          {isProcessing ? (
                            <>Processing...</>
                          ) : (
                            <>
                              <Plus className="h-4 w-4 mr-2" />
                              Add to Knowledge Base
                            </>
                          )}
                        </Button>
                      </CardContent>
                    </Card>

                    {/* Knowledge List */}
                    <div>
                      <h3 className="text-lg font-semibold mb-3">
                        Entries ({knowledge.length})
                      </h3>
                      <ScrollArea className="h-[400px] pr-4">
                        <div className="space-y-3">
                          {knowledge.length === 0 ? (
                            <p className="text-center text-gray-500 py-8">
                              No knowledge entries yet. Add your first entry
                              above!
                            </p>
                          ) : (
                            knowledge.map((item) => (
                              <Card key={item.id}>
                                <CardContent className="p-4">
                                  <div className="flex justify-between items-start mb-2">
                                    <div className="flex-1">
                                      <h4 className="font-semibold text-base mb-1">
                                        {item.title}
                                      </h4>
                                      <div className="flex gap-2 flex-wrap">
                                        <Badge variant="outline">
                                          {item.category}
                                        </Badge>
                                        {item.source_type && (
                                          <Badge
                                            variant="secondary"
                                            className="flex items-center gap-1"
                                          >
                                            {item.source_type === "text" && (
                                              <FileText className="h-3 w-3" />
                                            )}
                                            {item.source_type === "url" && (
                                              <Globe className="h-3 w-3" />
                                            )}
                                            {item.source_type === "file" && (
                                              <Upload className="h-3 w-3" />
                                            )}
                                            {item.source_type}
                                          </Badge>
                                        )}
                                      </div>
                                    </div>
                                    <Button
                                      variant="destructive"
                                      size="sm"
                                      onClick={() => deleteKnowledge(item.id)}
                                    >
                                      <Trash2 className="h-4 w-4" />
                                    </Button>
                                  </div>
                                  <p className="text-sm text-gray-700 mb-2 line-clamp-3">
                                    {item.content}
                                  </p>
                                  {item.source_url && (
                                    <p className="text-xs text-blue-600 mb-1 truncate">
                                      Source: {item.source_url}
                                    </p>
                                  )}
                                  <p className="text-xs text-gray-500">
                                    Added:{" "}
                                    {new Date(
                                      item.created_at
                                    ).toLocaleDateString()}
                                  </p>
                                </CardContent>
                              </Card>
                            ))
                          )}
                        </div>
                      </ScrollArea>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-auto p-6">
          {activeTab === "chat" && (
            <div className="max-w-5xl mx-auto h-full flex flex-col">
              <Card className="flex-1 flex flex-col">
                <CardHeader>
                  <CardTitle>AI Assistant</CardTitle>
                  <CardDescription>
                    Ask questions based on your knowledge base
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col">
                  {/* Chat Messages */}
                  <ScrollArea className="flex-1 pr-4 mb-4">
                    <div className="space-y-4 min-h-[400px]">
                      {messages.length === 0 && !isLoading ? (
                        <div className="flex items-center justify-center h-full text-center text-gray-500">
                          <div>
                            <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                            <p className="text-lg font-medium">
                              No messages yet
                            </p>
                            <p className="text-sm">
                              Start a conversation by typing a message below
                            </p>
                          </div>
                        </div>
                      ) : (
                        <>
                          {messages.map((msg) => (
                            <div key={msg.id} className="space-y-3">
                              {/* User Message */}
                              <div className="flex justify-end">
                                <div className="bg-gray-900 text-white rounded-lg px-4 py-2 max-w-[70%]">
                                  <p className="text-sm">{msg.user_message}</p>
                                </div>
                              </div>

                              {/* Bot Response */}
                              <div className="flex justify-start">
                                <div className="bg-gray-100 text-gray-900 rounded-lg px-4 py-2 max-w-[70%]">
                                  <p className="text-sm whitespace-pre-wrap">
                                    {msg.bot_response}
                                    {isLoading &&
                                      messages[messages.length - 1]?.id ===
                                        msg.id && (
                                        <span className="blinking-cursor">
                                          |
                                        </span>
                                      )}
                                  </p>
                                  {msg.context_used &&
                                    msg.context_used.length > 0 && (
                                      <div className="mt-2 pt-2 border-t border-gray-300">
                                        <p className="text-xs text-gray-600 mb-1">
                                          Sources:
                                        </p>
                                        <div className="flex flex-wrap gap-1">
                                          {msg.context_used.map((ctx, idx) => (
                                            <Badge
                                              key={idx}
                                              variant="secondary"
                                              className="text-xs"
                                            >
                                              {ctx.title}
                                            </Badge>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </>
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                  </ScrollArea>

                  <Separator className="mb-4" />

                  {/* Input Area */}
                  <div className="flex gap-2">
                    <Input
                      placeholder="Type your message..."
                      value={userInput}
                      onChange={(e) => setUserInput(e.target.value)}
                      onKeyDown={(e) =>
                        e.key === "Enter" && !e.shiftKey && sendMessage()
                      }
                      disabled={isLoading}
                      className="flex-1"
                    />
                    <Button
                      onClick={sendMessage}
                      disabled={isLoading || !userInput.trim()}
                      size="lg"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === "settings" && (
            <div className="max-w-3xl mx-auto space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>General Settings</CardTitle>
                  <CardDescription>
                    Configure your chatbot preferences
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      Session ID
                    </label>
                    <Input value={sessionId} disabled />
                    <p className="text-xs text-gray-500 mt-1">
                      Your current chat session identifier
                    </p>
                  </div>
                  <Separator />
                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      Backend Status
                    </label>
                    <div className="flex items-center gap-2">
                      <div
                        className={`h-3 w-3 rounded-full ${
                          backendStatus.includes("Connected")
                            ? "bg-green-500"
                            : "bg-red-500"
                        }`}
                      />
                      <span className="text-sm">{backendStatus}</span>
                    </div>
                  </div>
                  <Separator />
                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      Knowledge Base Entries
                    </label>
                    <p className="text-2xl font-bold">{knowledge.length}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Total entries in your knowledge base
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>About</CardTitle>
                  <CardDescription>
                    Information about this application
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700">
                    Hushh AI is an AI-powered knowledge base chatbot that uses
                    Retrieval-Augmented Generation to provide accurate answers
                    based on your custom knowledge base.
                  </p>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
