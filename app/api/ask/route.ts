import { type NextRequest, NextResponse } from "next/server"
import { generateText } from "ai"
import { openai } from "@ai-sdk/openai"

// Simulated vector search results
const mockVectorSearch = (query: string) => {
  const mockResults = [
    {
      content:
        "Engine anomaly detection systems monitor various parameters including temperature, pressure, vibration, and fuel flow rates. Critical thresholds are defined for each parameter, and alerts are triggered when values exceed normal operating ranges.",
      metadata: {
        document: "Engine_Diagnostics_Manual_v2.1.pdf",
        page: 45,
        section: "Anomaly Detection Systems",
      },
      similarity: 0.89,
    },
    {
      content:
        "Hydraulic system pressure should maintain between 2800-3200 PSI during normal operations. Pressure drops below 2500 PSI indicate potential pump failure or system leakage requiring immediate inspection.",
      metadata: {
        document: "Hydraulic_Systems_Handbook.pdf",
        page: 78,
        section: "Pressure Monitoring",
      },
      similarity: 0.82,
    },
    {
      content:
        "Flight control surface actuators are equipped with position feedback sensors. Discrepancies between commanded and actual positions greater than 2 degrees trigger fault isolation procedures.",
      metadata: {
        document: "Flight_Control_Systems.pdf",
        page: 156,
        section: "Actuator Diagnostics",
      },
      similarity: 0.76,
    },
  ]

  // Filter results based on query relevance (simplified)
  return mockResults.filter((result) => result.similarity > 0.7).slice(0, 3)
}

export async function POST(request: NextRequest) {
  try {
    const { question } = await request.json()

    if (!question) {
      return NextResponse.json({ error: "Question is required" }, { status: 400 })
    }

    // Step 1: Perform vector search to retrieve relevant documents
    const retrievedDocs = mockVectorSearch(question)

    // Step 2: Prepare context from retrieved documents
    const context = retrievedDocs
      .map(
        (doc) => `Document: ${doc.metadata.document} (Page ${doc.metadata.page})
Content: ${doc.content}`,
      )
      .join("\n\n")

    // Step 3: Generate response using RAG
    const prompt = `You are an expert aerospace diagnostic AI assistant. Use the following retrieved documents to answer the user's question about aerospace systems, anomaly detection, or technical troubleshooting.

IMPORTANT INSTRUCTIONS:
- Base your answer primarily on the provided documents
- If the documents don't contain sufficient information, clearly state this limitation
- Provide specific technical details when available
- Include relevant safety considerations
- Be precise and professional in your response

Retrieved Documents:
${context}

User Question: ${question}

Please provide a comprehensive answer based on the retrieved documentation:`

    const { text } = await generateText({
      model: openai("gpt-4o"),
      prompt,
      maxTokens: 500,
      temperature: 0.3,
    })

    // Step 4: Format sources for frontend
    const sources = retrievedDocs.map((doc) => ({
      document: doc.metadata.document,
      page: doc.metadata.page,
      relevance: doc.similarity,
    }))

    return NextResponse.json({
      answer: text,
      sources,
      retrievedChunks: retrievedDocs.length,
    })
  } catch (error) {
    console.error("Error in /api/ask:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
