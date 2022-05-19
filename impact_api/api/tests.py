from datetime import date
import json
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.admin.sites import AdminSite
from currency_converter import CurrencyConverter
from api.admin import EvaluationAdmin
from api import serializers
from api.models import (
    Allotment, Evaluation, MaxImpactFundGrant, Charity, Intervention)

def create_charity(charity_name='Skynet', abbreviation='SN'):
    return Charity.objects.create(
        charity_name=charity_name, abbreviation=abbreviation)

def create_intervention(
        short_description='Distributing killer robots',
        long_description='Reducing the risk from misaligned natural intelligence',
        short_description_no='Døstrøbøtøng køllør røbøts',
        long_description_no='Rødøcøng thø røsk frøm møsøløgnød nøtørøl øntølløgønce'):
    return Intervention.objects.create(
        short_description=short_description,
        long_description=long_description,
        short_description_no=short_description_no,
        long_description_no=long_description_no)

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

class CharityModelTests(TestCase):
    def test_string_representation(self):
        charity = Charity(charity_name="Evil Henchperson's Union")
        self.assertEqual(str(charity), "Evil Henchperson's Union")

    def test_abbreviation_upcasing_pre_save(self):
        '''Ensure Charity abbreviations are properly upcased on save'''
        charity = Charity(charity_name='Centre for Effective Despotism',
                          abbreviation='ced')
        charity.save()
        self.assertEqual(charity.abbreviation, 'CED')

class MaxImpactFundGrantModelTests(TestCase):
    def test_string_representation(self):
        grant = MaxImpactFundGrant(start_year=2015, start_month=6)
        self.assertEqual(str(grant), '2015-6')

    def test_validates_current_year_in_range(self):
        '''Ensure current_year is between 2000 and now'''
        grant = MaxImpactFundGrant(start_year=1999)
        try:
            grant.clean_fields()
        except ValidationError as e:
            self.assertIn('must be the year of a Givewell evalution', e.message_dict['start_year'])

        grant.start_year=2000
        try:
            grant.clean_fields()
        except ValidationError as e:
            self.assertFalse('start_year' in e.message_dict)

        this_year = date.today().year
        grant.start_year = this_year
        try:
            grant.clean_fields()
        except ValidationError as e:
            self.assertFalse('start_year' in e.message_dict)

        grant.start_year = this_year + 1
        try:
            grant.clean_fields()
        except ValidationError as e:
            self.assertIn('must be the year of a Givewell evalution', e.message_dict['start_year'])

    def test_validates_current_month_is_a_month(self):
        '''Ensure current_month is between 1 and 12'''
        grant = MaxImpactFundGrant(start_month=0)
        try:
            grant.clean_fields()
        except ValidationError as e:
            self.assertIn('month must be a number from 1-12', e.message_dict['start_month'])

        grant.start_month = 1
        try:
            grant.clean_fields()
        except ValidationError as e:
            self.assertFalse('start_month' in e.message_dict)

        grant.start_month = 12
        try:
            grant.clean_fields()
        except ValidationError as e:
            self.assertFalse('start_month' in e.message_dict)

        grant.start_month = 13
        try:
            grant.clean_fields()
        except ValidationError as e:
            self.assertIn('month must be a number from 1-12', e.message_dict['start_month'])

class InterventionModelTests(TestCase):
    def test_string_representation(self):
        intervention = Intervention(short_description='Toby Ord clones')
        self.assertEqual(str(intervention), 'Toby Ord clones')

class AllotmentModelTests(TestCase):
    def test_string_representation(self):
        charity = Charity(charity_name='Givewell Retirement Fund')
        allotment = Allotment(sum_in_cents=1234567890, charity=charity)

        self.assertEqual(str(allotment), '$12345678.9 to Givewell Retirement Fund')

    def test_calculates_cents_per_output_upward_correctly(self):
        """
            cents_per_output() returns the correct integer when
            rounding up
        """
        allotment = Allotment(sum_in_cents=5, number_outputs_purchased=3)
        self.assertEqual(allotment.cents_per_output(), 1.6666666666666667)

    def test_calculates_cents_per_output_downward_correctly(self):
        """
            cents_per_output() returns the correct integer when
            rounding down
        """
        allotment = Allotment(sum_in_cents=5, number_outputs_purchased=4)
        self.assertEqual(allotment.cents_per_output(), 1.25)

class EvaluationModelTests(TestCase):
    def test_string_representation(self):
        charity = Charity(charity_name = 'Bob')
        evaluation = Evaluation(start_year=2015, start_month=6, charity=charity)
        self.assertEqual(str(evaluation), 'Bob as of 2015-6')

    def test_validates_current_year_in_range(self):
        '''Ensure current_year is between 2000 and now'''
        evaluation = Evaluation(start_year=1999)
        try:
            evaluation.clean_fields()
        except ValidationError as e:
            self.assertIn('must be the year of a Givewell evalution', e.message_dict['start_year'])

        evaluation.start_year=2000
        try:
            evaluation.clean_fields()
        except ValidationError as e:
            self.assertFalse('start_year' in e.message_dict)

        this_year = date.today().year
        evaluation.start_year = this_year
        try:
            evaluation.clean_fields()
        except ValidationError as e:
            self.assertFalse('start_year' in e.message_dict)

        evaluation.start_year = this_year + 1
        try:
            evaluation.clean_fields()
        except ValidationError as e:
            self.assertIn('must be the year of a Givewell evalution', e.message_dict['start_year'])

    def test_validates_current_month_is_a_month(self):
        '''Ensure current_month is between 1 and 12'''
        evaluation = Evaluation(start_month=0)
        try:
            evaluation.clean_fields()
        except ValidationError as e:
            self.assertIn('month must be a number from 1-12', e.message_dict['start_month'])

        evaluation.start_month = 1
        try:
            evaluation.clean_fields()
        except ValidationError as e:
            self.assertFalse('start_month' in e.message_dict)

        evaluation.start_month = 12
        try:
            evaluation.clean_fields()
        except ValidationError as e:
            self.assertFalse('start_month' in e.message_dict)

        evaluation.start_month = 13
        try:
            evaluation.clean_fields()
        except ValidationError as e:
            self.assertIn('month must be a number from 1-12', e.message_dict['start_month'])

class EvaluationAdminTests(TestCase):
    def test_custom_admin_display_methods(self):
        charity = Charity(abbreviation='JAEG', charity_name='Against Vensusia Foundation')
        intervention = Intervention(
            short_description='Giant mechs',
            long_description='Preemptive defensive planning against giant Venusian monsters')
        evaluation = Evaluation(charity=charity, intervention=intervention)
        evaluation_admin = EvaluationAdmin(model=Evaluation, admin_site=AdminSite())
        self.assertEqual(evaluation_admin.charity_abbreviation(evaluation=evaluation), 'JAEG')
        self.assertEqual(evaluation_admin.long_description(evaluation=evaluation),
            'Preemptive defensive planning against giant Venusian monsters')
        self.assertEqual(evaluation_admin.charity(evaluation=evaluation),
                         'Against Vensusia Foundation')
        self.assertEqual(evaluation_admin.intervention(evaluation=evaluation), 'Giant mechs')

class EvaluationViewTests(TestCase):
    def setUp(self):
        if self._testMethodName != 'test_evaluation_not_found':
            self.eval_1 = create_evaluation()

    def test_evaluation_not_found(self):
        query = reverse('evaluations') + '?start_year=2016'
        content = json.loads(self.client.get(query).content)
        self.assertEqual(
            content['error'], 'No evaluation found with those parameters')

    def test_one_evaluation(self):
        '''Check output from a single evaluation'''
        response = self.client.get(reverse('evaluations'))
        content = json.loads(response.content)
        self.assertEqual(content['evaluations'],
            [{'id': 1,
              'start_month': 12,
              'start_year': 2010,
              'cents_per_output': 100,
              'converted_cost_per_output': 1.0,
              'currency': 'USD',
              'language': 'en',
              'charity': {
                  'abbreviation': 'SN', 'charity_name': 'Skynet', 'id': 1},
              'intervention': {
                  'id': 1,
                  'short_description': 'Distributing killer robots',
                  'long_description': (
                      'Reducing the risk from misaligned '
                      'natural intelligence')}}])

    def test_filtering_by_charity(self):
        '''Ensure that specifying charities in views returns only those charities'''
        charity = create_charity(
            charity_name='Impossible Meat', abbreviation='IM')
        intervention = create_intervention(
            short_description='Media training',
            long_description='Teaching multiple people to communicate with the dead')

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
        ''' Ensure specifying start_year/end_year in views gets only evaluations from/before
        that year'''
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
        ''' Ensure specifying start_month/end_month in views gets only evaluations from/before
        that month'''
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

    def test_currency_defaults(self):
        '''Ensure query with language and no currency defaults correctly'''
        query_1 = reverse('evaluations')
        content_1 = json.loads(self.client.get(query_1).content)
        query_2 = reverse('evaluations') + '?language=no'
        content_2 = json.loads(self.client.get(query_2).content)
        self.assertEqual(content_1['evaluations'][0]['currency'], 'USD')
        self.assertEqual(content_2['evaluations'][0]['currency'], 'EUR')

    def test_specified_language(self):
        '''Ensure queries specifying language get the correct language'''
        query = reverse('evaluations') + '?language=no'
        content = json.loads(self.client.get(query).content)
        self.assertEqual(content['evaluations'][0]['intervention']['short_description'],
                         'Døstrøbøtøng køllør røbøts')
        self.assertEqual(content['evaluations'][0]['intervention']['long_description'],
                         'Rødøcøng thø røsk frøm møsøløgnød nøtørøl øntølløgønce')

    def test_specified_currency(self):
        '''Ensure queries specifying currency get the correct currency'''
        original_cost_in_cents = Evaluation.objects.all()[0].cents_per_output
        expected_conversion = CurrencyConverter().convert(
            original_cost_in_cents / 100, 'USD', 'EUR')
        query = reverse('evaluations') + '?currency=EUR'
        content = json.loads(self.client.get(query).content)
        evaluation = content['evaluations'][0]
        self.assertEqual(evaluation['currency'], 'EUR')
        self.assertEqual(evaluation['converted_cost_per_output'], expected_conversion)

class MaxImpactFundGrantIndexViewTests(TestCase):
    def setUp(self):
        if self._testMethodName != 'test_grant_not_found':
            grant_1 = create_grant()
            self.allotment_1 = create_allotment(
                max_impact_fund_grant=grant_1)

    def test_grant_not_found(self):
        query = reverse('max_impact_fund_grants') + '?start_year=2016'
        content = json.loads(self.client.get(query).content)
        self.assertEqual(
            content['error'], 'No grant found with those parameters')

    def test_one_grant(self):
        '''Check output from a single grant'''
        response = self.client.get(reverse('max_impact_fund_grants'))
        content = json.loads(response.content)
        self.assertEqual(content['max_impact_fund_grants'],
            [{'id': 1,
              'start_year': 2015,
              'start_month': 6,
              'language': 'en',
              'allotment_set': [{
                  'id': 1,
                  'converted_sum': 99.99,
                  'currency': 'USD',
                  'sum_in_cents': 9999,
                  'converted_cost_per_output': 0.045,
                  'number_outputs_purchased': 2222,
                  'intervention': {
                      'id': 1,
                      'long_description': 'Reducing the risk from misaligned natural intelligence',
                      'short_description': 'Distributing killer robots'},
                  'charity': {
                      'id': 1,
                      'charity_name': 'Skynet',
                      'abbreviation': 'SN'}}]}])

    def test_filtering_by_year(self):
        '''Ensure specifying start_year/end_year in views gets only grants from/before
        that year'''
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
        self.assertEqual(
            content_1['max_impact_fund_grants'][0]['start_year'], 2016)
        self.assertEqual(
            content_2['max_impact_fund_grants'][0]['start_year'], 2015)

    def test_filtering_within_year(self):
        '''Ensure specifying start_month/end_month in views gets only grants from/before
        that month'''
        grant_2 = create_grant(start_month=1)
        query_1 = reverse('max_impact_fund_grants') + '?start_month=5'
        content_1 = json.loads(self.client.get(query_1).content)
        query_2 = reverse('max_impact_fund_grants') + '?end_month=5'
        content_2 = json.loads(self.client.get(query_2).content)
        self.assertEqual(len(content_1['max_impact_fund_grants']), 1)
        self.assertEqual(len(content_2['max_impact_fund_grants']), 1)
        self.assertEqual(
            content_1['max_impact_fund_grants'][0]['start_month'], 6)
        self.assertEqual(
            content_2['max_impact_fund_grants'][0]['start_month'], 1)

    def test_currency_defaults(self):
        '''Ensure query with language and no currency defaults correctly'''
        query_1 = reverse('max_impact_fund_grants')
        content_1 = json.loads(self.client.get(query_1).content)
        query_2 = reverse('max_impact_fund_grants') + '?language=no'
        content_2 = json.loads(self.client.get(query_2).content)
        self.assertEqual(content_1['max_impact_fund_grants'][0]['allotment_set'][0]['currency'], 'USD')
        self.assertEqual(content_2['max_impact_fund_grants'][0]['allotment_set'][0]['currency'], 'EUR')

    def test_specified_language(self):
        '''Ensure queries specifying language get the correct language'''
        query = reverse('max_impact_fund_grants') + '?language=no'
        content = json.loads(self.client.get(query).content)
        intervention = content['max_impact_fund_grants'][0]['allotment_set'][0]['intervention']
        self.assertEqual(intervention['short_description'],
                         'Døstrøbøtøng køllør røbøts')
        self.assertEqual(intervention['long_description'],
                         'Rødøcøng thø røsk frøm møsøløgnød nøtørøl øntølløgønce')

    def test_specified_currency(self):
        '''Ensure queries specifying currency get the correct currency'''
        original_sum_in_cents = Allotment.objects.all()[0].sum_in_cents
        expected_conversion = CurrencyConverter().convert(
            original_sum_in_cents / 100, 'USD', 'EUR')
        query = reverse('max_impact_fund_grants') + '?currency=EUR'
        content = json.loads(self.client.get(query).content)
        allotment = content['max_impact_fund_grants'][0]['allotment_set'][0]
        self.assertEqual(allotment['currency'], 'EUR')
        self.assertEqual(allotment['converted_sum'], expected_conversion)

