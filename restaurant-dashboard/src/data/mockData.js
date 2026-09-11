// Mock data layer for the restaurant-facing dashboard.

export const restaurantProfile = {
  id: 'r1',
  name: 'Paradise Biryani House',
  ownerName: 'Krishna Rao',
  phone: '+91 90000 11223',
  email: 'owner@paradisebiryani.example',
  address: 'Tirupati Main Road, Near Bus Stand',
  cuisines: ['Biryani', 'Mughlai', 'North Indian'],
  rating: 4.4,
  isOpen: true,
}

export const initialMenu = [
  {
    category: 'Biryani',
    items: [
      { id: 'i1', name: 'Hyderabadi Chicken Biryani', price: 260, veg: false, available: true, desc: 'Slow-cooked basmati, tender chicken, saffron' },
      { id: 'i2', name: 'Mutton Biryani', price: 320, veg: false, available: true, desc: 'Rich, spiced, dum-cooked mutton biryani' },
      { id: 'i3', name: 'Veg Dum Biryani', price: 210, veg: true, available: true, desc: 'Mixed vegetables and basmati, dum-sealed' },
    ],
  },
  {
    category: 'Starters',
    items: [
      { id: 'i4', name: 'Chicken 65', price: 190, veg: false, available: true, desc: 'Deep-fried spiced chicken bites' },
      { id: 'i5', name: 'Paneer Tikka', price: 180, veg: true, available: false, desc: 'Char-grilled marinated paneer' },
    ],
  },
]

export const initialOrders = [
  {
    id: 'ORD2001',
    customerName: 'Sneha Patil',
    items: [{ name: 'Hyderabadi Chicken Biryani', qty: 2 }, { name: 'Chicken 65', qty: 1 }],
    total: 710,
    status: 'new',
    placedAt: '2026-09-09T12:05:00',
    address: '4-2-11, Balaji Nagar, Tirupati',
  },
  {
    id: 'ORD2002',
    customerName: 'Vikram Iyer',
    items: [{ name: 'Mutton Biryani', qty: 1 }],
    total: 320,
    status: 'preparing',
    placedAt: '2026-09-09T11:40:00',
    address: 'Renigunta Road, Flat 302',
  },
  {
    id: 'ORD2003',
    customerName: 'Divya Menon',
    items: [{ name: 'Veg Dum Biryani', qty: 1 }, { name: 'Paneer Tikka', qty: 1 }],
    total: 428,
    status: 'ready',
    placedAt: '2026-09-09T11:10:00',
    address: 'Gandhi Road, Near Temple',
  },
  {
    id: 'ORD1998',
    customerName: 'Arjun Rao',
    items: [{ name: 'Hyderabadi Chicken Biryani', qty: 1 }],
    total: 295,
    status: 'completed',
    placedAt: '2026-09-08T20:15:00',
    address: 'Leela Mahal Circle',
  },
  {
    id: 'ORD1990',
    customerName: 'Priya Nair',
    items: [{ name: 'Mutton Biryani', qty: 2 }],
    total: 690,
    status: 'completed',
    placedAt: '2026-09-08T19:02:00',
    address: 'AIR Bypass Road',
  },
  {
    id: 'ORD1985',
    customerName: 'Rahul Verma',
    items: [{ name: 'Chicken 65', qty: 2 }],
    total: 415,
    status: 'rejected',
    placedAt: '2026-09-08T13:30:00',
    address: 'Tirchanur Road',
  },
]

export const offers = [
  { id: 'o1', title: '50% OFF up to ₹100', code: 'PARADISE50', active: true, minOrder: 300 },
  { id: 'o2', title: 'Free delivery on orders above ₹250', code: 'FREEDEL', active: true, minOrder: 250 },
  { id: 'o3', title: '₹50 OFF for new customers', code: 'FIRST50', active: false, minOrder: 200 },
]

export const reviews = [
  { id: 'rv1', customerName: 'Sneha Patil', rating: 5, comment: 'Best biryani in Tirupati, hands down.', date: '2026-09-07' },
  { id: 'rv2', customerName: 'Arjun Rao', rating: 4, comment: 'Great taste, delivery was a bit slow today.', date: '2026-09-06' },
  { id: 'rv3', customerName: 'Divya Menon', rating: 5, comment: 'Paneer tikka was fresh and well spiced.', date: '2026-09-05' },
  { id: 'rv4', customerName: 'Rahul Verma', rating: 3, comment: 'Good food, packaging could be better.', date: '2026-09-03' },
]

// Last 7 days, for the earnings chart
export const earningsSeries = [
  { day: 'Mon', amount: 8400 },
  { day: 'Tue', amount: 7250 },
  { day: 'Wed', amount: 9100 },
  { day: 'Thu', amount: 6800 },
  { day: 'Fri', amount: 11200 },
  { day: 'Sat', amount: 14500 },
  { day: 'Sun', amount: 12900 },
]

export const ORDER_STATUS_FLOW = {
  new: ['preparing', 'rejected'],
  preparing: ['ready'],
  ready: ['completed'],
  completed: [],
  rejected: [],
}
