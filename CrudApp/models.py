from django.db.models import (Model, CharField, TimeField, DateField,
                              DecimalField, PositiveIntegerField, ForeignKey, DO_NOTHING)
from django.contrib.auth.models import User
from ShopSite.MyShortcuts import MyManager
from decimal import Decimal
from datetime import datetime


class Product(Model):
    objects = MyManager()

    name = CharField(max_length=20)
    price = DecimalField(max_digits=6, decimal_places=2)
    description = CharField(max_length=400)
    count = PositiveIntegerField()

    def __str__(self):
        return f'{self.name} {self.price} {self.description} {self.count}'

    class Meta:
        db_table = 'Product'

    @staticmethod
    def get_inputs_data(request):
        return [
            request.POST.get('name'),
            request.POST.get('price'),
            request.POST.get('description'),
            request.POST.get('count'),
        ]

    @staticmethod
    def record_delete(request):
        delete_id = request.POST.get('delete_id')

        if delete_id:
            Product.objects.filter(id=int(delete_id)).delete()

    @staticmethod
    def update(request, inputs):
        update_id = request.POST.get('update_id')
        name, price, description, count = inputs

        if update_id:
            product = Product.objects.get(id=update_id)

            if name:
                product.name = name
            if price:
                product.price = Decimal(price)
            if description:
                product.description = description
            if count:
                product.count = count

            product.save()

    @staticmethod
    def create(inputs):
        name, price, description, count = inputs

        product = Product(
            name=name,
            price=Decimal(price),
            description=description,
            count=count,
        )
        product.save()
        return product.id


class RecordSave(Model):
    mode = CharField(
        max_length=30,
        choices=(
            ('create', 'create'),
            ('delete', 'delete'),
            ('update', 'update')
        ),
    )
    product_id = PositiveIntegerField()
    name = CharField(max_length=20)
    price = DecimalField(max_digits=6, decimal_places=2)
    description = CharField(max_length=400)
    count = PositiveIntegerField()
    salesmen = ForeignKey(User, on_delete=DO_NOTHING, null=True, blank=True)

    date = DateField()
    time = TimeField()

    def __str__(self):
        time = self.time.__str__()[:-3]
        return f'{self.mode} {self.date} {time} {self.name} {self.price} {self.description} {self.count} '

    class Meta:
        db_table = 'RecordSave'

    def ru_mode(self):
        if self.mode == 'create':
            return 'создано'
        elif self.mode == 'delete':
            return 'удалено'
        elif self.mode == 'update':
            return 'обновлено'

    @staticmethod
    def save_in_history(request):
        price = request.POST.get('price')
        dt = datetime.fromtimestamp(float(request.POST.get('timestamp')))
        record_save = RecordSave()

        record_save.mode = request.POST.get('mode')
        record_save.product_id = int(request.POST.get('product_id'))
        record_save.name = request.POST.get('name')
        record_save.description = request.POST.get('description')
        record_save.count = request.POST.get('count')
        record_save.date = dt.date()
        record_save.time = dt.time()
        record_save.salesmen = request.user
        if price:
            record_save.price = Decimal(price)

        record_save.save()
