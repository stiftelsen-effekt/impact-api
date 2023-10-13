from datetime import date
import json
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.admin.sites import AdminSite
from currency_converter import CurrencyConverter
from api.admin import EvaluationAdmin, AllotmentAdmin
from api import serializers
from api.models import (
    Allotment, Evaluation, MaxImpactFundGrant, Charity, Intervention, AllGrantsFundGrant)
from freezegun import freeze_time
# Freeze time on tests that hit the currency converter so that the tests
# don't grab external ECB data

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
                      cents_per_output_lower_bound = 1, cents_per_output_upper_bound=9**9,
                      comment='Killer robots will also generate many jobs',
                      source_name='Political Tesseract', source_url='https://www.youtube.com/watch?v=tSEOXRLSpVc',
                      charity=None, intervention=None):
    charity = charity or create_charity()
    intervention = intervention or create_intervention()
    return Evaluation.objects.create(
        start_month=start_month, start_year=start_year,
        cents_per_output=cents_per_output,
        cents_per_output_lower_bound=cents_per_output_lower_bound,
        cents_per_output_upper_bound=cents_per_output_upper_bound,
        comment=comment, charity=charity, intervention=intervention,
        source_name=source_name, source_url=source_url)

def create_grant(type='max_impact_fund_grant', start_year=2015, start_month=6) -> 'Some type of grant':
    dates = {
        'start_year': start_year,
        'start_month': start_month,
    }
    if type == 'all_grants_fund_grant':
        return AllGrantsFundGrant.objects.create(
            **dates)
    elif type == 'max_impact_fund_grant':
        return MaxImpactFundGrant.objects.create(
            **dates)
    else:
        raise 'Invalid grant type'

def create_allotment(
    grant, sum_in_cents=9999, number_outputs_purchased=2222,
    charity=None, intervention=None, number_outputs_purchased_lower_bound=0,
    number_outputs_purchased_upper_bound=None, source_name='Hollywood scriptwriters',
    source_url='https://www.darkhorizons.com/michael-bay-talks-his-biggest-explosion/',
    comment='May benefit from further RCTs'):
    charity = charity or create_charity()

    intervention = intervention or create_intervention()
    params = {
        'sum_in_cents': sum_in_cents, 'number_outputs_purchased': number_outputs_purchased,
        'charity': charity, 'intervention': intervention, 'sum_in_cents': sum_in_cents,
        'number_outputs_purchased': number_outputs_purchased, 'charity': charity,
        'intervention': intervention,
        'number_outputs_purchased_lower_bound': number_outputs_purchased_lower_bound,
        'number_outputs_purchased_upper_bound': number_outputs_purchased_upper_bound,
        'source_name': source_name, 'source_url': source_url, 'comment': comment}
    if type(grant) == MaxImpactFundGrant:
        return Allotment.objects.create(max_impact_fund_grant=grant,
                                        **params)
    elif type(grant) == AllGrantsFundGrant:
        return Allotment.objects.create(all_grants_fund_grant=grant, **params)

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
            cents_per_output() returns the correct value
        """
        allotment = Allotment(sum_in_cents=5, number_outputs_purchased=3)
        self.assertEqual(allotment.cents_per_output(), 1.6666666666666667)

    def test_validates_lower_bound_is_less_than_primary_estimate(self):
        allotment = create_allotment(create_grant())
        allotment.number_outputs_purchased=100
        allotment.number_outputs_purchased_lower_bound = 200
        try:
            allotment.clean()
        except ValidationError as e:
            self.assertIn('number_outputs_purchased_lower_bound must be less than number_outputs_purchased.',
                          e.message_dict['number_outputs_purchased_lower_bound'])

    def test_validates_upper_bound_is_greater_than_primary_estimate(self):
        allotment = create_allotment(create_grant())
        allotment.number_outputs_purchased=100
        allotment.number_outputs_purchased_upper_bound = 0
        try:
            allotment.clean()
        except ValidationError as e:
            self.assertIn('number_outputs_purchased_upper_bound must be greater than number_outputs_purchased.',
                          e.message_dict['number_outputs_purchased_upper_bound'])

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

    def test_validates_lower_bound_is_less_than_primary_estimate(self):
        evaluation = create_evaluation()
        evaluation.cents_per_output=100
        evaluation.cents_per_output_lower_bound = 200
        try:
            evaluation.clean()
        except ValidationError as e:
            self.assertIn('Cents per output lower bound must be less than cents per output.',
                          e.message_dict['cents_per_output_lower_bound'])

    def test_validates_upper_bound_is_greater_than_primary_estimate(self):
        evaluation = create_evaluation()
        evaluation.cents_per_output=100
        evaluation.cents_per_output_upper_bound = 0
        try:
            evaluation.clean()
        except ValidationError as e:
            self.assertIn('Cents per output upper bound must be greater than cents per output.',
                          e.message_dict['cents_per_output_upper_bound'])

class AllotmentAdminTests(TestCase):
    def test_rounding_cents_per_output(self):
        allotment = create_allotment(create_grant(), sum_in_cents=15, number_outputs_purchased=4)
        allotment_admin = AllotmentAdmin(model=Allotment, admin_site=AdminSite())
        self.assertEqual(allotment_admin.rounded_cents_per_output(allotment=allotment), 4)

class EvaluationAdminTests(TestCase):
    def test_custom_admin_display_methods(self):
        '''Check whether pseudo-fields on Evaluation are functioning'''
        charity = Charity(abbreviation='JAEG', charity_name='Against Vensusia Foundation')
        intervention = Intervention(
            short_description='Giant mechs',
            long_description='Preemptive defensive planning against giant Venusian monsters')
        evaluation = Evaluation(charity=charity, intervention=intervention)
        evaluation_admin = EvaluationAdmin(model=Evaluation, admin_site=AdminSite())
        self.assertEqual(evaluation_admin.charity(evaluation=evaluation),
                         'Against Vensusia Foundation')
        self.assertEqual(evaluation_admin.intervention(evaluation=evaluation), 'Giant mechs')

class MiddlewareIntegrationTests(TestCase):
    def test_unsupported_currency_and_language_code_errors(self):
        query_1 = reverse('evaluations') + '?language=ZZ'
        content = json.loads(self.client.get(query_1).content)
        self.assertEqual(len(content['errors']), 1)
        self.assertEqual(content['errors'][0], 'Language code zz not supported')

        query_2 = reverse('evaluations') + '?currency=zzz&language=ZZ'
        content_2 = json.loads(self.client.get(query_2).content)
        self.assertEqual(len(content_2['errors']), 2)
        self.assertEqual(content_2['errors'][0], 'Currency ZZZ not supported')
        self.assertEqual(content_2['errors'][1], 'Language code zz not supported')

@freeze_time("2022-08-23")
class EvaluationViewTests(TestCase):
    def setUp(self):
        if self._testMethodName != 'test_evaluation_not_found':
            self.charity = create_charity()
            self.intervention = create_intervention()
            self.eval_1 = create_evaluation(charity=self.charity, intervention=self.intervention)

    def test_evaluation_not_found_by_start_date(self):
        query = reverse('evaluations') + '?start_year=2016'
        content = json.loads(self.client.get(query).content)
        self.assertEqual(
            content['warnings'][0], 'No evaluations found with those parameters')

    def test_evaluation_not_found_by_donation_date(self):
        query = reverse('evaluations') + '?donation_year=2010'
        content = json.loads(self.client.get(query).content)
        self.assertEqual(
            content['warnings'][0], 'No evaluations found with those parameters')

    def test_one_evaluation(self):
        '''Check output from a single evaluation'''
        response = self.client.get(reverse('evaluations'))
        content = json.loads(response.content)
        self.assertNotIn('warnings', content)
        self.assertEqual(content['evaluations'],
            [{'id': 1,
              'start_month': 12,
              'start_year': 2010,
              'cents_per_output': 100,
              'cents_per_output_upper_bound': 9**9,
              'cents_per_output_lower_bound': 1,
              'converted_cost_per_output': 1.0,
              'source_name': 'Political Tesseract',
              'source_url': 'https://www.youtube.com/watch?v=tSEOXRLSpVc',
              'comment': 'Killer robots will also generate many jobs',
              'exchange_rate_date': '2010-12-01',
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

    def test_specifying_conversion_date(self):
        query = '?conversion_year=2011&conversion_month=12&conversion_day=25&currency=gbp'
        response = self.client.get(reverse('evaluations') + query)
        evaluation = json.loads(response.content)['evaluations'][0]
        self.assertEqual(evaluation['exchange_rate_date'], '2011-12-25')
        self.assertEqual(evaluation['converted_cost_per_output'], 0.6379085968001225)

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
        self.assertEqual(content_2['evaluations'][0]['currency'], 'NOK')

    def test_specified_language(self):
        '''Ensure queries specifying language get the correct language'''
        query = reverse('evaluations') + '?language=no'
        content = json.loads(self.client.get(query).content)
        self.assertEqual(content['evaluations'][0]['intervention']['short_description'],
                         'Døstrøbøtøng køllør røbøts')
        self.assertEqual(content['evaluations'][0]['intervention']['long_description'],
                         'Rødøcøng thø røsk frøm møsøløgnød nøtørøl øntølløgønce')

    def test_specified_currency_on_evaluation_date(self):
        '''Ensure queries specifying currency get the correct currency'''
        original_cost_in_cents = Evaluation.objects.all()[0].cents_per_output
        expected_conversion = CurrencyConverter().convert(
            original_cost_in_cents / 100, 'USD', 'EUR', date(2010, 12, 1))
        query = reverse('evaluations') + '?currency=EUR'
        content = json.loads(self.client.get(query).content)
        evaluation = content['evaluations'][0]
        self.assertEqual(evaluation['currency'], 'EUR')
        self.assertEqual(evaluation['converted_cost_per_output'], expected_conversion)

    def test_fetching_evaluation_by_donation_date(self):
        eval_2 = create_evaluation(
            charity=self.charity, intervention=self.intervention, start_year=2011, start_month=1)
        query_1 = reverse('evaluations') + '?currency=EUR&donation_year=2011&donation_month=2'
        query_2 = reverse('evaluations') + '?currency=EUR&donation_year=2011&donation_month=1'\
            '&conversion_year=2010&conversion_month=11&conversion_day=29'
        query_3 = reverse('evaluations') + '?currency=EUR&donation_year=2010&donation_month=12'

        result_1 = json.loads(self.client.get(query_1).content)['evaluations'][0]
        result_2 = json.loads(self.client.get(query_2).content)['evaluations'][0]
        result_3 = json.loads(self.client.get(query_3).content)['evaluations'][0]

        self.assertEqual(result_1['id'], eval_2.id)
        self.assertEqual(result_2['id'], eval_2.id)
        self.assertEqual(result_3['id'], self.eval_1.id)

        self.assertEqual(result_1['exchange_rate_date'], '2011-02-01')
        self.assertEqual(result_2['exchange_rate_date'], '2010-11-29')
        self.assertEqual(result_3['exchange_rate_date'], '2010-12-01')

        self.assertEqual(result_1['converted_cost_per_output'], 0.7270083605961469)
        self.assertEqual(result_2['converted_cost_per_output'], 0.7606876616461281)
        self.assertEqual(result_3['converted_cost_per_output'], 0.7624857033930613)

@freeze_time("2022-08-23")
class MaxImpactFundGrantIndexViewTests(TestCase):
    def setUp(self):
        if self._testMethodName != 'test_grant_not_found':
            self.grant_1 = create_grant(type='max_impact_fund_grant')
            self.allotment_1 = create_allotment(
                grant=self.grant_1)

    def test_grant_not_found_by_start_date(self):
        query = reverse('max_impact_fund_grants') + '?start_year=2016'
        content = json.loads(self.client.get(query).content)
        self.assertEqual(
            content['warnings'][0], 'No max_impact_fund_grants found with those parameters')

    def test_grant_not_found_by_donation_date(self):
        query = reverse('max_impact_fund_grants') + '?donation_year=2010'
        content = json.loads(self.client.get(query).content)
        self.assertEqual(
            content['warnings'][0], 'No max_impact_fund_grants found with those parameters')

    def test_one_grant(self):
        '''Check output from a single grant'''
        response = self.client.get(reverse('max_impact_fund_grants'))
        content = json.loads(response.content)
        self.assertNotIn('warnings', content)
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
                  'exchange_rate_date': '2015-06-01',
                  'number_outputs_purchased': 2222,
                  'number_outputs_purchased_upper_bound': None,
                  'number_outputs_purchased_lower_bound': 0,
                  'comment': 'May benefit from further RCTs',
                  'source_name': 'Hollywood scriptwriters',
                  'source_url': 'https://www.darkhorizons.com/michael-bay-talks-his-biggest-explosion/',
                  'intervention': {
                      'id': 1,
                      'long_description': 'Reducing the risk from misaligned natural intelligence',
                      'short_description': 'Distributing killer robots'},
                  'charity': {
                      'id': 1,
                      'charity_name': 'Skynet',
                      'abbreviation': 'SN'}}]}])

    def test_specifying_conversion_date(self):
        query = '?conversion_year=2017&conversion_month=5&conversion_day=2&currency=eur'
        response = self.client.get(reverse('max_impact_fund_grants') + query)
        allotment = json.loads(response.content)['max_impact_fund_grants'][0]['allotment_set'][0]
        self.assertEqual(allotment['exchange_rate_date'], '2017-05-02')
        self.assertEqual(allotment['converted_cost_per_output'], 0.04122766834631242)
        self.assertEqual(allotment['converted_sum'], 91.60787906550618)

    def test_filtering_by_year(self):
        '''Ensure specifying start_year/end_year in views gets only grants from/before
        that year'''
        grant_2 = create_grant(type='max_impact_fund_grant', start_year=2016)
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
        grant_2 = create_grant(type='max_impact_fund_grant', start_month=1)
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
        self.assertEqual(content_2['max_impact_fund_grants'][0]['allotment_set'][0]['currency'], 'NOK')

    def test_specified_language(self):
        '''Ensure queries specifying language get the correct language'''
        query = reverse('max_impact_fund_grants') + '?language=no'
        content = json.loads(self.client.get(query).content)
        intervention = content['max_impact_fund_grants'][0]['allotment_set'][0]['intervention']
        self.assertEqual(intervention['short_description'],
                         'Døstrøbøtøng køllør røbøts')
        self.assertEqual(intervention['long_description'],
                         'Rødøcøng thø røsk frøm møsøløgnød nøtørøl øntølløgønce')

    def test_specified_currency_on_grant_date(self):
        '''Ensure queries specifying currency get the correct currency'''
        original_sum_in_cents = Allotment.objects.all()[0].sum_in_cents
        expected_conversion = CurrencyConverter().convert(
            original_sum_in_cents / 100, 'USD', 'EUR', date(2015, 6, 1))
        query = reverse('max_impact_fund_grants') + '?currency=EUR'
        content = json.loads(self.client.get(query).content)
        allotment = content['max_impact_fund_grants'][0]['allotment_set'][0]
        self.assertEqual(allotment['currency'], 'EUR')
        self.assertEqual(allotment['converted_sum'], expected_conversion)

    def test_fetching_grant_by_donation_date(self):
        grant_2 = create_grant(type='max_impact_fund_grant', start_year=2016, start_month=1)
        grant_3 = create_grant(type='max_impact_fund_grant', start_year=2016, start_month=2)

        allotment_2 = create_allotment(
            grant=grant_2, intervention=Intervention.objects.first())
        allotment_3 = create_allotment(
            grant=grant_3, intervention=Intervention.objects.first())

        query_1 = reverse('max_impact_fund_grants') + '?currency=EUR&donation_year=2016&'\
            'donation_month=1&conversion_year=2015&conversion_month=7&conversion_day=30'
        query_2 = reverse('max_impact_fund_grants') + '?currency=EUR&donation_year=2016&donation_month=2'
        query_3 = reverse('max_impact_fund_grants') + '?currency=EUR&donation_year=2015&donation_month=12'

        result_1 = json.loads(self.client.get(query_1).content)['max_impact_fund_grants'][0]
        result_2 = json.loads(self.client.get(query_2).content)['max_impact_fund_grants'][0]
        result_3 = json.loads(self.client.get(query_3).content)['max_impact_fund_grants'][0]

        self.assertEqual(result_1['id'], grant_2.id)
        self.assertEqual(result_2['id'], grant_3.id)
        self.assertEqual(result_3['id'], self.grant_1.id)

        self.assertEqual(result_1['allotment_set'][0]['exchange_rate_date'], '2015-07-30')
        self.assertEqual(result_2['allotment_set'][0]['exchange_rate_date'], '2016-02-01')
        self.assertEqual(result_3['allotment_set'][0]['exchange_rate_date'], '2015-12-01')

        self.assertEqual(result_1['allotment_set'][0]['converted_cost_per_output'], 0.04107713372889092)
        self.assertEqual(result_2['allotment_set'][0]['converted_cost_per_output'], 0.041345093715545754)
        self.assertEqual(result_3['allotment_set'][0]['converted_cost_per_output'], 0.04245283018867924)

class MaxImpactFundGrantModelTests(TestCase):
    def test_string_representation(self):
        grant = MaxImpactFundGrant(start_year=2015, start_month=6)
        self.assertEqual(str(grant), 'Max Impact Fund Grant 2015-6')

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

# The test below intentionally pretty much duplicate the above two classes, replacing MaxImpactFundGrants
# with AllGrantsFundGrants. If we end up with more than two grant types, we should consider
# refactoring both these tests and the classes.
@freeze_time("2022-08-23")
class AllGrantsFundGrantIndexViewTests(TestCase):
    def setUp(self):
        if self._testMethodName != 'test_grant_not_found':
            self.grant_1 = create_grant('all_grants_fund_grant')
            self.allotment_1 = create_allotment(
                grant=self.grant_1)

    def test_grant_not_found_by_start_date(self):
        query = reverse('all_grants_fund_grants') + '?start_year=2016'
        content = json.loads(self.client.get(query).content)
        self.assertEqual(
            content['warnings'][0], 'No all_grants_fund_grants found with those parameters')

    def test_grant_not_found_by_donation_date(self):
        query = reverse('all_grants_fund_grants') + '?donation_year=2010'
        content = json.loads(self.client.get(query).content)
        self.assertEqual(
            content['warnings'][0], 'No all_grants_fund_grants found with those parameters')

    def test_one_grant(self):
        '''Check output from a single grant'''
        response = self.client.get(reverse('all_grants_fund_grants'))
        content = json.loads(response.content)
        self.assertNotIn('warnings', content)
        self.assertEqual(content['all_grants_fund_grants'],
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
                  'exchange_rate_date': '2015-06-01',
                  'number_outputs_purchased': 2222,
                  'number_outputs_purchased_upper_bound': None,
                  'number_outputs_purchased_lower_bound': 0,
                  'comment': 'May benefit from further RCTs',
                  'source_name': 'Hollywood scriptwriters',
                  'source_url': 'https://www.darkhorizons.com/michael-bay-talks-his-biggest-explosion/',
                  'intervention': {
                      'id': 1,
                      'long_description': 'Reducing the risk from misaligned natural intelligence',
                      'short_description': 'Distributing killer robots'},
                  'charity': {
                      'id': 1,
                      'charity_name': 'Skynet',
                      'abbreviation': 'SN'}}]}])

    def test_specifying_conversion_date(self):
        query = '?conversion_year=2017&conversion_month=5&conversion_day=2&currency=eur'
        response = self.client.get(reverse('all_grants_fund_grants') + query)
        allotment = json.loads(response.content)['all_grants_fund_grants'][0]['allotment_set'][0]
        self.assertEqual(allotment['exchange_rate_date'], '2017-05-02')
        self.assertEqual(allotment['converted_cost_per_output'], 0.04122766834631242)
        self.assertEqual(allotment['converted_sum'], 91.60787906550618)

    def test_filtering_by_year(self):
        '''Ensure specifying start_year/end_year in views gets only grants from/before
        that year'''
        grant_2 = create_grant(type='all_grants_fund_grant', start_year=2016)
        query_1 = reverse('all_grants_fund_grants') + '?start_year=2016'
        content_1 = json.loads(self.client.get(query_1).content)
        query_2 = reverse('all_grants_fund_grants') + '?end_year=2015'
        content_2 = json.loads(self.client.get(query_2).content)
        query_3 = reverse('all_grants_fund_grants')
        content_3 = json.loads(self.client.get(query_3).content)
        self.assertEqual(len(content_1['all_grants_fund_grants']), 1)
        self.assertEqual(len(content_2['all_grants_fund_grants']), 1)
        self.assertEqual(len(content_3['all_grants_fund_grants']), 2)
        self.assertEqual(
            content_1['all_grants_fund_grants'][0]['start_year'], 2016)
        self.assertEqual(
            content_2['all_grants_fund_grants'][0]['start_year'], 2015)

    def test_filtering_within_year(self):
        '''Ensure specifying start_month/end_month in views gets only grants from/before
        that month'''
        grant_2 = create_grant(type='all_grants_fund_grant', start_month=1)
        query_1 = reverse('all_grants_fund_grants') + '?start_month=5'
        content_1 = json.loads(self.client.get(query_1).content)
        query_2 = reverse('all_grants_fund_grants') + '?end_month=5'
        content_2 = json.loads(self.client.get(query_2).content)
        self.assertEqual(len(content_1['all_grants_fund_grants']), 1)
        self.assertEqual(len(content_2['all_grants_fund_grants']), 1)
        self.assertEqual(
            content_1['all_grants_fund_grants'][0]['start_month'], 6)
        self.assertEqual(
            content_2['all_grants_fund_grants'][0]['start_month'], 1)

    def test_currency_defaults(self):
        '''Ensure query with language and no currency defaults correctly'''
        query_1 = reverse('all_grants_fund_grants')
        content_1 = json.loads(self.client.get(query_1).content)
        query_2 = reverse('all_grants_fund_grants') + '?language=no'
        content_2 = json.loads(self.client.get(query_2).content)
        self.assertEqual(content_1['all_grants_fund_grants'][0]['allotment_set'][0]['currency'], 'USD')
        self.assertEqual(content_2['all_grants_fund_grants'][0]['allotment_set'][0]['currency'], 'NOK')

    def test_specified_language(self):
        '''Ensure queries specifying language get the correct language'''
        query = reverse('all_grants_fund_grants') + '?language=no'
        content = json.loads(self.client.get(query).content)
        intervention = content['all_grants_fund_grants'][0]['allotment_set'][0]['intervention']
        self.assertEqual(intervention['short_description'],
                         'Døstrøbøtøng køllør røbøts')
        self.assertEqual(intervention['long_description'],
                         'Rødøcøng thø røsk frøm møsøløgnød nøtørøl øntølløgønce')

    def test_specified_currency_on_grant_date(self):
        '''Ensure queries specifying currency get the correct currency'''
        original_sum_in_cents = Allotment.objects.all()[0].sum_in_cents
        expected_conversion = CurrencyConverter().convert(
            original_sum_in_cents / 100, 'USD', 'EUR', date(2015, 6, 1))
        query = reverse('all_grants_fund_grants') + '?currency=EUR'
        content = json.loads(self.client.get(query).content)
        allotment = content['all_grants_fund_grants'][0]['allotment_set'][0]
        self.assertEqual(allotment['currency'], 'EUR')
        self.assertEqual(allotment['converted_sum'], expected_conversion)

    def test_fetching_grant_by_donation_date(self):
        grant_2 = create_grant(type='all_grants_fund_grant', start_year=2016, start_month=1)
        grant_3 = create_grant(type='all_grants_fund_grant', start_year=2016, start_month=2)

        allotment_2 = create_allotment(
            grant=grant_2, intervention=Intervention.objects.first())
        allotment_3 = create_allotment(
            grant=grant_3, intervention=Intervention.objects.first())

        query_1 = reverse('all_grants_fund_grants') + '?currency=EUR&donation_year=2016&'\
            'donation_month=1&conversion_year=2015&conversion_month=7&conversion_day=30'
        query_2 = reverse('all_grants_fund_grants') + '?currency=EUR&donation_year=2016&donation_month=2'
        query_3 = reverse('all_grants_fund_grants') + '?currency=EUR&donation_year=2015&donation_month=12'

        result_1 = json.loads(self.client.get(query_1).content)['all_grants_fund_grants'][0]
        result_2 = json.loads(self.client.get(query_2).content)['all_grants_fund_grants'][0]
        result_3 = json.loads(self.client.get(query_3).content)['all_grants_fund_grants'][0]

        self.assertEqual(result_1['id'], grant_2.id)
        self.assertEqual(result_2['id'], grant_3.id)
        self.assertEqual(result_3['id'], self.grant_1.id)

        self.assertEqual(result_1['allotment_set'][0]['exchange_rate_date'], '2015-07-30')
        self.assertEqual(result_2['allotment_set'][0]['exchange_rate_date'], '2016-02-01')
        self.assertEqual(result_3['allotment_set'][0]['exchange_rate_date'], '2015-12-01')

        self.assertEqual(result_1['allotment_set'][0]['converted_cost_per_output'], 0.04107713372889092)
        self.assertEqual(result_2['allotment_set'][0]['converted_cost_per_output'], 0.041345093715545754)
        self.assertEqual(result_3['allotment_set'][0]['converted_cost_per_output'], 0.04245283018867924)

class AllGrantsFundGrantModelTests(TestCase):
    def test_string_representation(self):
        grant = AllGrantsFundGrant(start_year=2015, start_month=6)
        self.assertEqual(str(grant), 'All Grants Fund Grant 2015-6')

    def test_validates_current_year_in_range(self):
        '''Ensure current_year is between 2000 and now'''
        grant = AllGrantsFundGrant(start_year=1999)
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
        grant = AllGrantsFundGrant(start_month=0)
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
