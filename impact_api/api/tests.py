from django.test import TestCase
from django.urls import reverse
import json
# from unittest.mock import MagicMock

from .models import (
    Allotment, Evaluation, MaxImpactFundGrant, Charity, Intervention)

def create_charity(charity_name='Skynet', abbreviation='SN'):
    return Charity.objects.create(
        charity_name=charity_name, abbreviation=abbreviation)

def create_intervention(
        short_output_description='Distributing killer robots',
        long_output_description=('Working to reduce the risk from '
                                 'misaligned natural intelligence')):
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

def create_grant(start_year=2015, start_month=6) -> MaxImpactFundGrant:
    return MaxImpactFundGrant.objects.create(
        start_year=start_year, start_month=start_month)

def create_allotment(
    sum_in_cents=9999, number_outputs_purchased=2222,
    charity=None, intervention=None, max_impact_fund_grant=None):
    charity = charity or create_charity()
    intervention = intervention or create_intervention()
    max_impact_fund_grant = max_impact_fund_grant or create_grant()
    return Allotment.objects.create(
        sum_in_cents=sum_in_cents,
        number_outputs_purchased=number_outputs_purchased,
        charity=charity, intervention=intervention,
        max_impact_fund_grant=max_impact_fund_grant)

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
    def setUp(self):
        if self._testMethodName != 'test_no_evaluations':
            self.eval_1 = create_evaluation()

    def test_no_evaluations(self):
        response = self.client.get(reverse('evaluations'))
        self.assertIs(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['evaluations'], [])

    def test_one_evaluation(self):
        response = self.client.get(reverse('evaluations'))
        content = json.loads(response.content)
        self.assertEqual(content['evaluations'],
            [{'id': 1,
              'cents_per_output': 100,
              'start_month': 12,
              'start_year': 2010,
              'charity': {
                  'abbreviation': 'SN', 'charity_name': 'Skynet', 'id': 1},
              'intervention': {
                  'id': 1,
                  'short_output_description': 'Distributing killer robots',
                  'long_output_description': (
                      'Working to reduce the risk from misaligned '
                      'natural intelligence')}}])

    def test_filtering_by_charity(self):
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
        create_evaluation(
            charity=self.eval_1.charity,
            intervention=self.eval_1.intervention,
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
        create_evaluation(
            charity=self.eval_1.charity,
            intervention=self.eval_1.intervention,
            start_month=1)
        query_1 = reverse('evaluations') + '?start_month=6'
        content_1 = json.loads(self.client.get(query_1).content)
        query_2 = reverse('evaluations') + '?end_month=6'
        content_2 = json.loads(self.client.get(query_2).content)
        self.assertEqual(len(content_1['evaluations']), 1)
        self.assertEqual(len(content_2['evaluations']), 1)
        self.assertEqual(content_1['evaluations'][0]['start_month'], 12)
        self.assertEqual(content_2['evaluations'][0]['start_month'], 1)


class MaxImpactFundGrantIndexViewTests(TestCase):
    def setUp(self):
        if self._testMethodName != 'test_no_grants':
            grant_1 = create_grant()
            self.allotment_1 = create_allotment(
                max_impact_fund_grant=grant_1)

    def test_no_grants(self):
        response = self.client.get(reverse('max_impact_fund_grants'))
        self.assertIs(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['max_impact_fund_grants'], [])

    def test_one_grant(self):
        response = self.client.get(reverse('max_impact_fund_grants'))
        content = json.loads(response.content)
        self.assertEqual(content['max_impact_fund_grants'],
            [{'id': 1,
              'start_year': 2015,
              'start_month': 6,
              'allotment_set': [{
                  'id': 1,
                  'cents_per_output': 4,
                  'sum_in_cents': 9999,
                  'number_outputs_purchased': 2222,
                  'charity': {
                      'id': 1,
                      'charity_name': 'Skynet',
                      'abbreviation': 'SN'},
                  'intervention': {
                      'id': 1,
                      'short_output_description': 'Distributing killer robots',
                      'long_output_description': ('Working to reduce the '
                          'risk from misaligned natural intelligence')}}]}])

    def test_filtering_by_year(self):
        grant_2 = create_grant(start_year=2016)
        query_1 = reverse('max_impact_fund_grants') + '?start_year=2016'
        content_1 = json.loads(self.client.get(query_1).content)
        query_2 = reverse('max_impact_fund_grants') + '?end_year=2015'
        content_2 = json.loads(self.client.get(query_2).content)
        query_3 = reverse('max_impact_fund_grants')
        content_3 = json.loads(self.client.get(query_3).content)
        self.assertEqual(len(content_1['max_impact_fund_grants']), 1)
        self.assertEqual(len(content_2['max_impact_fund_grants']), 1)
        self.assertEqual(len(content_3['max_impact_fund_grants']), 2)
        self.assertEqual(content_1['max_impact_fund_grants'][0]['start_year'], 2016)
        self.assertEqual(content_2['max_impact_fund_grants'][0]['start_year'], 2015)

    def test_filtering_within_year(self):
        grant_2 = create_grant(start_month=1)
        query_1 = reverse('max_impact_fund_grants') + '?start_month=5'
        content_1 = json.loads(self.client.get(query_1).content)
        query_2 = reverse('max_impact_fund_grants') + '?end_month=5'
        content_2 = json.loads(self.client.get(query_2).content)
        self.assertEqual(len(content_1['max_impact_fund_grants']), 1)
        self.assertEqual(len(content_2['max_impact_fund_grants']), 1)
        self.assertEqual(content_1['max_impact_fund_grants'][0]['start_month'], 6)
        self.assertEqual(content_2['max_impact_fund_grants'][0]['start_month'], 1)



# Create your tests here.
