import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import React from 'react'
import ReactDOMServer from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'

import LoginPage from '../LoginPage.jsx'

const render = () =>
  ReactDOMServer.renderToStaticMarkup(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>
  )

describe('LoginPage', () => {
  it('renders the welcome copy and sign-in form fields', () => {
    const html = render()

    assert.match(html, /Welcome Back/)
    assert.match(html, /Sign in to chat about migraine care\./)
    assert.match(html, /type="email"/)
    assert.match(html, /type="password"/)
    assert.match(html, /Sign in/)
  })

  it('provides a link to create a new account', () => {
    const html = render()

    assert.match(html, /Need an account\?/)
    assert.match(html, /href="\/register"/)
    assert.match(html, />Create one<\/a>/)
  })
})
