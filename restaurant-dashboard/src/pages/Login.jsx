import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDashboard } from '../context/DashboardContext'
import styles from './Login.module.css'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { setIsAuthed } = useDashboard()
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    setIsAuthed(true)
    navigate('/')
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.brand}>
          <div className={styles.logoMark}>🍽</div>
          <h1 className={styles.brandName}>Restaurant Partner Portal</h1>
          <p className={styles.tagline}>Manage your menu, orders and earnings</p>
        </div>

        <form onSubmit={handleSubmit}>
          <label className={styles.label}>Email</label>
          <input
            className={styles.input}
            type="email"
            placeholder="owner@restaurant.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <label className={styles.label}>Password</label>
          <input
            className={styles.input}
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button className="btn-primary" type="submit" style={{ width: '100%', marginTop: 8 }}>
            Log in
          </button>
        </form>

        <p className={styles.footerText}>New restaurant partner? <a href="#register">Register here</a></p>
      </div>
    </div>
  )
}
