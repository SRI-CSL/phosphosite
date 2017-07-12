# phophosite
Stuff for Merrill (p.s. the repo should be called **phosphosite**)


```
http://www.phosphosite.org/simpleSearchSubmitAction.action?queryId=-1&from=0&searchStr=jun
```

In the second `tbody`.  In a `TD` with class `link13HoverRed` with text `human`:
```
/../proteinAction.action?id=943&showAllSites=true
```

then following that url. In the `div` with id `proteinModificationSitesDetails`

we want to scrape all the hrefs in elements like
```
<td colspan="3">
apoptosis, altered:
<a href="/../siteAction.action?id=2666">S63‑p</a>
,
<a href="/../siteAction.action?id=1988200">T95‑p</a>
</td>
```
where the text ranges over categories like
```
apoptosis, altered:
apoptosis, induced:
carcinogenesis, altered:
cell growth, altered:
cell motility, induced:
cell motility, inhibited:
transcription, altered:
transcription, induced:
transcription, inhibited:
activity, induced:
activity, inhibited:
molecular association, regulation:
phosphorylation:
protein stabilization:
ubiquitination:
```
