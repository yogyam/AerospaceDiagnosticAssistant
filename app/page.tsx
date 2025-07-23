"use client"

import { useState, useRef, FormEvent, ChangeEvent } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import DocumentUpload from "./components/document-upload"
import ChatMessage from "./components/chat-message"

interface Message {
  role: "user" | "assistant"
  content: string
  sources?: any[]
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage: Message = { role: "user", content: input }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer,
        sources: data.sources,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An unknown error occurred"
      setError(errorMessage)
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Sorry, I encountered an error: ${errorMessage}`,
        },
      ])
    } finally {
      setIsLoading(false)
      setInput("")
    }
  }

  const handleFileUpload = async (file: File) => {
    setIsUploading(true)
    setUploadStatus("Uploading and processing document...")
    setError(null)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "File upload failed")
      }

      const result = await response.json()
      setUploadStatus(
        `Successfully processed ${result.filename}. Chunks: ${result.chunks}, Embeddings: ${result.embeddings}.`,
      )
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An unknown error occurred"
      setError(errorMessage)
      setUploadStatus(`Error: ${errorMessage}`)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Left Panel: Document Upload */}
      <div className="w-1/4 border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-xl font-bold">Document AI</h2>
          <p className="text-sm text-gray-400">Upload technical manuals for analysis</p>
        </div>
        <div className="p-4 flex-grow">
          <DocumentUpload onFileUpload={handleFileUpload} isUploading={isUploading} />
          {uploadStatus && (
            <div className="mt-4 p-3 bg-gray-800 rounded-lg">
              <h3 className="font-semibold">Processing Status</h3>
              <p className={`text-sm ${error ? "text-red-400" : "text-green-400"}`}>
                {uploadStatus}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Right Panel: Chat Interface */}
      <div className="w-3/4 flex flex-col">
        <header className="p-4 border-b border-gray-700 flex justify-between items-center">
          <h1 className="text-xl font-bold">Aerospace Diagnostic Assistant</h1>
          <Badge variant="outline" className="border-green-500 text-green-500">
            Online
          </Badge>
        </header>

        <ScrollArea className="flex-grow p-4">
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500">
                <p>Ask a question about your uploaded documents.</p>
                <p className="text-sm">
                  e.g., "What are the pressure limits for the hydraulic system?"
                </p>
              </div>
            )}
            {messages.map((msg, i) => (
              <ChatMessage key={i} message={msg} />
            ))}
          </div>
        </ScrollArea>

        <div className="p-4 border-t border-gray-700">
          <form onSubmit={handleSubmit} className="flex items-center space-x-2">
            <Input
              value={input}
              onChange={handleInputChange}
              placeholder="Type your question here..."
              className="flex-grow bg-gray-800 border-gray-600"
              disabled={isLoading}
            />
            <Button type="submit" disabled={isLoading || isUploading}>
              {isLoading ? "Thinking..." : "Ask"}
            </Button>
          </form>
          {error && !uploadStatus && <p className="text-red-400 text-sm mt-2">{error}</p>}
        </div>
      </div>
    </div>
  )
}
