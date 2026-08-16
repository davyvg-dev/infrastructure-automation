# Glitch call 2026-08-04 21:40 — glm-45-air-fp8 garbage output

conversation_id: `conv_1001kz74naebey1vcx2fbcwc2vv6`  
caller: +31615851987 -> +3197006530002 | 107s | ended: Call ended by remote party  
verdict: failure | LLM: glm-45-air-fp8 (temp 0.4)

First live test call after the address idiot-proofing patch. What worked:
CLI passthrough (real 06 in system\_\_caller_id), spelling-alphabet
normalization ("Tinis Anton" -> 3035TA), postcode/huisnummer mismatch
caught and queried back. What broke: after the 4th lookup_address call
the LLM emitted pure garbage tokens (below, verbatim). Tool responses
were each ~4KB of raw BAG fields — since shrunk to one weergavenaam
per hit via fl=weergavenaam (commit 4187198). If garbage recurs on the
retest, switch the agent LLM — one config field.

## Summary (ElevenLabs)

De gebruiker meldde buitengesloten te zijn doordat de deur was dichtgevallen, niet op nachtslot. De agent probeerde herhaaldelijk het adres van de gebruiker te achterhalen voor assistentie. Meerdere pogingen om het adres te bevestigen, eerst in Dordrecht en later in Almere, waren onsuccesvol door onduidelijke of incorrecte straatnamen van de gebruiker. Het gesprek werd abrupt beëindigd toen de gebruiker een telefoontje ontving.

## Collected

- caller_name: None
- phone: None
- address: None
- job_type: buitensluiting
- is_emergency: True

## Transcript

**agent**: Hallo, u spreekt met Sam, de AI-assistent van Slotenmaker DRS. Waarmee...

**user**: Dank je wel.

**agent**: Graag gedaan. Wat is er aan de hand? Bent u buitengesloten of is er iets anders met uw slot?

**user**: Ik ben buitengesloten.

**agent**: Dat is vervelend. Zit de deur op het nachtslot, of is hij alleen dichtgevallen met de sleutel nog binnen?

**user**: Hij is dichtgevallen.

**agent**: Dat is...

**user**: U merkt het hier op uw beurt.

**agent**: Dat is goed nieuws. Dan zit de deur waarschijnlijk niet op slot en kan de slotenmaker hem vaak zonder schade openen.

Wat is uw postcode en huisnummer?

**user**: 3000, Dordrecht, Kieners Anton, 298.

> tool: lookup_address({"q": "Kieners Anton 298 Dordrecht"})
> **agent**: Ik heb een paar mogelijke adressen gevonden in Dordrecht met huisnummer 298. Kunt u mij de juiste...

**user**: Nederstokkum.

> tool: lookup_address({"q": "Nederstokkum 298 Dordrecht"})
> **user**: Derks, liefst vijf, en Derks, achttien, S. Anton, het huisnummer 298.

**agent**: Ik hoor het niet helemaal goed. Kunt u de straatnaam nog eens rustig spellen, of weet u misschien de postcode?

**user**: 3035 Tinis Anton, huisnummer 298.

> tool: lookup_address({"q": "3035TA 298"})
> **agent**: Ik vind bij die postcode alleen Bergstraat in Rotterdam, met huisnummers vijf A, B en C. U gaf huisnummer...

**user**: Ik sprak mis.

**agent**: Geen probleem. Kunt u het juiste huisnummer noemen, of misschien de straatnaam en plaats?

**user**: Laan der Feo's 298 in Almere.

> tool: lookup_address({"q": "Laan der Feo's 298 Almere"})
> **agent**: 4
> sp2 22ER:: person 1 people\n People", people1 people people sp person
> 0 sp

2 person::\n
|,4.-people person sp2 peopleERER people#, r
X people)\", people",e sp
. 9
people ", ER\n , r1 ER peopleER people sp 0 sp2
2 people peopleER people
3 people people
and00 3 people people", r) people people-0 \"
people " ER r people::2
people people3 people:::: ( people people::2 peoplePeople (

people " ( people
2 1, people people12 people0 people people person people- \"-people people
, ( people (" sp2
::

::[ peoplePeople::::ER person people

people1",2ER. ( person (people ( \ people people "- (9 0 people people
1 sp1ex--
people
::3
![ people people.():: People " \"::person "::::()::
people people people "
people people2/2 person sp 10ER::29 ( ER1 spER
people（ people11 people0 people people3 people", people
,6 0
\n- people
1
2 - - person ::4|1Person
people: sp1, person people</ people3 sp21
2 " people peoplepeople sp people2- people, (. sp peoplepeople2 sp 9: :: :: people:: people

::
people r| people25 people
R people r2 1 \"os \ r\

people person "-:: people (
l people\n \n0
peoplepeople people # \"
" sp people person People sp1 sppeople "
(:: "1 ::::::::()people people::::\n people3
{:: people people:: - people
9:: sp people1 | 2 ( -::23::2
[7 0-
2 1 sp\n spperson
&2 ( (::::4A People :: ::|::, People:: people -:: people
| sp people
.( person5:: people sp 1-people
sp ',"
r3a2:: people::
people::

\n people people
people \ \-- sp people

--0ER- "

person:: people people
people sp- People
2...

**user**: Ik ben net gebeld.
