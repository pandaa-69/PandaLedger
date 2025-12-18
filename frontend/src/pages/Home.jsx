// frontend/src/pages/Home.jsx
import React from 'react';
import AddExpenseForm from '../components/AddExpenseForm';

function Home({ expenses }) {
    const handleDelete = (id) => {
        // we need to ask a user that are they sure and want to delete so we know its not by accident 
        if (!confirm("Are you sure you want to delete this?")) return;

        // backend call 
        fetch(`http://127.0.0.1:8000/api/expenses/delete/${id}`, {
            method:'DELETE',
            credentials:'include', // for sending the cookies

        })
        .then(response =>{
            if(response.ok){
                alert("Deleted");
                window.location.reload(); // reloading the page tp update the list
            } else{
                alert("Failed to delete. Check backend terminal for errors");
            }
        })
        .catch(err =>console.error(err));
    };
return (
        <div style={{ padding: "20px", width: "100%", maxWidth: "800px", margin: "0 auto" }}>
            
            <h1 style={{ textAlign: "center" }}>🐼 PandaLedger Live</h1>
            
            <AddExpenseForm /> 
            
            <hr style={{ margin: "30px 0", borderColor: "#444" }}/>

            {expenses.length === 0 ? (
                <div style={{ textAlign:"center", color:"#888", marginTop:"20px" }}>
                    <h3>No expenses yet! 📝</h3>
                    <p>Use the form above to add your first transaction.</p>
                </div>
            ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
                    {expenses.map(expense => (
                        <div key={expense.id} style={styles.card}>
                            
                            {/* Left Side: Expense Info */}
                            <div>
                                <h3 style={{ margin: "0 0 5px 0" }}>{expense.description}</h3>
                                <div style={{ display: "flex", gap: "15px", alignItems: "center" }}>
                                    <span style={styles.amount}>₹{expense.amount}</span>
                                    <span style={styles.badge}>{expense.category}</span>
                                    <span style={{ color: "#666", fontSize: "0.9rem" }}>{expense.date}</span>
                                </div>
                            </div>

                            {/* Right Side: Delete Button (ADDED THIS) */}
                            <button 
                                onClick={() => handleDelete(expense.id)} 
                                style={styles.deleteBtn}
                                title="Delete Expense"
                            >
                                🗑️
                            </button>

                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

// Styles
const styles = {
    card: {
        backgroundColor: "#222",
        padding: "20px",
        borderRadius: "12px",
        display: "flex",        // Arrange Left/Right
        justifyContent: "space-between", // Push button to the right
        alignItems: "center",
        border: "1px solid #333",
        boxShadow: "0 2px 5px rgba(0,0,0,0.2)"
    },
    amount: { fontSize: "1.2rem", color: "#4ade80", fontWeight: "bold" },
    badge: { backgroundColor: "#333", padding: "4px 8px", borderRadius: "5px", fontSize: "0.85rem", color: "#ccc" },
    meta: { color: "#888" },
    deleteBtn: {
        backgroundColor: "transparent",
        border: "none",
        cursor: "pointer",
        fontSize: "1.5rem",
        transition: "transform 0.2s"
    }
};

export default Home