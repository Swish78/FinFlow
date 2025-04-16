from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class AccountType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    normal_balance = models.CharField(max_length=10, choices=[
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    ])
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Account(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT, related_name='accounts')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['account_type']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class FiscalYear(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('POSTED', 'Posted'),
        ('VOIDED', 'Voided'),
    ]
    
    reference_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    transaction_date = models.DateField()
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.PROTECT, related_name='transactions')
    
    class Meta:
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['status']),
            models.Index(fields=['reference_number']),
        ]
    
    def __str__(self):
        return f"Transaction {self.reference_number} ({self.transaction_date})"


class JournalEntry(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='entries')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='entries')
    description = models.TextField(blank=True)
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        verbose_name_plural = "Journal Entries"
        indexes = [
            models.Index(fields=['transaction']),
            models.Index(fields=['account']),
        ]
    
    def __str__(self):
        if self.debit_amount > 0:
            return f"{self.account} - Debit {self.debit_amount}"
        return f"{self.account} - Credit {self.credit_amount}"


class Ledger(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='ledger_entries')
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='ledger_entries')
    period = models.CharField(max_length=7)  # Format: YYYY-MM
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['account', 'fiscal_year', 'period']
        indexes = [
            models.Index(fields=['account', 'fiscal_year', 'period']),
        ]
    
    def __str__(self):
        return f"{self.account} - {self.period} - {self.closing_balance}"


class FinancialStatement(models.Model):
    STATEMENT_TYPES = [
        ('INCOME', 'Income Statement'),
        ('BALANCE', 'Balance Sheet'),
        ('CASHFLOW', 'Cash Flow Statement'),
        ('EQUITY', 'Statement of Changes in Equity'),
    ]
    
    statement_type = models.CharField(max_length=10, choices=STATEMENT_TYPES)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='financial_statements')
    period = models.CharField(max_length=7, blank=True)  # Format: YYYY-MM, blank for annual statements
    generated_at = models.DateTimeField(default=timezone.now)
    generated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='generated_statements')
    data = models.JSONField()  # Store the statement data as JSON
    
    class Meta:
        indexes = [
            models.Index(fields=['statement_type']),
            models.Index(fields=['fiscal_year']),
        ]
    
    def __str__(self):
        if self.period:
            return f"{self.get_statement_type_display()} - {self.fiscal_year} - {self.period}"
        return f"{self.get_statement_type_display()} - {self.fiscal_year} (Annual)"
