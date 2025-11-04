import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './hooks/useAuth'
import ChatPage from './components/ChatPage'
import LoginPage from './components/LoginPage'
import RegisterPage from './components/RegisterPage'

const RequireAuth = ({ children }) => {
  const { user, loading } = useAuth()
  if (loading) {
    return <div className="loader">Loading...</div>
  }
  return user ? children : <Navigate to="/login" replace />
}

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route
          path="/"
          element={
            <RequireAuth>
              <ChatPage />
            </RequireAuth>
          }
        />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
