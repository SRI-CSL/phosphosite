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


```
http://www.phosphosite.org/proteinAction.action?id=570&showAllSites=true

```

OK so problem (gotcha number 1) is that the desired stuff in the second page result is an ajax call.
And isn't in the second page itself.

```
  <script type="text/javascript">
   $(document).ready(function () {
        //call to get Modification Sites & proteinOrganisms Data
        $("#siteDomainWaitDiv").show();
        var serviceUrl = "proteinModificationSitesDomainsAction.action?id=" + 570 + "&showAllSites=" + true;

        $("#proteinModificationSitesDetails").load(serviceUrl, function(responseTxt, statusTxt, xhr){
            if(statusTxt == "success")
                $("#siteDomainWaitDiv").hide();
            if(statusTxt == "error")
                $("#proteinModificationSitesDetails").html("Unexpected error ");
        });
    });
  </script>
```

```
http://www.phosphosite.org/proteinModificationSitesDomainsAction.action?id=570&showAllSites=true
```


The third page starts with a call to
```
http://www.phosphosite.org/siteAction.action?id=2886
```
