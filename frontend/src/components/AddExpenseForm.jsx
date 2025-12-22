import React, { useState } from "react";
import { Plus, Loader2 } from "lucide-react";
import { getCookie } from "../utils/csrf";
import API_URL from '../config';

function AddExpenseForm() {
  // 1. MY STATE: This is where I keep track of what I'm typing right now.
  // Initially, everything is empty.
  const [formData, setFormData] = useState({
    description: "",
    amount: "",
    category: "",
  });

  // loading state: So I can show a spinner while waiting for Django
  const [loading, setLoading] = useState(false);

  // 2. THE HANDLER: When I type in any input, this updates the specific field in my state.
  // I use [e.target.name] so I don't have to write 3 separate functions. Smart!
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // 3. THE SUBMIT: This runs when I click the "Add Expense" button.
  const handleSubmit = (e) => {
    e.preventDefault(); // Stop the browser from refreshing the page automatically
    setLoading(true); // Start the spinner!

    // I need to add the current date before sending to backend
    const payload = {
      ...formData,
      date: new Date().toISOString(),
    };

    // Sending the data to my Django API...
    fetch(`${API_URL}/api/expenses/add/`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie('csrftoken')
      },
      body: JSON.stringify(payload), // Convert my JS object to JSON text
      credentials: "include", // CRITICAL: Send my session cookie so Django knows who I am
    })
      .then((res) => {
        if (!res.ok) throw new Error("Server said NO!"); // Handle 400/500 errors
        return res.json();
      })
      .then(() => {
        // Success! Reset the form so I can add another one
        setFormData({ description: "", amount: "", category: "" });
        // For now, I'm just reloading the page to see the new item.
        // Future Me: Try to update the list state directly to avoid reload?
        window.location.reload();
      })
      .catch((err) => {
        console.error(err);
        alert("Something went wrong. Check the console.");
        setLoading(false); // Stop the spinner if it fails
      });
  };

  return (
    // THE UI: Using Tailwind classes for that Glassmorphism look
    <div className="mx-auto mt-8 w-full max-w-md rounded-xl border border-white/10 bg-black/40 p-6 backdrop-blur-md transition-all hover:border-purple-500/30 hover:shadow-lg hover:shadow-purple-500/10">
      {/* Header Section: The icon and title */}
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-500/10 text-purple-400">
          <Plus size={20} />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white">New Transaction</h3>
          <p className="text-xs text-gray-400">Track my spending instantly</p>
        </div>
      </div>

      {/* The Form Inputs */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 1. Description Field */}
        <div className="space-y-1">
          <label className="ml-1 text-xs font-medium text-gray-400">
            Description
          </label>
          <input
            name="description"
            type="text"
            placeholder="e.g. Starbucks Coffee"
            value={formData.description}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder-gray-500 outline-none transition-all focus:border-purple-500/50 focus:bg-white/10 focus:ring-1 focus:ring-purple-500/50"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* 2. Amount Field */}
          <div className="space-y-1">
            <label className="ml-1 text-xs font-medium text-gray-400">
              Amount (₹)
            </label>
            <input
              name="amount"
              type="number"
              placeholder="0.00"
              value={formData.amount}
              onChange={handleChange}
              required
              className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder-gray-500 outline-none transition-all focus:border-green-500/50 focus:bg-white/10 focus:ring-1 focus:ring-green-500/50"
            />
          </div>

          {/* 3. Category Field */}
          <div className="space-y-1">
            <label className="ml-1 text-xs font-medium text-gray-400">
              Category
            </label>
            <input
              name="category"
              type="text"
              placeholder="Food, Travel..."
              value={formData.category}
              onChange={handleChange}
              required
              className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder-gray-500 outline-none transition-all focus:border-blue-500/50 focus:bg-white/10 focus:ring-1 focus:ring-blue-500/50"
            />
          </div>
        </div>

        {/* Submit Button: Shows a spinner when I'm waiting */}
        <button
          type="submit"
          disabled={loading}
          className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 py-3 text-sm font-bold text-white transition-all hover:opacity-90 active:scale-95 disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Adding...
            </>
          ) : (
            "Add Expense"
          )}
        </button>
      </form>
    </div>
  );
}

export default AddExpenseForm;
