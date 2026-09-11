import { useDashboard } from '../context/DashboardContext'
import { earningsSeries } from '../data/mockData'
import DashHeader from '../components/DashHeader'
import styles from './DashboardHome.module.css'

export default function DashboardHome() {
  const { stats, orders } = useDashboard()
  const recent = orders.slice(0, 5)
  const maxAmount = Math.max(...earningsSeries.map((d) => d.amount))

  return (
    <div>
      <DashHeader title="Dashboard" subtitle="Today's snapshot for your restaurant" />
      <div className={styles.content}>
        <div className={styles.statGrid}>
          <div className={`card ${styles.statCard}`}>
            <p className={styles.statLabel}>New orders</p>
            <p className={styles.statValue}>{stats.newCount}</p>
          </div>
          <div className={`card ${styles.statCard}`}>
            <p className={styles.statLabel}>Preparing</p>
            <p className={styles.statValue}>{stats.preparingCount}</p>
          </div>
          <div className={`card ${styles.statCard}`}>
            <p className={styles.statLabel}>Completed</p>
            <p className={styles.statValue}>{stats.completedCount}</p>
          </div>
          <div className={`card ${styles.statCard}`}>
            <p className={styles.statLabel}>Revenue (completed)</p>
            <p className={styles.statValue}>₹{stats.totalRevenue.toLocaleString('en-IN')}</p>
          </div>
        </div>

        <div className={styles.row}>
          <div className={`card ${styles.chartCard}`}>
            <h2 className={styles.cardTitle}>Earnings — last 7 days</h2>
            <div className={styles.chart}>
              {earningsSeries.map((d) => (
                <div key={d.day} className={styles.barCol}>
                  <div className={styles.barTrack}>
                    <div
                      className={styles.bar}
                      style={{ height: `${(d.amount / maxAmount) * 100}%` }}
                      title={`₹${d.amount}`}
                    />
                  </div>
                  <span className={styles.barLabel}>{d.day}</span>
                </div>
              ))}
            </div>
          </div>

          <div className={`card ${styles.recentCard}`}>
            <h2 className={styles.cardTitle}>Recent orders</h2>
            <div className={styles.recentList}>
              {recent.map((o) => (
                <div key={o.id} className={styles.recentRow}>
                  <div>
                    <p className={styles.recentId}>{o.id}</p>
                    <p className={styles.recentCustomer}>{o.customerName}</p>
                  </div>
                  <div className={styles.recentRight}>
                    <p className={styles.recentAmount}>₹{o.total}</p>
                    <span className={`${styles.statusPill} ${styles['status_' + o.status]}`}>{o.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
