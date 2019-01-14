from django.db import models


ORDER_STATUS_CHOICES = (
    ('new', 'New'),
    ('processing', 'Processing'),
    ('delivered', 'Delivered'),
)

IMMUTABLE_STATUSES = [
    'delivered',
]


class Customer(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.name


# it allowes to add new sizes without release
class PizzaSize(models.Model):
    size = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.size


class Pizza(models.Model):
    title = models.CharField(max_length=100)
    possible_sizes = models.ManyToManyField(PizzaSize)

    def __str__(self):
        return self.title


class Order(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.PROTECT)
    status = models.CharField(max_length=15, choices=ORDER_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Order {}'.format(self.id)

    @property
    def is_mutable(self):
        return self.status not in IMMUTABLE_STATUSES


class OrderedPizza(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, on_delete=models.PROTECT)
    size = models.ForeignKey(PizzaSize, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
