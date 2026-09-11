import { useState } from 'react'
import { useDashboard } from '../context/DashboardContext'
import { ORDER_STATUS_FLOW } from '../data/mockData'
import DashHeader from '../components/DashHeader'
import styles from './OrderManagement.module.css'

const COLUMNS = [
  { key: 'new', label: 'New' },
  { key: 'preparing', label: 'Preparing' },
  { key: 'ready', label: 'Ready for pickup' },
  { key: 'completed', label: 'Completed' },
]

const ACTION_LABELS = {
  preparing: 'Accept',
  ready: 'Mark ready',
  completed: 'Mark picked up',
  rejected: 'Reject',
}

export default function OrderManagement() {
  const { orders, updateOrderStatus } = useDashboard()
  const [tab, setTab] = useState('board')

  return (
    <div>
      <DashHeader
        title="Orders"
        subtitle="Manage incoming and in-progress orders"
        right={
          <div className={styles.tabs}>
            <button className={`${styles.tabBtn} ${tab === 'board' ? styles.tabBtnActive : ''}`} onClick={() => setTab('board')}>Board</button>
            <button className={`${styles.tabBtn} ${tab === 'history' ? styles.tabBtnActive : ''}`} onClick={() => setTab('history')}>History</button>
          </div>
        }
      />
      <div className={styles.content}>
        {tab === 'board' ? (
          <div className={styles.board}>
            {COLUMNS.map((col) => {
              const colOrders = orders.filter((o) => o.status === col.key)
              return (
                <div key={col.key} className={styles.column}>
                  <div className={styles.columnHeader}>
                    <span>{col.label}</span>
                    <span className={styles.count}>{colOrders.length}</span>
                  </div>
                  <div className={styles.columnBody}>
                    {colOrders.length === 0 && <p className={styles.emptyCol}>No orders here</p>}
                    {colOrders.map((o) => {
                      const nextOptions = ORDER_STATUS_FLOW[o.status] || []
                      return (
                        <div key={o.id} className={`card ${styles.orderCard}`}>
                          <div className={styles.orderTop}>
                            <span className="mono" style={{ fontSize: 11.5 }}>{o.id}</span>
                            <span className={styles.time}>{new Date(o.placedAt).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}</span>
                          </div>
                          <p className={styles.customer}>{o.customerName}</p>
                          <p className={styles.address}>{o.address}</p>
                          <ul className={styles.itemList}>
                            {o.items.map((it, idx) => (
                              <li key={idx}>{it.qty}× {it.name}</li>
                            ))}
                          </ul>
                          <p className={styles.total}>₹{o.total}</p>
                          {nextOptions.length > 0 && (
                            <div className={styles.actions}>
                              {nextOptions.map((status) => (
                                <button
                                  key={status}
                                  className={status === 'rejected' ? 'btn-danger' : 'btn-primary'}
                                  onClick={() => updateOrderStatus(o.id, status)}
                                >
                                  {ACTION_LABELS[status]}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className={`card ${styles.historyTable}`}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Order</th>
                  <th>Customer</th>
                  <th>Items</th>
                  <th>Total</th>
                  <th>Status</th>
                  <th>Placed</th>
                </tr>
              </thead>
              <tbody>
                {orders.filter((o) => o.status === 'completed' || o.status === 'rejected').map((o) => (
                  <tr key={o.id}>
                    <td className="mono">{o.id}</td>
                    <td>{o.customerName}</td>
                    <td>{o.items.map((i) => `${i.qty}× ${i.name}`).join(', ')}</td>
                    <td>₹{o.total}</td>
                    <td><span className={`${styles.statusPill} ${styles['status_' + o.status]}`}>{o.status}</span></td>
                    <td>{new Date(o.placedAt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
