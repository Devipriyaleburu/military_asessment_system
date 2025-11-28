from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Base(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('commander', 'Base Commander'),
        ('logistics', 'Logistics Officer'),
    )
    role = models.CharField(max_length=20, choices=ROLES)
    base = models.ForeignKey(Base, on_delete=models.SET_NULL, null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class Asset(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    base = models.ForeignKey(Base, on_delete=models.CASCADE)
    opening_balance = models.IntegerField(default=0)
    closing_balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.base.name})"

    @property
    def net_movement(self):
        purchases = self.purchase_set.aggregate(total=models.Sum('quantity'))['total'] or 0
        transfers_in = Transfer.objects.filter(to_base=self.base, asset=self).aggregate(total=models.Sum('quantity'))['total'] or 0
        transfers_out = Transfer.objects.filter(from_base=self.base, asset=self).aggregate(total=models.Sum('quantity'))['total'] or 0
        return purchases + transfers_in - transfers_out

    @property
    def assigned(self):
        return self.assignment_set.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def expended(self):
        return self.assignment_set.aggregate(total=models.Sum('expended'))['total'] or 0

    def update_closing_balance(self):
        self.closing_balance = self.opening_balance + self.net_movement - self.expended
        self.save()

class Purchase(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateField(auto_now_add=True)

class Transfer(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    from_base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='from_base')
    to_base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='to_base')
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Assignment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    personnel = models.CharField(max_length=100)
    quantity = models.IntegerField()
    expended = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)

class Log(models.Model):
    action = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
