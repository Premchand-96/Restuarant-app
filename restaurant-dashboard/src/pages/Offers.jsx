import { useDashboard } from '../context/DashboardContext'
import DashHeader from '../components/DashHeader'
import styles from './Offers.module.css'

export default function Offers() {
  const { offers, toggleOffer } = useDashboard()

  return (
    <div>
      <DashHeader title="Offers" subtitle="Discounts and promotions visible to customers" />
      <div className={styles.content}>
        <div className={styles.list}>
          {offers.map((offer) => (
            <div key={offer.id} className={`card ${styles.offerCard}`}>
              <div>
                <p className={styles.offerTitle}>{offer.title}</p>
                <p className={styles.offerMeta}>Code <span className="mono">{offer.code}</span> · Min order ₹{offer.minOrder}</p>
              </div>
              <label className={styles.switch}>
                <input type="checkbox" checked={offer.active} onChange={() => toggleOffer(offer.id)} />
                <span className={styles.slider} />
              </label>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
