import { describe, it, mock } from 'node:test'
import assert from 'node:assert/strict'
import React from 'react'
import ReactDOMServer from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'

import RegisterPage, { REGISTRATION_SUCCESS_MESSAGE, submitRegistration } from '../RegisterPage.jsx'
import { AuthContext } from '../../hooks/useAuth.jsx'

const render = () =>
  ReactDOMServer.renderToStaticMarkup(
    <AuthContext.Provider
      value={{
        user: null,
        token: null,
        loading: false,
        login: async () => {},
        logout: () => {},
        register: async () => {},
      }}
    >
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>
    </AuthContext.Provider>
  )

describe('RegisterPage', () => {
  it('reserves space for success announcements', () => {
    const html = render()

    assert.match(html, /role="status"/)
    assert.match(html, /aria-live="polite"/)
  })
})

describe('submitRegistration', () => {
  it('announces success and schedules a redirect when registration succeeds', async () => {
    const registerFn = mock.fn(async () => {})
    const navigate = mock.fn()
    const setError = mock.fn()
    const setSuccess = mock.fn()
    const setLoading = mock.fn()
    const scheduleRedirect = mock.fn((callback, delay) => {
      assert.equal(typeof callback, 'function')
      assert.strictEqual(delay, 1200)
      callback()
      return 42
    })

    const timerId = await submitRegistration({
      registerFn,
      email: 'teen@example.com',
      password: 'Secret123!',
      fullName: 'Test Teen',
      navigate,
      setError,
      setSuccess,
      setLoading,
      scheduleRedirect,
    })

    assert.strictEqual(timerId, 42)
    assert.strictEqual(registerFn.mock.calls.length, 1)
    assert.deepStrictEqual(registerFn.mock.calls[0].arguments, [
      'teen@example.com',
      'Secret123!',
      'Test Teen',
    ])

    assert.deepStrictEqual(setError.mock.calls.map((call) => call.arguments[0]), [''])
    assert.deepStrictEqual(setSuccess.mock.calls.map((call) => call.arguments[0]), [
      '',
      REGISTRATION_SUCCESS_MESSAGE,
    ])
    assert.deepStrictEqual(setLoading.mock.calls.map((call) => call.arguments[0]), [true, false])
    assert.strictEqual(scheduleRedirect.mock.calls.length, 1)
    assert.strictEqual(navigate.mock.calls.length, 1)
    assert.deepStrictEqual(navigate.mock.calls[0].arguments, ['/login'])
  })

  it('surfaces the error message and skips redirect when registration fails', async () => {
    const registerFn = mock.fn(async () => {
      throw new Error('Registration failed')
    })
    const navigate = mock.fn()
    const setError = mock.fn()
    const setSuccess = mock.fn()
    const setLoading = mock.fn()
    const scheduleRedirect = mock.fn()

    const timerId = await submitRegistration({
      registerFn,
      email: 'teen@example.com',
      password: 'Secret123!',
      fullName: 'Test Teen',
      navigate,
      setError,
      setSuccess,
      setLoading,
      scheduleRedirect,
    })

    assert.strictEqual(timerId, null)
    assert.deepStrictEqual(setError.mock.calls.map((call) => call.arguments[0]), [
      '',
      'Registration failed',
    ])
    assert.deepStrictEqual(setSuccess.mock.calls.map((call) => call.arguments[0]), [''])
    assert.deepStrictEqual(setLoading.mock.calls.map((call) => call.arguments[0]), [true, false])
    assert.strictEqual(scheduleRedirect.mock.calls.length, 0)
    assert.strictEqual(navigate.mock.calls.length, 0)
  })
})
