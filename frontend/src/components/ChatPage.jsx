import { useEffect, useRef, useState } from 'react'
import { useAuth } from '../hooks/useAuth'

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

const MessageBubble = ({ role, text }) => (
  <div className={`message ${role}`}>
    <div className="bubble">
      <p>{text}</p>
    </div>
  </div>
)

const ContextCard = ({ title, content, score }) => (
  <div className="context-card">
    <h4>{title}</h4>
    {typeof score === 'number' && <p className="muted">Relevance: {(score * 100).toFixed(0)}%</p>}
    <p>{content}</p>
  </div>
)

const ChatPage = () => {
  const { user, token, logout } = useAuth()
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Hi there! I am here to help answer your migraine questions in a teen-friendly way. Ask me anything!',
    },
  ])
  const [contexts, setContexts] = useState([])
  const [loading, setLoading] = useState(false)
  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!question.trim()) return

    const userMessage = { role: 'user', text: question }
    setMessages((prev) => [...prev, userMessage])
    setLoading(true)

    try {
      const res = await fetch(`${API_BASE}/chat/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question }),
      })
      if (!res.ok) {
        throw new Error('Unable to get answer')
      }
      const data = await res.json()
      setMessages((prev) => [...prev, { role: 'assistant', text: data.answer }])
      setContexts(
        data.context.map((snippet, index) => ({
          title: snippet.title ?? `Source ${index + 1}`,
          content: snippet.content,
          score: snippet.score,
        }))
      )
    } catch (error) {
      console.error(error)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: 'Sorry, I had trouble reaching the assistant. Please try again in a moment.',
        },
      ])
    } finally {
      setLoading(false)
      setQuestion('')
    }
  }

  return (
    <div className="page">
      <aside className="sidebar">
        <h2>Migraine RAG Assistant</h2>
        <p className="welcome">Welcome, {user?.full_name ?? user?.email}</p>
        <button className="secondary" onClick={logout}>
          Log out
        </button>
        <div className="context-panel">
          <h3>Key Facts Used</h3>
          {contexts.length === 0 && <p className="muted">Ask a question to see supporting details.</p>}
          {contexts.map((context, index) => (
            <ContextCard
              key={`${context.title}-${index}`}
              title={context.title}
              content={context.content}
              score={context.score}
            />
          ))}
        </div>
      </aside>
      <main className="chat-panel">
        <div className="messages">
          {messages.map((message, index) => (
            <MessageBubble key={`${message.role}-${index}`} role={message.role} text={message.text} />
          ))}
          <div ref={chatEndRef} />
        </div>
        <form className="chat-input" onSubmit={handleSubmit}>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about migraine care, triggers, or ways to feel better..."
            rows={3}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Thinking...' : 'Ask'}
          </button>
        </form>
      </main>
    </div>
  )
}

export default ChatPage
