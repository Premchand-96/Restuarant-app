import { NavLink, useNavigate } from 'react-router-dom'
import { useDashboard } from '../context/DashboardContext'
import styles from './Sidebar.module.css'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/orders', label: 'Orders' },
  { to: '/menu', label: 'Menu' },
  { to: '/offers', label: 'Offers' },
  { to: '/reviews', label: 'Reviews' },
  { to: '/earnings', label: 'Earnings' },
]

export default function Sidebar() {
  const { profile, toggleOpen, setIsAuthed, stats } = useDashboard()
  const navigate = useNavigate()

  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <div className={styles.logoMark}>{profile.name.split(' ').map((w) => w[0]).slice(0, 2).join('')}</div>
        <div>
          <p className={styles.brandName}>{profile.name}</p>
          <p className={styles.brandSub}>Restaurant Partner</p>
        </div>
      </div>

      <button className={styles.statusToggle} onClick={toggleOpen}>
        <span className={`${styles.statusDot} ${profile.isOpen ? styles.statusDotOpen : styles.statusDotClosed}`} />
        {profile.isOpen ? 'Open for orders' : 'Closed'}
      </button>

      <nav className={styles.nav}>
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => `${styles.navItem} ${isActive ? styles.navItemActive : ''}`}
          >
            {item.label}
            {item.to === '/orders' && stats.newCount > 0 && <span className={styles.navBadge}>{stats.newCount}</span>}
          </NavLink>
        ))}
      </nav>

      <button
        className={styles.logout}
        onClick={() => {
          setIsAuthed(false)
          navigate('/login')
        }}
      >
        Log out
      </button>
    </aside>
  )
}
