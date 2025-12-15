import { useState, useEffect } from 'react'
import './App.css'

function App() {
  // 1. The "Memory" (useState)
  // We create a variable 'expenses' to hold our data.
  // Initially, it is an empty list [].
  const [expenses, setExpenses] = useState([])

  // 2. The "Trigger" (useEffect)
  // This runs ONE time when the page loads.
  useEffect(() => {
    // The Waiter goes to the kitchen...
    fetch('http://127.0.0.1:8000/ledger/api/expenses/')
      .then(response => response.json()) // Waiter gets the JSON plate
      .then(data => {
        console.log("Data received:", data); // Check your browser console!
        setExpenses(data.results); // Update the Memory
      })
      .catch(error => console.error("Error fetching data:", error));
  }, [])

  return (
    // 3. The "Menu" (JSX - looks like HTML)
    <div style={{ padding: "20px" }}>
      <h1>🐼 PandaLedger Live</h1>
      
      {/* 4. The Loop (map) */}
      {/* For every expense in our memory, show a card */}
      {expenses.map(expense => (
        <div key={expense.id} style={{ border: "1px solid #444", margin: "10px", padding: "10px", borderRadius: "8px" }}>
          <h3>{expense.description}</h3>
          <p>💰 ₹{expense.amount}</p>
          <small>📅 {expense.date} | 🏷️ {expense.category}</small>
        </div>
      ))}
      
      {expenses.length === 0 && <p>Loading expenses...</p>}
    </div>
  )
}

export default App