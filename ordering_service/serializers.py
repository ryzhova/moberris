from rest_framework import serializers

from .models import Order, Customer, OrderedPizza


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('id', 'name', 'phone_number')


class OrderedPizzaListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        ordered_pizza_mapping = {pizza.id: pizza for pizza in instance}

        result = []
        for data in validated_data:
            ordered_pizza_id = data.get('id')
            if ordered_pizza_id:
                pizza = ordered_pizza_mapping.pop(ordered_pizza_id, None)
                if pizza:
                    result.append(self.child.update(pizza, data))
            else:
                result.append(self.child.create(data))

        for pizza in ordered_pizza_mapping.values():
            pizza.delete()
        return result


class OrderedPizzaSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    size_id = serializers.IntegerField()
    size = serializers.StringRelatedField(many=False, read_only=True)
    pizza_id = serializers.IntegerField()
    pizza = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = OrderedPizza
        list_serializer_class = OrderedPizzaListSerializer
        fields = ('id', 'pizza_id', 'pizza', 'size_id', 'size', 'quantity',)

    def create(self, validated_data):
        return OrderedPizza(**validated_data)


class OrderSerializer(serializers.ModelSerializer):
    orderedpizza_set = OrderedPizzaSerializer(many=True, allow_empty=False)
    customer = CustomerSerializer(many=False, read_only=True)
    customer_id = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ('id', 'status', 'customer_id', 'customer', 'orderedpizza_set')

    def run_validators(self, *args, **kwargs):
        if self.instance and not self.instance.is_mutable:
            raise serializers.ValidationError(
                'Delivered order can not be changed.'
            )
        return super(OrderSerializer, self).run_validators(*args, **kwargs)

    def create(self, validated_data):
        ordered_pizza_data = validated_data.pop('orderedpizza_set')
        ordered_pizza_set = self.fields['orderedpizza_set'].create(
            ordered_pizza_data
        )
        order = Order(**validated_data)
        order.save()
        order.orderedpizza_set.add(*ordered_pizza_set, bulk=False)
        return order

    def update(self, instance, validated_data):
        ordered_pizza_data = validated_data.pop('orderedpizza_set')

        ordered_pizza_set = self.fields['orderedpizza_set'].update(
            instance.orderedpizza_set.all(), ordered_pizza_data)
        instance.__dict__.update(validated_data)

        instance.orderedpizza_set.set(ordered_pizza_set, bulk=False)
        instance.save()
        return instance
