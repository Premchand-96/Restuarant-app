import styles from './DashHeader.module.css'

export default function DashHeader({ title, subtitle, right }) {
  return (
    <header className={styles.header}>
      <div>
        <h1 className={styles.title}>{title}</h1>
        {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      </div>
      {right && <div>{right}</div>}
    </header>
  )
}
