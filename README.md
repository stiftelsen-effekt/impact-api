# GiveWell Impact API

<h2>Instructions</h2>
<p>API consumers have two main types of request: 'Evaluations' and 'Max Impact Fund Grants'.</p>
<p>Evaluations represent a Givewell assessment of the cost of a single intervention type for a single charity in one specific date range, e.g. AMF, $10 per malaria net in 2018. Grants represent the collective allocations of the Givewell Maximum Impact Fund for a specific quarter and their assessment of what the money bought, e.g. one grant for ($10000 to AMF buying 1100 bednets, and $30000 to SCI for 200 deworming treatments)</p>
<h3>Evaluations</h3>
<p>To get evaluations, send a GET request to impact.gieffektivt.no/evaluations, including any of the optional query strings to filter within time periods or by charities: start_year=&lt;integer&gt;, start_month=&lt;integer&gt;, end_year=&lt;integer&gt; end_month=&lt;integer&gt;, charity_abbreviation=&lt;string&gt;</p>
<p>Multiple charities can be requested, and all evaluations within the time specified for those charities will be returned. Absent queries default to the maximally inclusive value. Charity abbreviations are not case sensitive.</p>
<h3>Grants</h3>
<p>To get grants, send a GET request to impact.gieffektivt.no/evaluations, including any of the optional query strings to filter within time periods: start_year=&lt;integer&gt;, start_month=&lt;integer&gt;, end_year=&lt;integer&gt; end_month=&lt;integer&gt;</p></p>
<h3>Admin section</h3>
<p>From here you can add, update and delete evaluations and grants and set permissions on other users to do some subset of these.</p>

[Project kanban](https://github.com/orgs/stiftelsen-effekt/projects/10)
[Project Drive folder](https://drive.google.com/drive/folders/1oq7mnB1tIN5beIFmf3iFKg01w46jSfiw?usp=sharing)
