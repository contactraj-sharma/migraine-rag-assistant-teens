import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export const REGISTRATION_SUCCESS_MESSAGE =
  'Account created! Redirecting you to sign in…'

export const submitRegistration = async ({
  registerFn,
  email,
  password,
  fullName,
  navigate,
  setError,
  setSuccess,
  setLoading,
  scheduleRedirect = (callback, delay) => setTimeout(callback, delay),
  redirectDelayMs = 1200,
}) => {
  setError('')
  setSuccess('')
  setLoading(true)
  try {
    await registerFn(email, password, fullName)
    setSuccess(REGISTRATION_SUCCESS_MESSAGE)
    return scheduleRedirect(() => navigate('/login'), redirectDelayMs)
  } catch (error) {
    const message = error?.message || 'Registration failed'
    setError(message)
    return null
  } finally {
    setLoading(false)
  }
}

const RegisterPage = () => {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const redirectTimer = useRef(null)

  const handleSubmit = async (event) => {
    event.preventDefault()
    const timerId = await submitRegistration({
      registerFn: register,
      email,
      password,
      fullName,
      navigate,
      setError,
      setSuccess,
      setLoading,
      scheduleRedirect: (callback, delay) => {
        if (redirectTimer.current) {
          clearTimeout(redirectTimer.current)
        }
        redirectTimer.current = setTimeout(callback, delay)
        return redirectTimer.current
      },
    })
    if (!timerId) {
      redirectTimer.current = null
    }
  }

  useEffect(() => {
    return () => {
      if (redirectTimer.current) {
        clearTimeout(redirectTimer.current)
      }
    }
  }, [])

  return (
    <div className="auth-page">
      <form className="card" onSubmit={handleSubmit}>
        <h1>Create your account</h1>
        <p className="muted">Join to get supportive migraine guidance for teens.</p>
        <label>
          Full name
          <input value={fullName} onChange={(event) => setFullName(event.target.value)} required />
        </label>
        <label>
          Email
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        </label>
        <p className="success" role="status" aria-live="polite">
          {success}
        </p>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" disabled={loading}>
          {loading ? 'Creating account…' : 'Create account'}
        </button>
        <p className="muted">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </form>
    </div>
  )
}

export default RegisterPage
