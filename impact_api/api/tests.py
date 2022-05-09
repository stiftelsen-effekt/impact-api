from django.test import TestCase

from .models import Allotment

class AllotmentModelTests(TestCase):
    def test_rounds_cents_per_output_upward_correctly(self):
        """
            Returns an integer value for number of cents per output
        """
        allotment = Allotment(sum_in_cents=5, number_outputs_purchased=3)
        self.assertIs(allotment.rounded_cents_per_output(), 2)

    def test_rounds_cents_per_output_downward_correctly(self):
        """
            Returns an integer value for number of cents per output
        """
        allotment = Allotment(sum_in_cents=5, number_outputs_purchased=4)
        self.assertIs(allotment.rounded_cents_per_output(), 1)

# Create your tests here.
