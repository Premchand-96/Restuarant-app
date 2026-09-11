import { earningsSeries } from '../data/mockData'
import { useDashboard } from '../context/DashboardContext'
import DashHeader from '../components/DashHeader'
import styles from './Earnings.module.css'

export default function Earnings() {
  const { orders } = useDashboard()
  const total = earningsSeries.reduce((s, d) => s + d.amount, 0)
  const avgOrderValue = Math.round(
    orders.filter((o) => o.status === 'completed').reduce((s, o) => s + o.total, 0) /
      Math.max(1, orders.filter((o) => o.status === 'completed').length)
  )
  const maxAmount = Math.max(...earningsSeries.map((d) => d.amount))

  return (
    <div>
      <DashHeader title="Earnings" subtitle="Payout summary and order value trends" />
      <div className={styles.content}>
        <div className={styles.summaryGrid}>
          <div className={`card ${styles.summaryCard}`}>
            <p className={styles.summaryLabel}>Last 7 days</p>
            <p className={styles.summaryValue}>₹{total.toLocaleString('en-IN')}</p>
          </div>
          <div className={`card ${styles.summaryCard}`}>
            <p className={styles.summaryLabel}>Avg. order value</p>
            <p className={styles.summaryValue}>₹{avgOrderValue}</p>
          </div>
          <div className={`card ${styles.summaryCard}`}>
            <p className={styles.summaryLabel}>Next payout</p>
            <p className={styles.summaryValue}>Fri, 12 Sep</p>
          </div>
        </div>

        <div className={`card ${styles.chartCard}`}>
          <h2 className={styles.cardTitle}>Daily earnings</h2>
          <table className={styles.table}>
            <thead>
              <tr><th>Day</th><th>Amount</th><th></th></tr>
            </thead>
            <tbody>
              {earningsSeries.map((d) => (
                <tr key={d.day}>
                  <td>{d.day}</td>
                  <td className="mono">₹{d.amount.toLocaleString('en-IN')}</td>
                  <td style={{ width: '50%' }}>
                    <div className={styles.barTrack}>
                      <div className={styles.bar} style={{ width: `${(d.amount / maxAmount) * 100}%` }} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
