import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import React from 'react'
import ReactDOMServer from 'react-dom/server'

import ChatPage from '../ChatPage.jsx'
import { AuthContext } from '../../hooks/useAuth.jsx'

const renderWithAuth = () =>
  ReactDOMServer.renderToStaticMarkup(
    <AuthContext.Provider
      value={{
        user: { full_name: 'Taylor' },
        token: 'test-token',
        loading: false,
        login: async () => {},
        register: async () => {},
        logout: () => {},
      }}
    >
      <ChatPage />
    </AuthContext.Provider>
  )

describe('ChatPage', () => {
  it('greets the signed-in teen and shows the initial assistant message', () => {
    const html = renderWithAuth()

    assert.match(html, /Migraine RAG Assistant/)
    assert.match(html, /Welcome, Taylor/)
    assert.match(
      html,
      /Hi there! I am here to help answer your migraine questions in a teen-friendly way\./
    )
  })

  it('encourages asking questions and highlights the context panel', () => {
    const html = renderWithAuth()

    assert.match(html, /Key Facts Used/)
    assert.match(html, /Ask a question to see supporting details\./)
    assert.match(html, /Ask about migraine care, triggers, or ways to feel better/)
    assert.match(html, />Log out<\/button>/)
  })
})
