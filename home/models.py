from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from datetime import date
from datetime import timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import calendar
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from decimal import Decimal


# Gender choices
GENDER_TYPE_CHOICES = (
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
)

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    email = models.EmailField(max_length=255, blank=True, null=True)
    otherName = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(
        max_length=20, choices=GENDER_TYPE_CHOICES, default="male"
    )
    dob = models.DateTimeField(null=True, blank=True)
    phoneNumber = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    nin = models.CharField(max_length=200, blank=True, null=True)
    
    image = models.ImageField(upload_to="profile-picture", blank=True, null=True)
    active = models.BooleanField(default=False)
    dateCreated = models.DateTimeField(auto_now_add=True)
    dateUpdated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}"
    

class SiteSetting(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    tmsaasKey = models.TextField(help_text="Encrypted key for TMSaaS payment")
    tmsaasBaseUrl = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return f"{self.site.name} Settings"
    


class UserOTP(models.Model):
    phoneNumber = models.CharField(max_length=24)
    otp = models.TextField(help_text="Encrypted OTP Value", blank=True, null=True)
    expiry = models.DateTimeField(blank=True, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True)
    dateUpdated = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phoneNumber}"



class TierAmountDb(models.Model):
    class Tiers(models.TextChoices):
        TIER_1 = "1", 
        TIER_2 = "2", 
        TIER_3 = "3", 
        
    tier_choice = models.CharField(
        max_length=25,
        choices=Tiers.choices,
        default=Tiers.TIER_1
    )

    minimum_balance = models.DecimalField(max_digits=32, decimal_places=16,
        null=True, blank=True
    )
    
    maximum_balance = models.DecimalField(max_digits=32, decimal_places=16,
        null=True, blank=True
    )
    

class CreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="credit_cards")
    card_number = models.CharField(max_length=16)
    card_holder_name = models.CharField(max_length=100)
    expiry_date = models.DateField() 
    cvv = models.CharField(max_length=4)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card_holder_name} - **** **** **** {self.card_number[-4:]}"
    
    
    
    # base model
class BaseInvestment(models.Model):
    investment_interest_tracking = models.DecimalField(max_digits=12, decimal_places=2)
    investment_latest_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_returns = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        abstract = True

    def calculate_daily_return(self, monthly_return):
        now = timezone.now()
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        return monthly_return / days_in_month

    def update_daily_interest(self, monthly_return):
        daily_interest = self.calculate_daily_return(monthly_return)
        self.investment_interest_tracking += daily_interest
        self.investment_latest_amount += daily_interest
        self.total_returns += daily_interest
        self.save()
        return daily_interest


class Type(models.TextChoices):
        DAILY= "DAILY", "Daily"
        WEEKLY = 'WEEKLY', "Weekly"
        MONTHLY = "MONTHLY","Monthly"
        QUARTERLY = "QUARTERLY", "Quarterly",
        ONETIME = "ONETIME", "Onetime"
        
        
        
        
        
        
class HalalInvestment(BaseInvestment):  # Inherit here
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    investment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    card = models.ForeignKey(CreditCard, null=True, blank=True, on_delete=models.SET_NULL, related_name='investments')
    investment_latestest_withdrawl = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)    
    investment_deposit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    frequency_choices = models.CharField(choices=Type.choices, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    last_withdrawal_date = models.DateTimeField(auto_now=True)
    cards_registered = models.BooleanField(default=True)

    def calculate_monthly_return(self):
        return self.investment_amount * 0.20

    def update_daily_interest(self):
        monthly_return = self.calculate_monthly_return()
        return super().update_daily_interest(monthly_return)
        
        
        
        


class FreeStyleInvestment(BaseInvestment):  # Inherit here
    #
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    frequency_choices = models.CharField(choices=Type.choices, max_length=20)
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    investment_returns_monthly = models.DecimalField(max_digits=12, decimal_places=2)
    investment_deposit = models.PositiveBigIntegerField(
        validators=(MinValueValidator(500), MaxValueValidator(1000000)),
        null=True
    )
    withdrawl = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    last_withdrawal_date = models.DateField(null=True, blank=True)
    total_withdrawn = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    #returns the 
    def calculate_monthly_return(self):
        return self.investment_returns_monthly * 0.10

    def is_eligible_for_withdrawal(self):
        today = timezone.now().date()
        if not self.last_withdrawal_date:
            return today >= self.start_date + relativedelta(months=1)
        return today >= self.last_withdrawal_date + relativedelta(months=1)

    def withdrawl_monthly(self):
        if not self.is_eligible_for_withdrawal():
            return {'success': False, 'message': 'Not eligible for withdrawal yet.'}
        
        monthly_return = self.calculate_monthly_return()
        self.withdrawl = monthly_return
        self.last_withdrawal_date = timezone.now().date()
        self.total_withdrawn += monthly_return
        self.save()
        return {'success': True, 'message': 'Withdrawal successful', 'amount': monthly_return}

    def get_next_withdrawal_date(self):
        if not self.last_withdrawal_date:
            return self.start_date + relativedelta(months=1)
        return self.last_withdrawal_date + relativedelta(months=1)

    def update_daily_interest(self):
        monthly_return = self.calculate_monthly_return()
        return super().update_daily_interest(monthly_return)






class InvestmentType(models.TextChoices):
    RELIEF = 'relief', 'Relief'
    SENIOR = 'senior', 'Senior'
    EARLY_STARTER = 'early_starter', 'Early Starter'
    VACAY = 'vacay', 'Vacay'
    HI_WEALTH = 'hi_wealth', 'Hi-Wealth'






class TargetInvestment(models.Model):
    """Base model for all investment types"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    investment_type = models.CharField(max_length=20, choices=InvestmentType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    payment_frequency = models.CharField(max_length=20, choices=Type.choices)
    total_interest_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    
    def calculate_interest_rate(self):
        """Return the annual interest rate as a decimal"""
        if self.investment_type == InvestmentType.RELIEF:
            return Decimal('0.20')  # 20% P.A
        elif self.investment_type == InvestmentType.SENIOR:
            return Decimal('0.20')  # Default to minimum 20% P.A
        elif self.investment_type == InvestmentType.EARLY_STARTER:
            return Decimal('0.20')  # 20% P.A
        elif self.investment_type == InvestmentType.VACAY:
            return Decimal('0.20')  # 20% P.A
        elif self.investment_type == InvestmentType.HI_WEALTH:
            return Decimal('0.20')  # Assumed 20% P.A
        return Decimal('0.0')
    
    def calculate_monthly_interest(self):
        """Calculate the monthly interest"""
        annual_rate = self.calculate_interest_rate()
        monthly_rate = annual_rate / 12
        return self.current_balance * monthly_rate
    
    def add_monthly_interest(self):
        """Add monthly interest to the balance"""
        monthly_interest = self.calculate_monthly_interest()
        self.total_interest_earned += monthly_interest
        self.current_balance += monthly_interest
        self.save()
        
        # Create transaction record
        Transaction.objects.create(
            investment=self,
            transaction_type='interest',
            amount=monthly_interest,
            description='Monthly interest credited'
        )
        
        return monthly_interest
    
    def make_deposit(self, amount):
        """Process a deposit to the investment"""
        self.current_balance += amount
        self.save()
        
        # Create transaction record
        Transaction.objects.create(
            investment=self,
            transaction_type='deposit',
            amount=amount,
            description='Deposit to investment'
        )
        
        return True
    
    def make_withdrawal(self, amount):
        """Process a withdrawal from the investment"""
        # Subclass implementations would override this with specific rules
        if amount <= self.current_balance:
            self.current_balance -= amount
            self.save()
            
            # Create transaction record
            Transaction.objects.create(
                investment=self,
                transaction_type='withdrawal',
                amount=amount,
                description='Withdrawal from investment'
            )
            
            return True
        return False
    
    def get_tenure_in_months(self):
        """Calculate the tenure in months"""
        delta = relativedelta(self.end_date, self.start_date)
        return delta.years * 12 + delta.months
    
    def get_remaining_tenure_in_days(self):
        """Calculate remaining days in tenure"""
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days
    
    class Meta:
        abstract = False





class ReliefInvestment(models.Model):
    """Relief investment model - 20% P.A"""
    base_investment = models.OneToOneField(TargetInvestment, on_delete=models.CASCADE, primary_key=True)
    withdrawal_count = models.PositiveIntegerField(default=0)
    last_withdrawal_date = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Set minimum tenure to 2 months
        if not self.pk:  # Only for new instances
            min_tenure = timezone.now().date() + relativedelta(months=2)
            if self.base_investment.end_date < min_tenure:
                self.base_investment.end_date = min_tenure
                self.base_investment.save()
        super().save(*args, **kwargs)
    
    def make_withdrawal(self, amount):
        """Process a withdrawal with Relief-specific rules"""
        today = timezone.now().date()
        
        # Check if investment is at least 180 days old
        days_since_start = (today - self.base_investment.start_date).days
        is_long_term = days_since_start >= 180
        
        # Long-term investments (180+ days) get 2 free withdrawals
        if is_long_term and self.withdrawal_count < 2:
            if amount <= self.base_investment.current_balance:
                self.base_investment.current_balance -= amount
                self.base_investment.save()
                
                self.withdrawal_count += 1
                self.last_withdrawal_date = today
                self.save()
                
                # Create transaction record
                Transaction.objects.create(
                    investment=self.base_investment,
                    transaction_type='withdrawal',
                    amount=amount,
                    description='Relief investment withdrawal'
                )
                
                return {
                    'success': True,
                    'message': f'Withdrawal successful. You have {2 - self.withdrawal_count} free withdrawals remaining.'
                }
            else:
                return {
                    'success': False,
                    'message': 'Insufficient balance for withdrawal.'
                }
        
        # Handle withdrawals beyond the free limit or for short-term investments
        # This will result in interest loss
        if amount <= self.base_investment.current_balance:
            # Calculate interest to forfeit (all accrued interest)
            interest_to_forfeit = self.base_investment.total_interest_earned
            
            # Reduce balance by amount and forfeit interest
            self.base_investment.current_balance -= amount
            self.base_investment.current_balance -= interest_to_forfeit
            self.base_investment.total_interest_earned = 0
            self.base_investment.save()
            
            self.withdrawal_count += 1
            self.last_withdrawal_date = today
            self.save()
            
            # Create transaction records
            Transaction.objects.create(
                investment=self.base_investment,
                transaction_type='withdrawal',
                amount=amount,
                description='Relief investment withdrawal'
            )
            
            Transaction.objects.create(
                investment=self.base_investment,
                transaction_type='interest_loss',
                amount=interest_to_forfeit,
                description='Interest forfeited due to early/excess withdrawal'
            )
            
            return {
                'success': True,
                'message': f'Withdrawal successful, but all accrued interest ({interest_to_forfeit}) has been forfeited.',
                'interest_forfeited': interest_to_forfeit
            }
        else:
            return {
                'success': False,
                'message': 'Insufficient balance for withdrawal.'
            }


class SeniorInvestment(models.Model):
    """Senior investment model - 20-28% P.A"""
    base_investment = models.OneToOneField(TargetInvestment, on_delete=models.CASCADE, primary_key=True)
    additional_investments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0.20)  # 20% default
    
    def save(self, *args, **kwargs):
        # Set minimum investment and tenure validation
        if not self.pk:  # Only for new instances
            # Minimum investment of N10,000,000
            min_investment = Decimal('10000000.00')
            if self.base_investment.amount < min_investment:
                self.base_investment.amount = min_investment
            
            # Set tenure to 12 months
            self.base_investment.end_date = self.base_investment.start_date + relativedelta(months=12)
            self.base_investment.save()
            
            # Calculate interest rate based on amount (simplified logic)
            if self.base_investment.amount >= Decimal('20000000.00'):
                self.interest_rate = Decimal('0.24')  # 24%
            elif self.base_investment.amount >= Decimal('15000000.00'):
                self.interest_rate = Decimal('0.22')  # 22%
            
        super().save(*args, **kwargs)
    
    def calculate_interest_rate(self):
        """Override to provide senior-specific interest rate"""
        return self.interest_rate
    
    def add_additional_investment(self, amount):
        """Add additional investment to Senior Investment"""
        self.additional_investments += amount
        self.base_investment.current_balance += amount
        self.base_investment.save()
        self.save()
        
        # Create transaction record
        Transaction.objects.create(
            investment=self.base_investment,
            transaction_type='additional_deposit',
            amount=amount,
            description='Additional deposit to Senior investment'
        )
        
        return True
    
    def withdraw_additional_investment(self, amount):
        """Withdraw from additional investments with no penalty"""
        if amount <= self.additional_investments:
            self.additional_investments -= amount
            self.base_investment.current_balance -= amount
            self.base_investment.save()
            self.save()
            
            # Create transaction record
            Transaction.objects.create(
                investment=self.base_investment,
                transaction_type='additional_withdrawal',
                amount=amount,
                description='Withdrawal from additional investment (no penalty)'
            )
            
            return {
                'success': True,
                'message': 'Additional investment withdrawal successful with no penalty.'
            }
        else:
            return {
                'success': False,
                'message': f'Insufficient additional investment balance. Maximum available: {self.additional_investments}'
            }
    
    def make_withdrawal(self, amount):
        """Process a withdrawal with Senior-specific rules"""
        today = timezone.now().date()
        
        # Check if investment has matured (12 months)
        days_since_start = (today - self.base_investment.start_date).days
        is_matured = days_since_start >= 365  # Assuming 365 days in a year
        
        # If matured, allow withdrawal without penalty
        if is_matured:
            if amount <= self.base_investment.current_balance:
                self.base_investment.current_balance -= amount
                self.base_investment.save()
                
                # Create transaction record
                Transaction.objects.create(
                    investment=self.base_investment,
                    transaction_type='withdrawal',
                    amount=amount,
                    description='Senior investment matured withdrawal'
                )
                
                return {
                    'success': True,
                    'message': 'Withdrawal successful. Investment has matured.'
                }
            else:
                return {
                    'success': False,
                    'message': 'Insufficient balance for withdrawal.'
                }
        
        # For pre-maturity withdrawal, apply 35% penalty on interest
        if amount <= self.base_investment.current_balance:
            # Calculate penalty (35% of accrued interest)
            penalty = self.base_investment.total_interest_earned * Decimal('0.35')
            
            # Reduce balance by amount and penalty
            self.base_investment.current_balance -= amount
            self.base_investment.current_balance -= penalty
            self.base_investment.total_interest_earned -= penalty
            self.base_investment.save()
            
            # Create transaction records
            Transaction.objects.create(
                investment=self.base_investment,
                transaction_type='withdrawal',
                amount=amount,
                description='Senior investment pre-maturity withdrawal'
            )
            
            Transaction.objects.create(
                investment=self.base_investment,
                transaction_type='penalty',
                amount=penalty,
                description='35% penalty on interest due to pre-maturity withdrawal'
            )
            
            return {
                'success': True,
                'message': f'Withdrawal successful, but a penalty of {penalty} (35% of interest) has been applied.',
                'penalty': penalty
            }
        else:
            return {
                'success': False,
                'message': 'Insufficient balance for withdrawal.'
            }


class EarlyStarterInvestment(models.Model):
    """Early Starter investment model for children (0-17 years) - 20% P.A"""
    base_investment = models.OneToOneField(TargetInvestment, on_delete=models.CASCADE, primary_key=True)
    child_name = models.CharField(max_length=100)
    child_date_of_birth = models.DateField()
    parent_name = models.CharField(max_length=100)
    parent_bvn = models.CharField(max_length=11)
    parent_nin = models.CharField(max_length=11)
    birth_certificate = models.FileField(
        upload_to='early_starter/birth_certificates/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    child_passport_photo = models.ImageField(upload_to='early_starter/child_photos/')
    parent_passport_photo = models.ImageField(upload_to='early_starter/parent_photos/')
    parent_id = models.FileField(
        upload_to='early_starter/parent_ids/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    
    def save(self, *args, **kwargs):
        # Validate child's age (0-17 years)
        today = timezone.now().date()
        age = today.year - self.child_date_of_birth.year - (
            (today.month, today.day) < (self.child_date_of_birth.month, self.child_date_of_birth.day)
        )
        
        if age < 0 or age > 17:
            raise ValueError('Child must be between 0-17 years old')
        
        super().save(*args, **kwargs)


class VacayInvestment(models.Model):
    """Vacay investment model - 20% P.A"""
    base_investment = models.OneToOneField(TargetInvestment, on_delete=models.CASCADE, primary_key=True)
    withdrawal_count = models.PositiveIntegerField(default=0)
    has_active_loan = models.BooleanField(default=False)
    management_fee_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0.01)  # 1% default
    
    def save(self, *args, **kwargs):
        # Set minimum deposit validation
        if not self.pk:  # Only for new instances
            # Minimum investment of N50,000
            min_investment = Decimal('50000.00')
            if self.base_investment.amount < min_investment:
                self.base_investment.amount = min_investment
                self.base_investment.save()
        super().save(*args, **kwargs)
    
    def make_withdrawal(self, amount):
        """Process a withdrawal with Vacay-specific rules"""
        if amount <= self.base_investment.current_balance:
            # Any withdrawal leads to loss of interest
            interest_to_forfeit = self.base_investment.total_interest_earned
            
            # Reduce balance by amount and forfeit interest
            self.base_investment.current_balance -= amount
            self.base_investment.current_balance -= interest_to_forfeit
            self.base_investment.total_interest_earned = 0
            self.base_investment.save()
            
            self.withdrawal_count += 1
            self.save()
            
            # Create transaction records
            Transaction.objects.create(
                investment=self.base_investment,
                transaction_type='withdrawal',
                amount=amount,
                description='Vacay investment withdrawal'
            )
            
            Transaction.objects.create(
                investment=self.base_investment,
                transaction_type='interest_loss',
                amount=interest_to_forfeit,
                description='Interest forfeited due to withdrawal'
            )
            
            return {
                'success': True,
                'message': f'Withdrawal successful, but all accrued interest ({interest_to_forfeit}) has been forfeited.',
                'interest_forfeited': interest_to_forfeit
            }
        else:
            return {
                'success': False,
                'message': 'Insufficient balance for withdrawal.'
            }
    
    def request_loan(self, amount):
        """Request a loan against the Vacay investment"""
        # Check if there's already an active loan
        if self.has_active_loan:
            return {
                'success': False,
                'message': 'You already have an active loan against this investment.'
            }
        
        # Check if loan amount is within 60% of saved funds
        max_loan = self.base_investment.current_balance * Decimal('0.60')
        if amount > max_loan:
            return {
                'success': False,
                'message': f'Maximum loan amount cannot exceed 60% of saved funds. Maximum available: {max_loan}'
            }
        
        # Calculate loan processing fee
        processing_fee = amount * Decimal('0.02')  # 2% processing fee
        
        # Create loan record
        loan = VacayLoan.objects.create(
            vacay_investment=self,
            loan_amount=amount,
            processing_fee=processing_fee,
            repayment_deadline=timezone.now().date() + relativedelta(months=6)  # Default to 6 months
        )
        
        self.has_active_loan = True
        self.save()
        
        return {
            'success': True,
            'message': f'Loan approved for {amount}. Processing fee: {processing_fee}.',
            'loan_id': loan.id,
            'repayment_deadline': loan.repayment_deadline
        }


class HiWealthInvestment(models.Model):
    """Hi-Wealth investment model (similar to PiggyVest)"""
    base_investment = models.OneToOneField(TargetInvestment, on_delete=models.CASCADE, primary_key=True)
    is_locked = models.BooleanField(default=True)
    lock_duration = models.IntegerField(help_text="Lock duration in days")
    unlock_date = models.DateField()
    break_lock_penalty = models.DecimalField(max_digits=4, decimal_places=2, default=0.25)  # 25% penalty
    
    def save(self, *args, **kwargs):
        # Calculate unlock date based on lock duration
        if not self.pk:  # Only for new instances
            self.unlock_date = self.base_investment.start_date + timezone.timedelta(days=self.lock_duration)
        super().save(*args, **kwargs)
    
    def make_withdrawal(self, amount):
        """Process a withdrawal with Hi-Wealth-specific rules"""
        today = timezone.now().date()
        
        # Check if the lock period has expired
        if today >= self.unlock_date:
            # Lock expired, allow withdrawal without penalty
            if amount <= self.base_investment.current_balance:
                self.base_investment.current_balance -= amount
                self.base_investment.save()
                
                # Create transaction record
                Transaction.objects.create(
                    investment=self.base_investment,
                    transaction_type='withdrawal',
                    amount=amount,
                    description='Hi-Wealth investment unlocked withdrawal'
                )
                
                return {
                    'success': True,
                    'message': 'Withdrawal successful. Investment lock period has expired.'
                }
            else:
                return {
                    'success': False,
                    'message': 'Insufficient balance for withdrawal.'
                }
        
        # Lock period still active, apply penalty for breaking the lock
        if amount <= self.base_investment.current_balance:
            # Calculate penalty
            penalty = amount * self.break_lock_penalty
            
            # Reduce balance by amount and penalty
            if self.base_investment.current_balance >= (amount + penalty):
                self.base_investment.current_balance -= amount
                self.base_investment.current_balance -= penalty
                self.base_investment.save()
                
                # Create transaction records
                Transaction.objects.create(
                    investment=self.base_investment,
                    transaction_type='withdrawal',
                    amount=amount,
                    description='Hi-Wealth investment early withdrawal (lock broken)'
                )
                
                Transaction.objects.create(
                    investment=self.base_investment,
                    transaction_type='penalty',
                    amount=penalty,
                    description=f'Penalty for breaking lock ({self.break_lock_penalty * 100}%)'
                )
                
                return {
                    'success': True,
                    'message': f'Withdrawal successful, but a penalty of {penalty} ({self.break_lock_penalty * 100}%) has been applied for breaking the lock.',
                    'penalty': penalty
                }
            else:
                return {
                    'success': False,
                    'message': f'Insufficient balance for withdrawal with penalty. Required: {amount + penalty}'
                }
        else:
            return {
                'success': False,
                'message': 'Insufficient balance for withdrawal.'
            }


class VacayLoan(models.Model):
    """Vacay Loan model"""
    vacay_investment = models.ForeignKey(VacayInvestment, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=12, decimal_places=2)
    date_issued = models.DateField(auto_now_add=True)
    repayment_deadline = models.DateField()
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0.02)  # 2% monthly
    amount_repaid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_repaid = models.BooleanField(default=False)
    
    def calculate_payoff_amount(self):
        """Calculate the current payoff amount including interest"""
        today = timezone.now().date()
        months_elapsed = relativedelta(today, self.date_issued).months + 1  # Add 1 for partial months
        
        # Calculate interest
        interest = self.loan_amount * self.interest_rate * months_elapsed
        
        # Total amount due
        payoff_amount = self.loan_amount + interest - self.amount_repaid
        
        return max(payoff_amount, 0)  # Ensure non-negative
    
    def make_repayment(self, amount):
        """Process a loan repayment"""
        payoff_amount = self.calculate_payoff_amount()
        
        if amount >= payoff_amount:
            # Full repayment
            self.amount_repaid = self.loan_amount + (payoff_amount - self.loan_amount)  # Principal + interest
            self.is_repaid = True
            self.vacay_investment.has_active_loan = False
            self.vacay_investment.save()
            self.save()
            
            # Create transaction record
            Transaction.objects.create(
                investment=self.vacay_investment.base_investment,
                transaction_type='loan_repayment',
                amount=amount,
                description='Full loan repayment'
            )
            
            return {
                'success': True,
                'message': f'Loan fully repaid. {amount - payoff_amount} refunded.',
                'refund': max(amount - payoff_amount, 0)
            }
        else:
            # Partial repayment
            self.amount_repaid += amount
            self.save()
            
            # Create transaction record
            Transaction.objects.create(
                investment=self.vacay_investment.base_investment,
                transaction_type='loan_repayment',
                amount=amount,
                description='Partial loan repayment'
            )
            
            remaining = payoff_amount - amount
            return {
                'success': True,
                'message': f'Partial repayment successful. Remaining balance: {remaining}',
                'remaining': remaining
            }


class Transaction(models.Model):
    """Transaction model to track all investment activities"""
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('interest', 'Interest'),
        ('additional_deposit', 'Additional Deposit'),
        ('additional_withdrawal', 'Additional Withdrawal'),
        ('penalty', 'Penalty'),
        ('interest_loss', 'Interest Loss'),
        ('loan_issue', 'Loan Issue'),
        ('loan_repayment', 'Loan Repayment'),
    ]
    
    investment = models.ForeignKey(TargetInvestment, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']


class PaymentCard(models.Model):
    """Payment Card model to store users' card information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_cards')
    card_provider = models.CharField(max_length=50)  # Visa, Mastercard, etc.
    last_four_digits = models.CharField(max_length=4)
    expiry_month = models.CharField(max_length=2)
    expiry_year = models.CharField(max_length=4)
    is_default = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'last_four_digits', 'expiry_month', 'expiry_year']

class HiWealthTargetInvestment(models.Model):
    minimum = models.PositiveBigIntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(100000)),
        null=True
    )
    maximum = models.PositiveBigIntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(2000000)),
        null=True
    )
    
 