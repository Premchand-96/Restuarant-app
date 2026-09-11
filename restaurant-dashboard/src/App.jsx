import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { DashboardProvider, useDashboard } from './context/DashboardContext'
import Sidebar from './components/Sidebar'
import DashboardHome from './pages/DashboardHome'
import OrderManagement from './pages/OrderManagement'
import MenuManagement from './pages/MenuManagement'
import Offers from './pages/Offers'
import Reviews from './pages/Reviews'
import Earnings from './pages/Earnings'
import Login from './pages/Login'

function RequireAuth({ children }) {
  const { isAuthed } = useDashboard()
  const location = useLocation()
  if (!isAuthed) return <Navigate to="/login" state={{ from: location }} replace />
  return children
}

function Shell() {
  const location = useLocation()
  if (location.pathname === '/login') {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
      </Routes>
    )
  }

  return (
    <div style={{ display: 'flex' }}>
      <Sidebar />
      <main style={{ flex: 1, minWidth: 0 }}>
        <Routes>
          <Route path="/" element={<RequireAuth><DashboardHome /></RequireAuth>} />
          <Route path="/orders" element={<RequireAuth><OrderManagement /></RequireAuth>} />
          <Route path="/menu" element={<RequireAuth><MenuManagement /></RequireAuth>} />
          <Route path="/offers" element={<RequireAuth><Offers /></RequireAuth>} />
          <Route path="/reviews" element={<RequireAuth><Reviews /></RequireAuth>} />
          <Route path="/earnings" element={<RequireAuth><Earnings /></RequireAuth>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <DashboardProvider>
      <Shell />
    </DashboardProvider>
  )
}
