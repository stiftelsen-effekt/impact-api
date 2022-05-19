# GiveWell Impact API

<div><h2>Instructions</h2>
  <p>API consumers have two main types of request: 'Evaluations' and 'Max Impact Fund Grants'.</p>
  <p>Evaluations represent a Givewell assessment of the cost of a single intervention type for a single charity in one specific date range, e.g. AMF, $10 per malaria net in 2018. Grants represent the collective allocations of the Givewell Maximum Impact Fund for a specific quarter and their assessment of what the money bought, e.g. one grant for ($10000 to AMF buying 1100 bednets, and $30000 to SCI for 200 deworming treatments).</p>
  <h3>Evaluations</h3>
  <p>To get evaluations, send a GET request to impact.gieffektivt.no/evaluations, including any of the optional query strings to filter within time periods or by charities: start_year=&lt;integer&gt;, start_month=&lt;integer&gt;, end_year=&lt;integer&gt; end_month=&lt;integer&gt;, charity_abbreviation=&lt;string&gt;, language=&lt;i18n country code&gt;, currency=&lt;ISO 4217 code&gt;.  </p>
  <p>Multiple charities can be requested, and all evaluations within the time specified for those charities will be returned. Absent queries default to the maximally inclusive value. Charity abbreviations are not case sensitive.</p>
  <h3>Grants</h3>
  <p>To get grants, send a GET request to impact.gieffektivt.no/evaluations, including any of the optional query strings to filter within time periods: start_year=&lt;integer&gt;, start_month=&lt;integer&gt;, end_year=&lt;integer&gt; end_month=&lt;integer&gt;, language=&lt;i18n country code&gt;, currency=&lt;ISO 4217 code&gt;. </p>
  <p>For any query, if language is given but no currency, currency will default to the natural currency for that language (eg Euros for Norway, USD for English). Language options are currently only English and Norwegian. Currency can be converted to most major denominations.</p>
  <p>To access to the admin section, first create an admin user: from the relevant command line, run `python manage.py createsuperuser` and follow the prompts. Then you can access the admin section by visiting impact.gieffektivt.no/admin, and log in with the details you provided. From there you can create, edit and delete evaluations and grants (and associated models), as well as add other admin users.</p>
</div>

[Project kanban](https://github.com/orgs/stiftelsen-effekt/projects/10)
[Project Drive folder](https://drive.google.com/drive/folders/1oq7mnB1tIN5beIFmf3iFKg01w46jSfiw?usp=sharing)
