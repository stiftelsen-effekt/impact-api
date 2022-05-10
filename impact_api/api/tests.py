from django.test import TestCase
from django.urls import reverse
import json
# from unittest.mock import MagicMock

from .models import (
    Allotment, Evaluation, MaxImpactFundGrant, Charity, Intervention)

def create_charity(charity_name='Skynet', abbreviation='SN') -> Charity:
    return Charity.objects.create(
        charity_name=charity_name, abbreviation=abbreviation)

def create_intervention(
        short_output_description='Distributing killer robots',
        long_output_description=('Working to reduce the risk from '
                                 'misaligned natural intelligence')) -> Intervention:
    return Intervention.objects.create(
        short_output_description=short_output_description,
        long_output_description=long_output_description)

def create_evaluation(start_year=2010, start_month=12, cents_per_output=100,
                      charity=None, intervention=None):
    charity = charity or create_charity()
    intervention = intervention or create_intervention()
    return Evaluation.objects.create(
        start_month=start_month, start_year=start_year,
        cents_per_output=cents_per_output, charity=charity,
        intervention=intervention)

class AllotmentModelTests(TestCase):
    def test_rounds_cents_per_output_upward_correctly(self):
        """
            rounded_cents_per_output() returns the correct integer when
            rounding up
        """
        allotment = Allotment(sum_in_cents=5, number_outputs_purchased=3)
        self.assertIs(allotment.rounded_cents_per_output(), 2)

    def test_rounds_cents_per_output_downward_correctly(self):
        """
            rounded_cents_per_output() returns the correct integer when
            rounding down
        """
        allotment = Allotment(sum_in_cents=5, number_outputs_purchased=4)
        self.assertIs(allotment.rounded_cents_per_output(), 1)

class EvaluationViewTests(TestCase):
    def test_no_evaluations(self):
        response = self.client.get(reverse('evaluations'))
        self.assertIs(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['evaluations'], [])

    def test_one_evaluation(self):
        create_evaluation()
        response = self.client.get(reverse('evaluations'))
        content = json.loads(response.content)
        self.assertEqual(content['evaluations'],
            [{'cents_per_output': 100,
              'charity': {
                  'abbreviation': 'SN', 'charity_name': 'Skynet', 'id': 1},
              'id': 1,
              'intervention': {
                  'id': 1,
                  'short_output_description': 'Distributing killer robots',
                  'long_output_description': (
                      'Working to reduce the risk from misaligned '
                      'natural intelligence')},
              'start_month': 12,
              'start_year': 2010}])

    def test_filtering_by_charity(self):
        create_evaluation()
        charity = create_charity(
            charity_name='Impossible Meat', abbreviation='IM')
        intervention = create_intervention(
            long_output_description='DNA cloning from burgers',
            short_output_description='Bringing the original animal back')
        create_evaluation(charity=charity, intervention=intervention)
        query_1 = reverse('evaluations') + '?charity_abbreviation=im'
        content_1 = json.loads(self.client.get(query_1).content)
        query_2 = reverse('evaluations') + '?charity_abbreviation=sn'
        content_2 = json.loads(self.client.get(query_2).content)
        query_3 = reverse('evaluations')
        content_3 = json.loads(self.client.get(query_3).content)
        self.assertEqual(len(content_1['evaluations']), 1)
        self.assertEqual(len(content_2['evaluations']), 1)
        self.assertEqual(len(content_3['evaluations']), 2)
        self.assertEqual(
            content_1['evaluations'][0]['charity']['charity_name'],
            'Impossible Meat')
        self.assertEqual(
            content_2['evaluations'][0]['charity']['charity_name'],
            'Skynet')

    def test_filtering_by_year(self):
        eval_1 = create_evaluation()
        eval_2 = create_evaluation(
            charity=eval_1.charity, intervention=eval_1.intervention,
            start_year=2011)
        query_1 = reverse('evaluations') + '?start_year=2011'
        content_1 = json.loads(self.client.get(query_1).content)
        query_2 = reverse('evaluations') + '?end_year=2010'
        content_2 = json.loads(self.client.get(query_2).content)
        self.assertEqual(len(content_1), 1)
        self.assertEqual(len(content_2), 1)
        self.assertEqual(
            content_1['evaluations'][0]['start_year'],
            2011)
        self.assertEqual(
            content_2['evaluations'][0]['start_year'],
            2010)

    def test_filtering_within_year(self):
        eval_1 = create_evaluation()
        eval_2 = create_evaluation(
            charity=eval_1.charity, intervention=eval_1.intervention,
            start_month=1)
        query_1 = reverse('evaluations') + '?start_month=6'
        content_1 = json.loads(self.client.get(query_1).content)
        query_2 = reverse('evaluations') + '?end_month=6'
        content_2 = json.loads(self.client.get(query_2).content)
        self.assertEqual(len(content_1), 1)
        self.assertEqual(len(content_2), 1)
        self.assertEqual(
            content_1['evaluations'][0]['start_month'],
            12)
        self.assertEqual(
            content_2['evaluations'][0]['start_month'],
            1)


class MaxImpactFundGrantIndexViewTests(TestCase):
    def test_no_evaluations(self):
        response = self.client.get(reverse('max_impact_fund_grants'))
        self.assertIs(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['max_impact_fund_grants'], [])



# Create your tests here.
