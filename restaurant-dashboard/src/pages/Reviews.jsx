import { useDashboard } from '../context/DashboardContext'
import { reviews } from '../data/mockData'
import DashHeader from '../components/DashHeader'
import styles from './Reviews.module.css'

export default function Reviews() {
  const { profile } = useDashboard()
  const avg = (reviews.reduce((s, r) => s + r.rating, 0) / reviews.length).toFixed(1)

  return (
    <div>
      <DashHeader title="Reviews" subtitle={`${reviews.length} reviews · ${avg} average rating`} />
      <div className={styles.content}>
        <div className={styles.list}>
          {reviews.map((r) => (
            <div key={r.id} className={`card ${styles.reviewCard}`}>
              <div className={styles.reviewTop}>
                <p className={styles.customerName}>{r.customerName}</p>
                <span className={styles.stars}>{'★'.repeat(r.rating)}{'☆'.repeat(5 - r.rating)}</span>
              </div>
              <p className={styles.comment}>{r.comment}</p>
              <p className={styles.date}>{new Date(r.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
