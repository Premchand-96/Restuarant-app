import { useState } from 'react'
import { useDashboard } from '../context/DashboardContext'
import DashHeader from '../components/DashHeader'
import styles from './MenuManagement.module.css'

export default function MenuManagement() {
  const { menu, toggleItemAvailability, updateItem, addItem, deleteItem } = useDashboard()
  const [editingId, setEditingId] = useState(null)
  const [draft, setDraft] = useState({})
  const [showAdd, setShowAdd] = useState(false)
  const [newItem, setNewItem] = useState({ category: menu[0]?.category || '', name: '', price: '', veg: true, desc: '' })

  const startEdit = (item) => {
    setEditingId(item.id)
    setDraft({ name: item.name, price: item.price, desc: item.desc })
  }

  const saveEdit = (itemId) => {
    updateItem(itemId, { name: draft.name, price: Number(draft.price), desc: draft.desc })
    setEditingId(null)
  }

  const handleAddItem = (e) => {
    e.preventDefault()
    if (!newItem.name || !newItem.price || !newItem.category) return
    addItem(newItem.category, {
      name: newItem.name,
      price: Number(newItem.price),
      veg: newItem.veg,
      available: true,
      desc: newItem.desc,
    })
    setNewItem({ category: menu[0]?.category || '', name: '', price: '', veg: true, desc: '' })
    setShowAdd(false)
  }

  return (
    <div>
      <DashHeader
        title="Menu"
        subtitle="Manage categories, items, prices and availability"
        right={<button className="btn-primary" onClick={() => setShowAdd((s) => !s)}>{showAdd ? 'Close' : '+ Add item'}</button>}
      />
      <div className={styles.content}>
        {showAdd && (
          <form className={`card ${styles.addForm}`} onSubmit={handleAddItem}>
            <div className={styles.addGrid}>
              <label className={styles.field}>
                <span>Category</span>
                <input value={newItem.category} onChange={(e) => setNewItem((n) => ({ ...n, category: e.target.value }))} placeholder="e.g. Starters" />
              </label>
              <label className={styles.field}>
                <span>Item name</span>
                <input value={newItem.name} onChange={(e) => setNewItem((n) => ({ ...n, name: e.target.value }))} placeholder="e.g. Gobi Manchurian" required />
              </label>
              <label className={styles.field}>
                <span>Price (₹)</span>
                <input type="number" value={newItem.price} onChange={(e) => setNewItem((n) => ({ ...n, price: e.target.value }))} required />
              </label>
              <label className={styles.field}>
                <span>Type</span>
                <select value={newItem.veg ? 'veg' : 'nonveg'} onChange={(e) => setNewItem((n) => ({ ...n, veg: e.target.value === 'veg' }))}>
                  <option value="veg">Veg</option>
                  <option value="nonveg">Non-Veg</option>
                </select>
              </label>
              <label className={styles.field} style={{ gridColumn: '1 / -1' }}>
                <span>Description</span>
                <input value={newItem.desc} onChange={(e) => setNewItem((n) => ({ ...n, desc: e.target.value }))} placeholder="Short description" />
              </label>
            </div>
            <button className="btn-primary" type="submit" style={{ marginTop: 14 }}>Save item</button>
          </form>
        )}

        {menu.map((sec) => (
          <div key={sec.category} className={styles.section}>
            <h2 className={styles.sectionTitle}>{sec.category}</h2>
            <div className={`card ${styles.itemTable}`}>
              {sec.items.map((item) => (
                <div key={item.id} className={styles.itemRow}>
                  <span className={item.veg ? 'veg-dot' : 'nonveg-dot'} style={vegDotStyle(item.veg)} />
                  {editingId === item.id ? (
                    <div className={styles.editFields}>
                      <input value={draft.name} onChange={(e) => setDraft((d) => ({ ...d, name: e.target.value }))} />
                      <input type="number" value={draft.price} onChange={(e) => setDraft((d) => ({ ...d, price: e.target.value }))} style={{ width: 80 }} />
                      <input value={draft.desc} onChange={(e) => setDraft((d) => ({ ...d, desc: e.target.value }))} placeholder="Description" />
                    </div>
                  ) : (
                    <div className={styles.itemInfo}>
                      <p className={styles.itemName}>{item.name}</p>
                      <p className={styles.itemDesc}>{item.desc}</p>
                    </div>
                  )}
                  {editingId !== item.id && <p className={styles.itemPrice}>₹{item.price}</p>}
                  <label className={styles.availToggle}>
                    <input type="checkbox" checked={item.available} onChange={() => toggleItemAvailability(item.id)} />
                    {item.available ? 'Available' : 'Sold out'}
                  </label>
                  <div className={styles.rowActions}>
                    {editingId === item.id ? (
                      <>
                        <button className="btn-primary" onClick={() => saveEdit(item.id)}>Save</button>
                        <button className="btn-secondary" onClick={() => setEditingId(null)}>Cancel</button>
                      </>
                    ) : (
                      <>
                        <button className="btn-secondary" onClick={() => startEdit(item)}>Edit</button>
                        <button className="btn-danger" onClick={() => deleteItem(item.id)}>Delete</button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function vegDotStyle() {
  return { marginTop: 4 }
}
