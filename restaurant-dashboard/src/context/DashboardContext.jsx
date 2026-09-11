import { createContext, useContext, useState, useCallback, useMemo } from 'react'
import { restaurantProfile, initialMenu, initialOrders, offers as initialOffers } from '../data/mockData'

const DashboardContext = createContext(null)

export function DashboardProvider({ children }) {
  const [isAuthed, setIsAuthed] = useState(true)
  const [profile, setProfile] = useState(restaurantProfile)
  const [menu, setMenu] = useState(initialMenu)
  const [orders, setOrders] = useState(initialOrders)
  const [offers, setOffers] = useState(initialOffers)

  const toggleOpen = useCallback(() => {
    setProfile((p) => ({ ...p, isOpen: !p.isOpen }))
  }, [])

  const toggleItemAvailability = useCallback((itemId) => {
    setMenu((prev) =>
      prev.map((sec) => ({
        ...sec,
        items: sec.items.map((it) => (it.id === itemId ? { ...it, available: !it.available } : it)),
      }))
    )
  }, [])

  const updateItem = useCallback((itemId, patch) => {
    setMenu((prev) =>
      prev.map((sec) => ({
        ...sec,
        items: sec.items.map((it) => (it.id === itemId ? { ...it, ...patch } : it)),
      }))
    )
  }, [])

  const addItem = useCallback((category, item) => {
    setMenu((prev) => {
      const exists = prev.find((s) => s.category === category)
      const newItem = { ...item, id: `i${Date.now()}` }
      if (exists) {
        return prev.map((s) => (s.category === category ? { ...s, items: [...s.items, newItem] } : s))
      }
      return [...prev, { category, items: [newItem] }]
    })
  }, [])

  const deleteItem = useCallback((itemId) => {
    setMenu((prev) => prev.map((sec) => ({ ...sec, items: sec.items.filter((it) => it.id !== itemId) })).filter((sec) => sec.items.length > 0))
  }, [])

  const updateOrderStatus = useCallback((orderId, status) => {
    setOrders((prev) => prev.map((o) => (o.id === orderId ? { ...o, status } : o)))
  }, [])

  const toggleOffer = useCallback((offerId) => {
    setOffers((prev) => prev.map((o) => (o.id === offerId ? { ...o, active: !o.active } : o)))
  }, [])

  const stats = useMemo(() => {
    const completed = orders.filter((o) => o.status === 'completed')
    const totalRevenue = completed.reduce((s, o) => s + o.total, 0)
    const newCount = orders.filter((o) => o.status === 'new').length
    const preparingCount = orders.filter((o) => o.status === 'preparing').length
    return { totalRevenue, newCount, preparingCount, completedCount: completed.length, totalOrders: orders.length }
  }, [orders])

  const value = {
    isAuthed, setIsAuthed,
    profile, toggleOpen,
    menu, toggleItemAvailability, updateItem, addItem, deleteItem,
    orders, updateOrderStatus,
    offers, toggleOffer,
    stats,
  }

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>
}

export function useDashboard() {
  const ctx = useContext(DashboardContext)
  if (!ctx) throw new Error('useDashboard must be used within DashboardProvider')
  return ctx
}
