import React from "react";
import AddExpenseForm from "../components/AddExpenseForm";
import BudgetCard from "../components/ledger/BudgetCard"; // 👈 Import the new component
import { Trash2, Wallet, ArrowDownCircle } from "lucide-react";
import { getCookie } from '../utils/csrf';

function Ledger({ expenses, onTransactionUpdate }) { 
  
  // Simple delete logic
  const handleDelete = (id) => {
    if (!confirm("Delete transaction?")) return;
    fetch(`http://127.0.0.1:8000/api/expenses/delete/${id}/`, {
      method: "DELETE",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie('csrftoken')
      },
      credentials: "include",
    }).then((res) => {
      if (res.ok) {
        window.location.reload(); 
      }
    });
  };

  const formatDate = (date) =>
    new Date(date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });

  return (
    <div className="mx-auto max-w-4xl animate-in fade-in slide-in-from-bottom-4 duration-700 pb-20">
      {/* Header */}
      <div className="mb-8 flex items-center gap-4 pt-8">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-500/20 text-purple-400">
          <Wallet size={24} />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-white">Expense Ledger</h1>
          <p className="text-gray-400">Track every penny.</p>
        </div>
      </div>

      {/* 📊 NEW: Budget Progress Card */}
      <BudgetCard />

      {/* 1. Add Expense Form */}
      <div className="mb-10">
        <AddExpenseForm onSuccess={() => window.location.reload()} />
      </div>

      {/* 2. Transaction List */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-white">Recent Transactions</h3>
        <span className="text-xs text-gray-500 uppercase tracking-widest">
          History
        </span>
      </div>

      {/* List Content */}
      {!expenses || expenses.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-800 bg-black/20 p-12 text-center text-gray-500">
          <p>No records found. Start spending! 💸</p>
        </div>
      ) : (
        <div className="space-y-3">
          {expenses.map((expense) => (
            <div
              key={expense.id}
              className="group flex items-center justify-between rounded-xl border border-white/5 bg-white/5 p-4 transition-all hover:border-purple-500/30 hover:bg-white/10 hover:translate-x-1"
            >
              <div className="flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-500/10 text-red-400">
                  <ArrowDownCircle size={18} />
                </div>
                <div>
                  <p className="font-medium text-gray-200">
                    {expense.description}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatDate(expense.date)} • {expense.category}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-lg font-bold text-white">
                  -₹{parseFloat(expense.amount).toLocaleString()}
                </span>
                <button
                  onClick={() => handleDelete(expense.id)}
                  className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-500 transition-all"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Ledger;