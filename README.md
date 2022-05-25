# GiveWell Impact API

  <div><h2>Instructions</h2>
    <p>API consumers have two main types of request: 'Evaluations' and 'Max Impact Fund Grants'.</p>
    <p>Evaluations represent a Givewell assessment of the cost of a single intervention type for a single charity in one specific date range, e.g. AMF, $10 per malaria net in 2018. Grants represent the collective allocations of the Givewell Maximum Impact Fund for a specific quarter and their assessment of what the money bought, e.g. one grant for ($10000 to AMF buying 1100 bednets, and $30000 to SCI for 200 deworming treatments).</p>
    <h3>Evaluations</h3>
    <p>To get evaluations, send a GET request to impact.gieffektivt.no/evaluations, including any of the optional query strings to filter within time periods or by charities: start_year=&lt;integer&gt;, start_month=&lt;integer&gt;, end_year=&lt;integer&gt; end_month=&lt;integer&gt;, charity_abbreviation=&lt;string&gt;, language=&lt;i18n country code, defaulting to 'en'&gt;, currency=&lt;ISO 4217 code, defaulting to USD and otherwise converted from USD using previous-day conversion rate&gt;. </p>
    <p>Multiple charities can be requested, and all evaluations within the time specified for those charities will be returned. Absent queries default to the maximally inclusive value. Charity abbreviations are not case sensitive.</p>
    <p>The JSON response object will contain either (a list of `errors`) or (a list of `evaluations` and optionally a list of `warnings`). Currently the only warning is that the `evaluations` list is empty, given the filter parameters entered.</p>
    <h3>Grants</h3>
    <p>To get grants, send a GET request to impact.gieffektivt.no/evaluations, including any of the optional query strings to filter within time periods: start_year=&lt;integer&gt;, start_month=&lt;integer&gt;, end_year=&lt;integer&gt; end_month=&lt;integer&gt;, language=&lt;i18n country code, defaulting to 'en'&gt;, currency=&lt;ISO 4217 code, defaulting to USD and otherwise converted from USD using previous-day conversion rate&gt;. </p>
    <p>The JSON response object will contain either (a list of `errors`) or (a list of `max_impact_fund_grants` and optionally a list of `warnings`). Currently the only warning is that the `max_impact_fund_grants` list is empty, given the filter parameters entered.</p>
    <h3>Language and currency</h3>
    <p>For any query, if language is given but no currency, currency will default to the natural currency for that language (eg NOK for Norway, USD for English). Language options are currently only English and Norwegian. Currency can be converted to most major denominations. Adding a language has to be done codeside with the following steps:</p>
    <ul>
        <li>In impact_api/settings.py, add the language details to the `LANGUAGES` tuple</li>
        <li>In impact_api/api/serializers.py, add the language and its default currency to the `DEFAULT_LANGUAGE_CURRENCY_MAPPING` dictionary</li>
        <li>From the command line, run `python manage.py makemigrations`</li>
        <li>Check the migration has been created with your desired language. Then from the command line, run `python manage.py migrate`</li>
        <li>Once the database in question is up to date, make sure to populate all the existing 'Intervention' fields to ensure that someone requesting the new language gets text</li>
    </ul>
    <p>To view supported currencies, open the relevant Django shell (`python manage.py shell`), then</p>
    <ul>
        <li>`from currency_converter import CurrencyConverter`</li>
        <li>`c = CurrencyConverter()`</li>
        <li>`c.currencies`</li>
    </ul>
    <p>The current list is 'AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CYP', 'CZK', 'DKK', 'EEK', 'EUR', 'GBP', 'HKD', 'HRK', 'HUF', 'IDR', 'ILS', 'INR', 'ISK', 'JPY', 'KRW', 'LTL', 'LVL', 'MTL', 'MXN', 'MYR', 'NOK', 'NZD', 'PHP', 'PLN', 'ROL', 'RON', 'RUB', 'SEK', 'SGD', 'SIT', 'SKK', 'THB', 'TRL', 'TRY', 'USD', 'ZAR'.</p>
    <h3>Admin section</h3>
    <p>To access to the admin section, first create an admin user: from the relevant command line, run `python manage.py createsuperuser` and follow the prompts. Then you can access the admin section by visiting impact.gieffektivt.no/admin, and log in with the details you provided. From there you can create, edit and delete evaluations and grants (and associated models), as well as add other admin users.</p>
  </div>

[Project kanban](https://github.com/orgs/stiftelsen-effekt/projects/10)
[Project Drive folder](https://drive.google.com/drive/folders/1oq7mnB1tIN5beIFmf3iFKg01w46jSfiw?usp=sharing)
