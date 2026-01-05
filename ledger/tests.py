from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Expense, Category

User = get_user_model()

class ExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.category = Category.objects.create(name="Food", user=self.user)

    def test_expense_creation(self):
        """Test that an expense is correctly created and string representation is valid."""
        expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=100.50,
            description="Lunch",
            date=timezone.now()
        )
        self.assertEqual(expense.description, "Lunch")
        self.assertEqual(expense.amount, 100.50)
        self.assertIn("Lunch", str(expense))
        self.assertIn("Food", str(expense))

