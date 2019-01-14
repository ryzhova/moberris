import json

from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from .models import Order


CORRECT_ORDER = {
    "status": "processing",
    "customer_id": 1,
    "orderedpizza_set": [
        {
            "pizza_id": 3,
            "size_id": 1,
            "quantity": 4
        },
        {
            "pizza_id": 2,
            "size_id": 2,
            "quantity": 1
        }
    ]
}

ORDER_WITH_INCORRECT_DATA = {
    "status": "processing",
    "customer_id": "Elen",
    "orderedpizza_set": [
        {
            "pizza_id": 3,
            "size_id": 1,
            "quantity": 4
        },
        {
            "pizza_id": 2,
            "size_id": 2,
            "quantity": 1
        }
    ]
}

INCORRECT_ORDER = {
    "status": "processing",
    "customer_id": 1,
    "orderedpizza_set": [
    ]
}

CHANGED_ORDER = {
  "status": "new",
  "customer_id": 1,
  "orderedpizza_set": [
    {
      "id": 8,
      "pizza_id": 3,
      "size_id": 1,
      "quantity": 2
    },
    {
      "pizza_id": 2,
      "size_id": 2,
      "quantity": 3
    },
    {
      "id": 18,
      "pizza_id": 1,
      "size_id": 2,
      "quantity": 4
    }
  ]
}

IMMUTABLE_STATUS_ORDER = {
  "status": "processing",
  "customer_id": 1,
  "orderedpizza_set": [
    {
      "id": 8,
      "pizza_id": 3,
      "size_id": 1,
      "quantity": 2
    },
    {
      "pizza_id": 2,
      "size_id": 2,
      "quantity": 3
    },
    {
      "id": 18,
      "pizza_id": 1,
      "size_id": 2,
      "quantity": 4
    }
  ]
}


class OrderAPITest(TestCase):
    fixtures = ['test_data.json', ]

    def setUp(self):
        self.client = APIClient()

    def test_get_all_orders(self):
        response = self.client.get(reverse('order-list'))

        self.assertEqual(response.status_code, 200)

        response_ids = {int(item['id']) for item in response.data}
        db_ids = {item.id for item in Order.objects.all()}
        self.assertEqual(response_ids, db_ids)

    def test_get_orders_by_customer(self):
        params = {'customer_id': 2}
        response = self.client.get(
            '{}?{}'.format(reverse('order-list'), urlencode(params))
        )

        self.assertEqual(response.status_code, 200)

        response_ids = {item['id'] for item in response.data}
        db_ids = {item.id for item in Order.objects.filter(
            customer_id=params['customer_id']
        )}
        self.assertEqual(response_ids, db_ids)

    def test_get_orders_by_order_status(self):
        params = {'status': 'new'}
        response = self.client.get(
            '{}?{}'.format(reverse('order-list'), urlencode(params)),
        )

        self.assertEqual(response.status_code, 200)

        response_ids = {int(item['id']) for item in response.data}
        db_ids = {item.id for item in Order.objects.filter(
            status=params['status']
        )}
        self.assertEqual(response_ids, db_ids)

    def test_get_order(self):
        order_id = 2
        response = self.client.get(reverse('order-detail', args=[order_id]))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data['id'], order_id)

        customer_from_db = Order.objects.get(id=order_id).customer.id
        self.assertEqual(response.data['customer_id'], customer_from_db)

    def test_get_nonexistent_order(self):
        order_id = 3434
        response = self.client.get(reverse('order-detail', args=[order_id]))

        self.assertEqual(response.status_code, 404)

    def test_create_order(self):
        response = self.client.post(
            reverse('order-list'),
            data=json.dumps(CORRECT_ORDER),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)

        response_id = response.data['id']
        self.assertTrue(Order.objects.filter(id=response_id).exists())

    def test_create_order_with_incorrect_data(self):
        response = self.client.post(
            reverse('order-list'),
            data=json.dumps(ORDER_WITH_INCORRECT_DATA),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

    def test_create_order_without_pizza(self):
        response = self.client.post(
            reverse('order-list'),
            data=json.dumps(INCORRECT_ORDER),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

    def test_change_order(self):
        order_id = 4

        changed_pizza_quantity = Order.objects.get(
            id=order_id).orderedpizza_set.get(id=8).quantity
        self.assertNotEqual(
            CHANGED_ORDER['orderedpizza_set'][0]['quantity'],
            changed_pizza_quantity,
        )

        response = self.client.put(
            reverse('order-detail', args=[order_id]),
            data=json.dumps(CHANGED_ORDER),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)

        changed_pizza_quantity = Order.objects.get(
            id=order_id).orderedpizza_set.get(id=8).quantity
        self.assertEqual(
            CHANGED_ORDER['orderedpizza_set'][0]['quantity'],
            changed_pizza_quantity,
        )

    def test_change_order_with_immutable_status(self):
        order_id = 2
        response = self.client.put(
            reverse('order-detail', args=[order_id]),
            data=json.dumps(IMMUTABLE_STATUS_ORDER),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

    def test_change_nonexistent_order(self):
        order_id = 2323
        response = self.client.put(
            reverse('order-detail', args=[order_id]),
            data=json.dumps(CHANGED_ORDER),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_order(self):
        order_id = 2

        self.assertTrue(Order.objects.filter(id=order_id).exists())

        response = self.client.delete(reverse('order-detail', args=[order_id]))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Order.objects.filter(id=order_id).exists())

    def test_delete_nonexistent_order(self):
        order_id = 2434
        response = self.client.delete(reverse('order-detail', args=[order_id]))

        self.assertEqual(response.status_code, 404)
