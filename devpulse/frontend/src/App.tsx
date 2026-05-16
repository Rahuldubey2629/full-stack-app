import { Navigate, Route, Routes } from 'react-router-dom'

import { getAccessToken } from '@/api/client'
import DashboardPage from '@/pages/Dashboard'
import LoginPage from '@/pages/Login'
import NewIncidentPage from '@/pages/NewIncident'
import RetrospectivePage from '@/pages/Retrospective'

function RequireAuth({ children }: { children: JSX.Element }) {
  const token = getAccessToken()
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <div className="min-h-full bg-gray-50 text-gray-900">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <RequireAuth>
              <Navigate to="/dashboard" replace />
            </RequireAuth>
          }
        />
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <DashboardPage />
            </RequireAuth>
          }
        />
        <Route
          path="/incidents/new"
          element={
            <RequireAuth>
              <NewIncidentPage />
            </RequireAuth>
          }
        />
        <Route
          path="/retro/:retroId"
          element={
            <RequireAuth>
              <RetrospectivePage />
            </RequireAuth>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}
