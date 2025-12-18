import React, { useState } from 'react';

function AddExpenseForm() {
    // 1. The "State" (Memory) for our form fields
    const [description, setDescription] = useState('');
    const [amount, setAmount] = useState('');
    const [category, setCategory] = useState('');

    // 2. The function that runs when you click "Add Expense"
    const handleSubmit = (e) => {
        e.preventDefault(); // Stop the page from reloading (default browser behavior)

        // The Data we want to send
        const expenseData = {
            description: description,
            amount: amount,
            category: category,
            date: new Date().toISOString() // Today's date (YYYY-MM-DD)
        };

        // 3. The POST Request (Sending the order to Django)
        fetch('http://127.0.0.1:8000/api/expenses/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(expenseData),
            credentials:'include' // Convert JS Object to JSON Text
        })
        .then(response => {
            if(!response.ok){
                throw new Error("Server rejected request");
            }
            return response.json();
        })
        .then(data => {
            console.log("Success:", data);
            alert("Expense Added! (Refresh the page to see it)");
            // Clear the form
            setDescription('');
            setAmount('');
            setCategory('');

            // reloading automatically so the new item 
            window.location.reload();
        })
        .catch((error) => {
            console.error('Error:', error);
            alert("Error adding expense. Check the console.");
        });
    };

    return (
        <div style={styles.formContainer}>
            <h3>➕ Add New Expense</h3>
            <form onSubmit={handleSubmit} style={styles.form}>
                
                <input 
                    type="text" 
                    placeholder="Description (e.g. Burger)" 
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    style={styles.input}
                    required
                />

                <input 
                    type="number" 
                    placeholder="Amount (₹)" 
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    style={styles.input}
                    required
                />

                {/* NOTE: For now, type a Category that ACTUALLY exists in your DB (e.g. 'Food') */}
                <input 
                    type="text" 
                    placeholder="Category (e.g. Food)" 
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    style={styles.input}
                    required
                />

                <button type="submit" style={styles.button}>Add Expense</button>
            </form>
        </div>
    );
}

// Simple Styles to make it look decent
const styles = {
    formContainer: {
        backgroundColor: '#2a2a2a',
        padding: '20px',
        borderRadius: '10px',
        marginTop: '20px',
        border: '1px solid #444',
        maxWidth: '500px'
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '15px',
    },
    input: {
        padding: '10px',
        borderRadius: '5px',
        border: '1px solid #555',
        backgroundColor: '#333',
        color: 'white',
        fontSize: '1rem'
    },
    button: {
        padding: '10px',
        borderRadius: '5px',
        border: 'none',
        backgroundColor: '#a78bfa',
        color: 'black',
        fontWeight: 'bold',
        cursor: 'pointer',
        fontSize: '1rem'
    }
};

export default AddExpenseForm;